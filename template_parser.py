import json
import uuid
from utils import Tree


def template_parser(template_file):

    template = Tree()
            
    with open(template_file, 'r') as lines:
        
        for line in lines:
            
            line = line.rstrip()
            if not line.strip(): # ignore empty lines
                continue

            if line == '# Global config items beginning ignore':
                context = 'glb_beg_ign'
                template[context] = []

            elif line == '# Global config items subset or exact ignore':
                context = 'glb_sub_ign'
                template[context] = []

            elif line == '# Global config items beginning with':
                context = 'glb_beg_with'
                template[context] = []

            elif line == '# Global config items':
                context = 'glb_cfg'
                template[context] = []

            elif line == '# Grouped optional config items':
                key = uuid.uuid4().hex
                context = 'grp_opt'
                template['grp_opt'][key] = []

            elif line == '# Global hierarchical config items':
                context = 'glb_hier'
                hierarc_cfg = []
                template[context] = []

            if '#' in line:
                continue

            if context == 'glb_hier':
                if line == '!':
                    template['glb_hier'].append(hierarc_cfg)
                    hierarc_cfg = []
                else:
                    hierarc_cfg.append(line)
            elif context == 'grp_opt':
                template['grp_opt'][key].append(line)
            else:
                template[context].append(line)

        return template


def main():
    template = template_parser('test-template.txt')

    with open('template.json', 'w') as f:
        json.dump(template, f, indent=4)
    

if __name__ == '__main__':
    main()

            
            
            


        
            
        




    


