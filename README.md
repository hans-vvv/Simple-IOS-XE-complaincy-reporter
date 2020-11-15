# Simple-IOS-XE-complaincy-reporter
This script reads one or more Cisco IOS-XE based configurations and compare these with a template configuration. Both global and hierarchical configuration items can be compared. The main.py file runs the script. In the backup directory the configurations of the network elements must be present. Three basic functions are used to get the job done, a function to parse the configuration template, a function to parse a IOS-XE configuration file and a function to compare a parsed template and a parsed configuration.

The template file contains the information to compare with a device configuration. The basic idea is to define all mandatory global configuration items and to define the items which must be ignored in the comparison of the items of the device configurations. This enables you to present global configuration items which are missing in the device configuration but are defined in the template and to present items which are not defined in the template but are present in the device configuration. 

The template must only contains hierarchical items which you want to compare with the device configurations. Also you can specify one or more optional hierarchical configuration items after the "# Grouped optional config items" line in the template file. Multiple of these lines can be present to specify one or more optional items. Furthermore the <<>> 'sign' can be used as wildcard in the template file. At last, don't forget to put a "!" at the last line of the template file as this is used as a seperator.

I think there are some self explanatory template items (starting with #) to include or exclude items from the template definitions. The logic of the script is tested with a large base of layer-2 switches. So hopefully all the bugs have run away. The result of the comparison is presented in the "complaincy_result.txt" text file.

Hans Verkerk - November 2020
