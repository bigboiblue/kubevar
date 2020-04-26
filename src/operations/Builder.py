import click
import os
import yaml
import re
from .util.checking import err, warn
from .util.yaml import load_yaml
from glob import glob
from typing import Set, Tuple, Any, List
from .Resources import Resources

class Builder:
    build_help = """
        --- Overview ---\n
        Output kubernetes manifests (yaml) where all ${{ VARIABLES }} are converted into the values defined in file specified by PATH.\n
        --- Conventions ---\n
        It is convention for the file at PATH to take the format *.kubervar.yaml therefore there is no need to append ".kubevar.yaml" to the PATH if convention is followed.\n
        If the file you are referencing is simply named "kubevar.yaml", then PATH only needs to specify the directory. Additionally, PATH does not need to be specified if you currently reside in the target directory\n
        --- *.kubevar.yaml format ---\n
    """


    def __init__(self):
        self.file= ""
        self.directory = ""
        self.framework_config = {
            "vars": {
                "dynamic": {},
                "static": {}
            },
            "common": {},
            "resources": []
        }



    def get_file_from_path(self, path: str) -> str:
        path = path.strip()
        if not os.path.exists(path):
            err("The PATH specified is not a file nor a directory!")

        file = os.path.join(path, "kubevar.yaml") if os.path.isdir(path) else path
        if not os.path.isfile(file) or not file.endswith(".yaml"):
            err("Incorrect path.\n\
                * If you specified a \033[1;33mdirectory\033[m, no kubevar.yaml is present in that directory\
                * If you specified a \033[1;33mfile\033[m, it is not a yaml file")
        return file
    

    def unglob_resources(self, config: dict, arePathsTranslated = True):
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
        config_dir = self.directory if config_dir == None else config_dir
        merged_config = base_config
        merged_config["resources"] = list(map(lambda x: os.path.join(config_dir, x), merged_config["resources"]))

        for key in config.keys():
            if key == "common":
                merged_config["common"] = {**merged_config["common"], **config["common"]}
            elif key == "vars":
                for var_type in ["static", "dynamic"]:
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


    
    def build(self, path: str):
        ######## Retreive data ########
        self.file = self.get_file_from_path(path)
        self.directory = os.path.dirname(self.file)

        config = load_yaml(self.file)
        base_config = {}
        if "extends" in config:
            base_config_path = os.path.join(self.directory, config["extends"])
            base_config = load_yaml(base_config_path)
        
        # Applied framework to each
        config = {**self.framework_config, **config}
        base_config = {**self.framework_config, **base_config}

        merged_config = self.get_merged_config(base_config, config)
        self.unglob_resources(merged_config)

        self.check_variable_collisions(merged_config)

        ######## Replace resources ########
        resources = Resources(merged_config["resources"])
        resources.add_common_attributes(merged_config["common"])
        resources.replace_variables(merged_config["vars"]["static"])
        print(resources)
        # self.replace_dynamic_variables(merged_config) #Will implement later
        
    ###


###

@click.command(help=Builder.build_help)
@click.argument("PATH", required=False, default='.')
def build(path: str):
    builder = Builder()
    builder.build(path)
