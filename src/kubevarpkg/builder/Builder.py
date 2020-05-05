import os
from ..util.checking import err, warn
from ..util.yaml import load_yaml
import re
from typing import Dict, Union, Any, Set, Tuple
from benedict import benedict
from base64 import b64encode

class Builder:
    def __init__(self):
        self.resources = None
        self.file= ""
        self.directory = ""
        self.framework_config = {
            "vars": {
                "dynamic": {},
                "static": {},
                "file": {}
            },
            "common": {},
            "resources": []
        }
        self.framework_config = benedict(self.framework_config, keypath_separator=None)






    def get_file_from_path(self, path: str) -> str:
        path = path.strip()
        if not os.path.exists(path):
            err("The PATH specified is not a file nor a directory!")

        file = os.path.join(path, "kubevar.yaml") if os.path.isdir(path) else path
        if not os.path.isfile(file) or not file.endswith(".yaml"):
            err("""Incorrect path.
* If you specified a \033[1;33mdirectory\033[m, no kubevar.yaml is present in that directory
* If you specified a \033[1;33mfile\033[m, it is not a yaml file""")
        return file
    




    def unglob_resources(self, config: dict, arePathsTranslated = True):
        from glob import glob
        
        res_names: Set[str] = set()
        if "resources" in config:
            ### If wildcard exists, add files according to wildcard
            for res_path in config["resources"]:
                if not arePathsTranslated:
                    res_path = os.path.normpath(os.path.join(self.directory, res_path))
                glob_names = set(glob(res_path))
                glob_names -= set(glob(os.path.join(os.path.dirname(res_path), "*kubevar.yaml"))) # Remove kubervar files
                res_names |=  glob_names if len(glob_names) > 0 else {res_path}

            config["resources"] = list(res_names)
        





    def get_merged_config(self, base_config: dict, config: dict, config_dir = None) -> dict:
        """
            Merges the two configs (the second passed gets precedence).
            All paths are converted to paths relative to the current directory where kubevar was called
        """

        config_dir = self.directory if config_dir == None else config_dir # Current configs directory ( this is recursive )
        merged_config = base_config
        merged_config["resources"] = list(map(lambda x: os.path.join(config_dir, x), merged_config["resources"]))

        for key in config.keys():
            if key == "common":
                merged_config["common"] = {**merged_config["common"], **config["common"]}
            elif key == "vars":
                for c in merged_config, config: # Convert file paths
                    for label in c["vars"]["file"].keys():
                        c["vars"]["file"][label] = os.path.join(config_dir, c["vars"]["file"][label])
                for var_type in ["static", "dynamic", "file"]:
                    merged_config["vars"][var_type] = {**merged_config["vars"][var_type], **config["vars"][var_type]}
            elif key == "resources":
                for res_name in config["resources"]:
                    res_path = os.path.join(config_dir, res_name)
                    if res_path not in merged_config["resources"]:
                        merged_config["resources"].append(res_path)
            elif key == "extends":
                pass
            else:
                if key not in self.framework_config:
                    warn(f"Unknown attribute: '{key}'")
                
        if "extends" in merged_config: # Repeat the process
            new_config = merged_config
            new_config_dir = os.path.join(config_dir, config["extends"]) # The new config_dir is the previous base_config dir. This is needed since they are relative directories
            new_base_config = load_yaml(os.path.join(config_dir, merged_config["extends"]))
            merged_config = self.get_merged_config(new_base_config, new_config, new_config_dir)

        if len(merged_config) == 0:
            err("Config file invalid. No: 'common', 'vars', 'resources', or 'extends' attributes")
        if "resources" not in merged_config:
            err("No resources included!")

        removal_queue = []
        for key in merged_config.keys():
            if key not in self.framework_config:
                warn(f"Unknown attribute: '{key}'")
                removal_queue.append(key)
        for key in removal_queue:
            merged_config.pop(key)

        return merged_config




    def check_variable_collisions(self, config: dict):
        vars = config["vars"]
        for static_var in vars["static"]:
            if static_var in vars["dynamic"]:
                err(f"Variable collision --- {static_var} included in both static and dynamic vars...")






    def get_converted_file_variables(self, variables: dict) -> dict:
        converted_variables: Dict[str, str] = {}
        
        for key, value in variables.items():
            ## Checks
            if type(value) != str or not os.path.isfile(value):
                err("File variables must be a string containing a relative path to a file")

            with open(value, mode='r') as file:
                contents = file.read()
                converted_variables[key] = contents
        return converted_variables





    def apply_framework(self, framework: dict, config: Any) -> dict:
        if isinstance(config, dict) and isinstance(framework, dict):
            for key, value in framework.items():
                if key not in config:
                    config[key] = value
                else:
                    self.apply_framework(framework[key], config[key])
        return config




    def preprocess_config(self, config: Union[dict, list]):        
        iterable = range(len(config)) if type(config) == list else config.keys()

        ### b64 encode 
        pattern = re.compile("\~b64\(\(.*\)\)")
        for key in iterable: # Could be a list or dict
            if type(config[key]) == str:
                replacements = pattern.findall(config[key])
                for r in replacements:
                    r = str(r[6:-2])
                    r = b64encode(r.encode("utf-8")).decode("utf-8")
                    config[key] = pattern.sub(r, config[key], 1)
            if isinstance(config[key], dict) or type(config[key]) == list:
                self.preprocess_config(config[key])

    def build(self, path: str) -> str:
        from .Resources import Resources

        ######## Retreive data ########
        self.file = self.get_file_from_path(path)
        self.directory = os.path.dirname(self.file)

        config = load_yaml(self.file)
        base_config: dict = {}
        if "extends" in config:
            base_config_path = os.path.join(self.directory, config["extends"])
            base_config = load_yaml(base_config_path)
        
        # Applied framework to each
        self.apply_framework(self.framework_config, config)
        self.apply_framework(self.framework_config, base_config)

        merged_config = self.get_merged_config(base_config, config)
        self.unglob_resources(merged_config)

        self.check_variable_collisions(merged_config)
        self.preprocess_config(merged_config)

        ######## Replace resources ########
        self.resources = Resources(merged_config["resources"])
        self.resources.add_common_attributes(merged_config["common"])

        file_variables = self.get_converted_file_variables(merged_config["vars"]["file"])
        all_variables = {**merged_config["vars"]["static"], **file_variables}
        self.resources.replace_variables(all_variables)
        # self.replace_dynamic_variables(merged_config) #Will implement later

        return str(self.resources)
            
        
    ###



###