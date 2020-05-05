import os
from ..util.checking import err, warn
from ..util.yaml import load_yaml
import re
from typing import Dict, Union, Any, Set, Tuple
from benedict import benedict
from base64 import b64encode
from ..util.dict import recursive_map

class Builder:
    def __init__(self):
        self.resources = None
        self.config_file = ""
        self.config_dir = ""
        self.framework_config = benedict({
            "vars": {
                "dynamic": {},
                "static": {},
                "file": {}
            },
            "common": {},
            "resources": []
        },  keypath_separator=None)






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
                    res_path = os.path.normpath(os.path.join(self.config_dir, res_path))
                glob_names = set(glob(res_path))
                glob_names -= set(glob(os.path.join(os.path.dirname(res_path), "*kubevar.yaml"))) # Remove kubervar files
                res_names |=  glob_names if len(glob_names) > 0 else {res_path}

            config["resources"] = list(res_names)
        

    def convert_paths(self, config: dict, config_dir) -> dict:
        """Make paths in the config relative to the directory kubevar was called in"""
        new_config = config
        new_config["vars"]["file"] = {key: os.path.join(config_dir, val) for key, val in new_config["vars"]["file"].items()}
        new_config["resources"] = [os.path.join(config_dir, x) for x in new_config["resources"]]
        return new_config



    def get_extended_config(self, config: dict, config_dir = None) -> dict:
        """Merges the two configs (the second passed gets precedence).
        All paths are converted to paths relative to the current directory where kubevar was called"""
        if "extends" not in config:
            return config
        config_dir = self.config_dir if config_dir is None else config_dir # Current configs directory ( this is recursive )
        base_config_dir = os.path.dirname(os.path.normpath(os.path.join(config_dir, config["extends"])))
        base_config = load_yaml(os.path.join(config_dir, config["extends"]))

        ### Pre-process
        self.apply_framework(config)
        self.apply_framework(base_config)


        merged_config = base_config

        config = self.convert_paths(config, config_dir)
        merged_config = self.convert_paths(merged_config, base_config_dir)

        ### MERGE
        merged_config["common"] = {**merged_config["common"], **config["common"]}
        for var_type in ["static", "dynamic", "file"]:
            merged_config["vars"][var_type] = {**merged_config["vars"][var_type], **config["vars"][var_type]}
        merged_config["resources"] = [*merged_config["resources"], *config["resources"]]

        ### RECURSE IF EXTENDS EXISTS
        if "extends" in merged_config: # Repeat the process
            new_config = merged_config
            new_config_dir = os.path.join(config_dir, config["extends"]) # The new config_dir is the previous base_config dir. This is needed since they are relative directories
            new_base_config = load_yaml(os.path.join(config_dir, merged_config["extends"]))
            merged_config = self.get_extended_config(new_base_config, new_config, new_config_dir)

        self.check_not_empty(merged_config)
        self.check_unknown_attributes(merged_config)

        return merged_config






    def join_paths(self, paths: dict, base_dir: str):
        new = {}
        for key, path in paths.items():
            path = os.path.normpath(os.path.join(path, base_dir))
            new[key] = path
        return new

    def check_not_empty(self, merged_config):
        if len(merged_config) == 0:
            err("Config file invalid. No: 'common', 'vars', 'resources', or 'extends' attributes")
        if "resources" not in merged_config:
            err("No resources included!")

    def check_unknown_attributes(self, merged_config):
        for key in merged_config.keys():
            if key not in self.framework_config:
                err(f"Unknown attribute: '{key}'")


    def check_var_duplicates(self, config: dict):
        vars = config["vars"]
        all_labels = []
        for label in {**vars["static"], **vars["dynamic"], **vars["file"]}.keys():
            all_labels.append(label)
        label_set = set()
        duplicates = set(x for x in all_labels if x in label_set or label_set.add(x))
        if len(duplicates) != 0:
            err(f"Multiple definitions exist for the following variables: {''.join(map(str, duplicates))} Variables can only be defined once...")



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





    def apply_framework(self, config: Any, *, framework = None) -> dict:
        framework = self.framework_config if framework is None else framework
        if isinstance(config, dict) and isinstance(framework, dict):
            for key, value in framework.items():
                if key not in config:
                    config[key] = value
                else:
                    self.apply_framework(config[key], framework=framework[key])
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
        self.config_file = self.get_file_from_path(path)
        self.config_dir = os.path.dirname(self.config_file)

        config = self.get_extended_config(load_yaml(self.config_file))

        self.unglob_resources(config)

        self.check_var_duplicates(config)
        self.preprocess_config(config)

        ######## Replace resources ########
        self.resources = Resources(config["resources"])
        self.resources.add_common_attributes(config["common"])

        file_variables = self.get_converted_file_variables(config["vars"]["file"])
        all_variables = {**config["vars"]["static"], **file_variables}
        self.resources.replace_variables(all_variables)
        # self.replace_dynamic_variables(merged_config) #Will implement later

        return str(self.resources)
