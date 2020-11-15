import re
import os
import json


class ReSearcher():
    
    """
    Helper  to enable evaluation
    and regex formatting in a single line
    """
    
    match = None

    def __call__(self, pattern, string):
        self.match = re.search(pattern, string)
        return self.match

    def __getattr__(self, name):
        return getattr(self.match, name)


class Tree(dict):
    """ Autovivificious dictionary """
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

    def __str__(self):
        """ Serialize dictionary to JSON formatted string with indents """
        return json.dumps(self, indent=4)


def get_value(key, item):

    """
    key + value = interface item
    function returns value for given key and item
    """

    if key.strip() == item.strip():
        return key
    else:
        item = item.lstrip()
        result = re.search('^('+key+')(.*)', item)
        value = format(result.group(2)).lstrip()
        return value
    

def get_key(item, key_length):

    """
    key + value = item
    number of words of key = key_length
    function returns key
    """

    word = item.strip().split()
    if key_length == 0: # fix
        return item
    elif len(word) == key_length:
        return item
    else:
        return ' '.join(word[0:key_length])


def splitrange(raw_range):

    """
    '1,2,4-6' returns ['1','2','4','5','6']
    'none'    returns ['None']
    """

    m = re.search(r'^(\d+)\-(\d+)$', raw_range)
    if m:
        first = int(format(m.group(1)))
        last = int(format(m.group(2)))
        return [str(i) for i in range(first, last+1)]

    m = re.search(r'[\d+,-]+', raw_range)
    if m:
        result = []
        for raw_element in format(m.group(0)).split(','):
            if '-' in raw_element:
                for element in splitrange(raw_element):
                    result.append(element)
            else:
                result.append(raw_element)
        return result

    m = re.search(r'^none$', raw_range)
    if m:        
        return ['None']
 

def unpack_optional_items(grouped_config_part):

    """
    Helper function to unpack grouped config parts in template_parser
    """

    context = ''
    global_cfg = []
    hierarc_cfg = [] # list of individual hierarchical config part
    hierarc_cfgs = [] # list with all individual hierarchical confg parts

    for previous_line, line in prev_cur_generator(grouped_config_part):
        line = line.rstrip()

        if not line.strip(): # skip empty lines
            continue

        if line.lstrip() == line and context == '':
            if previous_line is None:
                pass
            elif (not previous_line.startswith('!') or previous_line == ''):
                global_cfg.append(previous_line)
            
        elif line.lstrip() != line and context == '':
            hierarc_cfg = []
            hierarc_cfg.append(previous_line)
            context = 'hierarc'

        elif line.lstrip() != line and context == 'hierarc':
            hierarc_cfg.append(previous_line)

        elif line == '!' or line.startswith('') and context == 'hierarc':
            hierarc_cfg.append(previous_line)
            hierarc_cfgs.append(hierarc_cfg)
            context = ''

    return global_cfg, hierarc_cfgs


def hierarc_cfg_diff(templ_cfg, hier_cfg, templ_wildcard_char='<<>>'):

    """
    Function compares hierarchical configuration items and
    takes into account that wildcards can be used in template.
    If template    --> key 7 <<>>
    and config     --> key 7 SDFT123WERfsdf
    Then function considers these two lines identical.    
    """

    if len(templ_cfg) != len(hier_cfg):
        return False

    for line1, line2 in zip(templ_cfg, hier_cfg):
        for word1, word2 in zip(line1.split(), line2.split()):
            if word1 != word2 and word1 == templ_wildcard_char:
                pass
            elif word1 != word2 and word1 != templ_wildcard_char:
                return False
    return True


def prev_cur_generator(iterable):

    """
    Helper function/generator to read lines (iterable) and yield both current
    and previous line.
    """

    previous = None
    iterable = iter(iterable)
    curr = next(iterable)
    try:
        while True:
            yield previous, curr
            previous = curr
            curr = next(iterable)
    except StopIteration:
        pass




