from .util.yaml import load_yaml
from .util.checking import err, warn
from benedict import benedict
from typing import *
import yaml
import re

class Resources:    
    def __init__(self, resource_names: List[str]):
        self.resources: List[benedict] = [] 
        for res_name in resource_names:
            self.resources.append(benedict(load_yaml(res_name)))
    

    def replace_variables(self, variables: list):
        for res in self.resources:
            potentials = self.get_potentials_from(res)
            
            # key_path: list = []
            # iterable = {}
            # for 
            # iterable = enumerate(res) if type(res) == list else benedict(res).items()

            # for key, value, in iterable: # Could be a list or dict
            #     key = [*key_path, key]
            #     if re.search("\$\{\{.*}\}", str(key[-1])) != None:
            #         potentials[key] = value
            #     if isinstance(value, str) and re.search("\$\{\{.*}\}", value) != None:
            #         potentials[key] = value
            #     if isinstance(value, dict) or isinstance(value, list):
            #         key_path.append(key[-1])
            #         self.get_potentials_from(res[key[-1]], potentials, key_path)
            #         if isinstance(value, list): # Remove null values
            #             potentials[key] = list(filter(lambda x: x != None, potentials[key]))

    ## // TODO: convert recusion into loop
    def get_potentials_from(self, res: Union[benedict, list], potentials = benedict(), key_path = []):
        iterable = enumerate(res) if type(res) == list else benedict(res).items()

        for key, value, in iterable: # Could be a list or dict
            key = [*key_path, key]
            if re.search("\$\{\{.*}\}", str(key[-1])) != None:
                potentials[key] = value
            if isinstance(value, str) and re.search("\$\{\{.*}\}", value) != None:
                potentials[key] = value
            if isinstance(value, dict) or isinstance(value, list):
                key_path.append(key[-1])
                self.get_potentials_from(res[key[-1]], potentials, key_path)
                if isinstance(value, list): # Remove null values
                    potentials[key] = list(filter(lambda x: x != None, potentials[key]))

        if len(key_path) > 0:
            key_path.pop()
        return potentials


    def replace_list_for_resource(self):
        pass

    def replace_str_for_resource(self):
        pass

    def replace_map_for_resource(self):
        pass

    def __str__(self):
        return yaml.dump(self.resources, indent=2)