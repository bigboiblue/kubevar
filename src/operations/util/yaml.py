import os
import yaml
from .checking import err
import re

def load_yaml(file_name: str, error_msg: str = None) -> dict:
    error_msg = f"The file: '{file_name}' has invalid yaml syntax. Please check spacing..." if error_msg == None else error_msg
    yaml_dict = dict()
    if not os.path.isfile(file_name) or not re.search("\.ya?ml$", file_name):
        err(f"{file_name} is not a yaml file")
    
    try:
        with open(file_name, mode='r') as file:
            yaml_dict = yaml.load(file.read(), Loader=yaml.FullLoader)
    except Exception as e:
        err(str(error_msg))
    return yaml_dict
###