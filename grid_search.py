# -*- coding: utf-8 -*-
"""
Creates configurations for a systematic grid search of hyperparameters.

Created on Wed Feb  7 15:31:59 2018

@author: lbechberger
"""

import sys, ast
from configparser import ConfigParser


template_file_name = sys.argv[1]
template_config = sys.argv[2]
input_config = ConfigParser()
input_config.read(template_file_name)
template_dict = dict(input_config[template_config])

constant_part = {}
search_part = {}
for name, value in template_dict.items():
    parsed_value = ast.literal_eval(value)
    if isinstance(parsed_value, list):
        search_part[name] = parsed_value
    else:
        constant_part[name] = parsed_value

output_config = ConfigParser()
config_names = []

search_names = sorted(search_part.keys())

def get_config_string(full_dictionary):
    parts = []
    for name in search_names:
        parts.append("{0}{1}".format(name[0:2], full_dictionary[name]))
    return "-".join(parts)

def append_to_config(search_name_idx, current_dict):
    name = search_names[search_name_idx]
    possible_values = search_part[name]
    for value in possible_values:
        local_dict = current_dict.copy()
        local_dict[name] = value
        if search_name_idx + 1 < len(search_names):
            append_to_config(search_name_idx + 1, local_dict)
        else:
            config_string = get_config_string(local_dict)
            output_config[config_string] = local_dict
            config_names.append(config_string)

append_to_config(0, constant_part)    

num_configs = 1
for value in search_part.values():
    num_configs *= len(value)

print("Created {0} configurations".format(num_configs))

with open('grid_search.cfg', 'w') as f:
    output_config.write(f)
    
with open('params.txt', 'w') as f:
    for config_name in config_names:
        f.write(config_name + '\n')
    f.write('\n')