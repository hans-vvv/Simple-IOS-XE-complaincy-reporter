import os
import json
from glob import glob
from collections import Counter
from multiprocessing import Pool
from ios_xe_parser import ios_xe_parser
from template_parser import template_parser
from complaince_check import complaince_check


def main():

    base_dir = os.getcwd()
    template_file = 'config-template.txt'
    template = template_parser(template_file)

    os.chdir(base_dir + '\\backup')
    config_files = [configfile for configfile in glob('*.txt')]

    # list of Tree objects
    # Use list comprehension during debugging, else use multiprocessing
    # configs = [ios_xe_parser(config) for config in config_files]
    pool = Pool()
    configs = pool.map(ios_xe_parser, config_files)
    print('Number of IOS configurations read: ' + str(len(configs)))
    os.chdir(base_dir)
 
##    with open('configs.json', 'w') as f:
##        json.dump(configs, f, indent=4)
##
##    with open('template.json', 'w') as f:
##        json.dump(template, f, indent=4)

    with open('complaincy_result.txt', 'w') as f:
        errors_per_device = []
        number_configs_checked = 0
        for config in configs:
            # Simple filter, only configs with IOS version 16.1 are analysed.
            if 'version 16.1' in config['global_cfg']:
                number_configs_checked += 1
                result, errors = complaince_check(config, template)
                errors_per_device.append(errors)
                for line in result:
                    print(line, file=f)
        fmt = 'The number of checked configurations is: '
        print(fmt + str(number_configs_checked))
        for errors, number in sorted(dict(Counter(errors_per_device)).items()):
            (w1, w2) = ('is', '') if number == 1 else ('are', 's')
            w3 = '' if errors == 1 else 's'
            fmt = 'There {} {} device{} with {} error{}'
            print(fmt.format(w1, number, w2, errors, w3))
 

if __name__ == '__main__':
    main()   


