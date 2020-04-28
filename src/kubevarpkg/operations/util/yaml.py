from os import path
from yaml import load, load_all, FullLoader
from .checking import err
from re import search as re_search
from typing import Dict, List, Tuple, Union, Optional, Any

def load_yaml(file_name: str, error_msg: str = None, *, multiple=False) -> Union[dict, List[dict]]:
    error_msg = f"The file: '{file_name}' has invalid yaml syntax. Please check spacing..." if error_msg == None else error_msg
    yaml_output: Union[dict, List[dict]] = []
    if not path.isfile(file_name) or not re_search("\.ya?ml$", file_name):
        err(f"{file_name} is not a yaml file")
    
    try:
        with open(file_name, mode='r') as file:
            if multiple == True:
                yaml_output = load_all(file.read(), Loader=FullLoader)
            else:
                yaml_output = load(file.read(), Loader=FullLoader)
    except Exception as e:
        err(str(error_msg))
    return yaml_output
###