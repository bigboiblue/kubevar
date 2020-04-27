import os
import yaml
from .checking import err
import re
from typing import *

def load_yaml(file_name: str, error_msg: str = None, *, multiple=False) -> Union[dict, List[dict]]:
    error_msg = f"The file: '{file_name}' has invalid yaml syntax. Please check spacing..." if error_msg == None else error_msg
    yaml_output: Union[dict, List[dict]] = []
    if not os.path.isfile(file_name) or not re.search("\.ya?ml$", file_name):
        err(f"{file_name} is not a yaml file")
    
    try:
        with open(file_name, mode='r') as file:
            if multiple == True:
                yaml_output = yaml.load_all(file.read(), Loader=yaml.FullLoader)
            else:
                yaml_output = yaml.load(file.read(), Loader=yaml.FullLoader)
    except Exception as e:
        err(str(error_msg))
    return yaml_output
###