import json
from copy import deepcopy
from utils import unpack_optional_items, hierarc_cfg_diff


def complaince_check(config, template):

    """
    """
    result = []
    total_errors = 0
    
    # preserve template, as it may gets modified.
    template_ = deepcopy(template)
        
    # Compare general configuration items of template and configuration ########
    # Initialize audit list which will be finally compared with template
    glb_cfg_audit = [i for i in config['global_cfg']] # Deep copy

    # Remove items from audit list which must be ignored
    for line in config['global_cfg']:
        for item in template_['glb_beg_ign']:
            if line.startswith(item):
                glb_cfg_audit.remove(line) 
        for item in template_['glb_sub_ign']:
            if set(item.split()).issubset(line.split()):
                glb_cfg_audit.remove(line)

    hostname = config['hostname']
    fmt = '################ Compliancy report for hostname {}'
    result.append(fmt.format(hostname))
    
    # Report missing "beginning with" items
    result.append('## Missing general template beginning with items: ########')
    for item in template_['glb_beg_with']:
        found_item = False
        for line in glb_cfg_audit:
           if line.startswith(item):
                glb_cfg_audit.remove(line)
                found_item = True
        if not found_item:
            total_errors += 1
            result.append(item)

    # Calculate differences between config and template
    non_compl_items = set(glb_cfg_audit) - set(template_['glb_cfg'])

    # Calculate if non compliant global items intersects with optional grouped
    # items. If so, add items to template.
    if template_['grp_opt']:
        for key, grouped_config_part in template_['grp_opt'].items():
            glb_cfg, hier_cfg = unpack_optional_items(grouped_config_part)
            if set(glb_cfg) & set(non_compl_items):
                for line in glb_cfg:
                    template_['glb_cfg'].append(line)
                if hier_cfg:
                    for cfg in hier_cfg:
                        template_['glb_hier'].append(cfg)
 
    # Recalculate differences between config and template
    non_compl_items = set(glb_cfg_audit) - set(template_['glb_cfg'])

    result.append('################ Missing general template items: #########')
    for item in template_['glb_cfg']:
        if item not in glb_cfg_audit:
            total_errors += 1
            result.append(item)
    result.append('################ Non compliant General items: ############')
    for item in sorted(non_compl_items):
        total_errors += 1
        result.append(item)
        
    # Compare hierarchical configuration items of template and configuration ###
    # Create config audit list and lists of all first lines of template, config
    # and audit lists
    hier_templ_item_names = [cfg[0] for cfg in template_['glb_hier']]
    hier_config_item_names = [cfg[0] for cfg in config['hierarc_cfgs']]
    hier_cfg_audit = [cfg for cfg in config['hierarc_cfgs']
                      if cfg[0] in hier_templ_item_names]
    hier_audit_config_item_names = [cfg[0] for cfg in hier_cfg_audit]

    # Print items not found in audit config but present in template
    result.append('################ Missing hierarchical template items: ####')
    diff = set(hier_templ_item_names) - set(hier_audit_config_item_names)
    for item_name in diff:
        for templ_item in template_['glb_hier']:
            if item_name == templ_item[0]:
                total_errors += 1
                # Remove from template to ease further comparison
                template_['glb_hier'].remove(templ_item)
                for item in templ_item:
                    result.append(item)
                                                
    result.append('################ Non compliant Hierarchical items: #######')

    # Finally compare stripped template with audit config.
    template_['glb_hier'] = sorted(template_['glb_hier'], key=lambda x: x[0])
    hier_cfg_audit = sorted(hier_cfg_audit, key=lambda x: x[0])

    for templ_cfg, cfg in zip(template_['glb_hier'], hier_cfg_audit):
        if not hierarc_cfg_diff(templ_cfg, cfg):
            total_errors += 1
            result.append('## template configuration is:')
            for item in templ_cfg:
                result.append(item)
            result.append('## But configuration found is:')
            for item in cfg:
                result.append(item)
    result.append('##########################################################')
    result.append('##########################################################')
    result.append('#')
    result.append('#')
    result.append('#')

    return result, total_errors
