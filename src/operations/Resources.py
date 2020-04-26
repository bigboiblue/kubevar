from .util.yaml import load_yaml
from .util.checking import err, warn
from benedict import benedict
from typing import *
import yaml
from copy import deepcopy
import re

class Resources:    
    def __init__(self, resource_names: List[str]):
        self.resources: List[benedict] = [] 
        for res_name in resource_names:
            self.resources.append(benedict(load_yaml(res_name)))
    

    def replace_variables(self, variables: dict):
        for res in self.resources:
            potentials = self.replace_variables_for_res(variables, res)
            print(yaml.dump(dict(potentials), indent=2))

    def replace_variables_for_res(self, variables: dict, res: benedict, potentials = benedict()) -> benedict:
        old_keys: list = []
        new_keys: list= []

        res = self.recurse_replace_variables_for_res(variables, res, cur_pass="value")
        res = self.recurse_replace_variables_for_res(variables, res, old_keys, new_keys, cur_pass="key")
        for index, old_key in enumerate(old_keys):
                if old_key in res:
                    res[new_keys[index]] = res.pop(old_key)
        return res


    ## // TODO: convert recusion into loop
    def recurse_replace_variables_for_res(self, variables: dict, res: benedict,  old_keys = [], new_keys = [], key_path = [], *, cur_pass = "value"):
        iterable = res.keys()
        if key_path != []:
            iterable = range(len(res[key_path])) if type(res[key_path]) == list else res[key_path].keys()

        for key in iterable: # Could be a list or dict
            key = [*key_path, key]
            pattern = re.compile("\$\{\{.*}\}")
            if cur_pass == "value":
                self.replace_res_values(res, key, pattern, variables)
            if cur_pass == "key":
                old, new = self.get_key_replacements(res, key, pattern, variables)
                for i in old:
                    old_keys.append(i)
                for i in new:
                    new_keys.append(i)

            if isinstance(res[key], dict) or isinstance(res[key], list):
                key_path.append(key[-1])
                self.recurse_replace_variables_for_res(variables, res, old_keys, new_keys, key_path, cur_pass=cur_pass)

        if len(key_path) > 0:
            key_path.pop()
        return res

    def replace_res_values(self, res: benedict, key: list, pattern, variables: dict):
        if type(res[key]) == str:
                value_matches = pattern.finditer(res[key])
                for match in value_matches:
                    var_name = res[key][match.start() + 3:match.end() - 2].strip()
                    
                    for label, value in variables.items():
                        if var_name == label:
                            if type(value) != str:
                                res[key] = deepcopy(value)
                            else:
                                res[key] = res[key][:match.start()] + str(value) + res[key][match.end():]
                            break
    
    def get_key_replacements(self, res, key, pattern, variables) -> Tuple[List, List]:
        new_keys, old_keys = [], []
        key_matches = pattern.finditer(str(key[-1]))
        for match in key_matches:
            var_name = key[-1][match.start() + 3:match.end() - 2].strip()
            for label, value in variables.items():
                if var_name == label:
                    if type(value) != str:
                        err("Keys can only contain string variables...")
                    new_key_value = key[-1][:match.start()] + str(value) + key[-1][match.end():]
                    old_keys.append(key)
                    new_keys.append([*key[:-1], new_key_value])
        return old_keys, new_keys

        

    def replace_list_for_resource(self):
        pass

    def replace_str_for_resource(self):
        pass

    def replace_map_for_resource(self):
        pass

    def __str__(self):
        return yaml.dump(self.resources, indent=2)