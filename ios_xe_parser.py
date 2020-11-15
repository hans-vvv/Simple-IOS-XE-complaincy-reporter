import re
import json
from utils import ReSearcher, Tree, splitrange, \
     prev_cur_generator, get_key, get_value


class InterfaceParser():

    """
    Helper class to parse interface items. Items which are
    present in list_items are stored in lists.
    With using the _select_key method the following logic is implemented
    to determine which part of an interface item is considered to be a
    key and which part a value.

    1. First portkey_exceptions list is examined. If an interface item
       contains the words found in this list then key = item in the list
       and value = remaining words of the interface item. If an interface
       item is found then the other methods are not considered.
    2. Key_length dict is examined. If interface item contains an item
       found in a list of the dict then corresponding key (i.e. 1 or 2)
       is used to split the item. The key of the item is equal to the
       number of words of the dict key, the rest of the item = value.
       Example: If line = channel-group 2 mode active, then
       key = "channel-group"  and value = "2 mode active". If an interface
       item is found then the last method is not considered.
    3. Default method. Last word of line = value
       and all preceding words = key.
    """

    def __init__(self, list_items, key_exceptions, key_length):
        self.list_items = list_items
        self.key_exceptions = key_exceptions
        self.key_length = key_length

    def initialize_lists(self):
        """ List for each item where value is a list """
        self.values = [[] for item in self.list_items]

    def _get_index(self, line):
        """ Get index by name of lists to store values """
        for index, item in enumerate(self.list_items):
            if line.startswith(item):
                return index

    def _select_key(self, line):
        """ Determine key-value split of items """
        for key in self.key_exceptions:
            if line.startswith(key):
                return key
        for key_length, items in self.key_length.items():
            for item in items:
                if line.startswith(item):
                    return get_key(line, key_length)
        return get_key(line, len(line.split())-1)
            
    def parse_line(self, tree, portindex, line):
        """ Parse line into dict where value is str, list or extended list """
        line = line.lstrip()
        key = self._select_key(line)
        for item in self.list_items:
            if line.startswith(item):
                index = self._get_index(line)
                if line.startswith('switchport trunk allowed vlan'):
                    self.values[index].extend(splitrange(get_value(key, line)))
                    tree['port'][portindex]['vlan_allow_list'] \
                                                         = self.values[index]
                    return tree
                else:
                    self.values[index].append(get_value(key, line))
                    tree['port'][portindex][item] = self.values[index]
                    return tree
        tree['port'][portindex][key] = get_value(key, line)
        return tree


def ios_xe_parser(configfile):

    """
    This function parses banners, interface, vlan, global and hierarchical
    config items into a Python data structure
    """

    with open(configfile, 'r') as lines:
        
        match = ReSearcher()
        tree = Tree()

        key_exceptions = ['ip vrf forwarding']
        key_length = {1: ['hold-queue', 'standby', 'channel-group',
                          'description'],
                      2: ['switchport port-security', 'ip', 'spanning-tree',
                          'speed auto', 'srr-queue bandwidth']
        }
        list_items = ['switchport trunk allowed vlan', 'standby',
                      'ip helper-address', 'logging event']
        intf_parser = InterfaceParser(list_items, key_exceptions, key_length)

        context = ''
        global_cfg = []
        hierarc_cfg = [] # Individual hierarchical config part
        hierarc_cfgs = [] # list with all individual hierarchical config parts
              
        for previous_line, line in prev_cur_generator(lines):
            
            if not line.strip(): # skip empty lines
                continue
            
            line = line.rstrip()
            if previous_line is not None:
                previous_line = previous_line.rstrip()

            if match(r'^hostname (.*)', line):
                hostname = format(match.group(1))
                tree['hostname'] = hostname

            elif match(r'^interface (.*)', line):
                context = 'port'
                portindex = format(match.group(1))
                tree['port'][portindex] = {}
                intf_parser.initialize_lists()
 
            elif match(r'^vlan ([\d,-]+)', line):
                context = 'vlan'
                for vlan in splitrange(format(match.group(1))):
                    tree['vlan'][vlan] = {}

            elif match(r'^banner (\w+) (\S)', line):
                banner_type = format(match.group(1))
                delimeter_char = format(match.group(2))
                tree['banner'][banner_type]['delimeter_char'] = delimeter_char
                tree['banner'][banner_type]['lines'] = []
                context = 'banner'

            elif context == 'port':

                if match(r'^ no (.*)', line):
                    key = format(match.group(1))
                    value = format(match.group(0))
                    tree['port'][portindex][key] = value

                # interface items are stored with helper class
                elif match('^ .*', line):
                    tree = intf_parser.parse_line(tree, portindex, line)

                elif match(r'!$', line):
                    context = ''

            elif context == 'vlan':

                if match(r'^ name (.*)', line):
                    tree['vlan'][vlan]['name'] = format(match.group(1))

                elif match(r'!$', line):
                    context = ''

                elif not line.startswith(' '):
                    global_cfg.append(line)
                    context = ''

            # Both line and previous line are global items                       
            elif line.lstrip() == line and context == '':
                if previous_line is None:
                    pass
                elif not previous_line.startswith('!'):
                    global_cfg.append(previous_line)
    
            # Previous line was beginning of hierarchical item
            elif line.lstrip() != line and context == '':
                hierarc_cfg = []
                hierarc_cfg.append(previous_line)
                context = 'hierarc'

            # Both current and previous line belongs to hierarchical item
            elif line.lstrip() != line and context == 'hierarc':
                hierarc_cfg.append(previous_line)

            # Previous line was last hierarchical item
            elif line == '!' or line.startswith('') and context == 'hierarc':
                hierarc_cfg.append(previous_line)
                hierarc_cfgs.append(hierarc_cfg)
                context = ''

            # Previous line was last hierarchical item and directly followed
            # by start of another hierarchical item
            elif line.lstrip() == line and context == 'hierarc':
                hierarc_cfg.append(previous_line)
                hierarc_cfgs.append(hierarc_cfg)
                hierarc_cfg = []
                          
            elif context == 'banner' and not line.startswith(delimeter_char):
                tree['banner'][banner_type]['lines'].append(line)

            elif context == 'banner' and line.startswith(delimeter_char):
                context = ''

        tree['global_cfg'] = global_cfg
        tree['hierarc_cfgs'] = hierarc_cfgs
        return tree
