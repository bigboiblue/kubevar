from os import path
from yaml import load, load_all, FullLoader, dump
from .checking import err
from re import search as re_search
from re import sub as re_sub
from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from copy import deepcopy


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




FuncType = Callable[[str, Union[str, int, float, list, dict]], Union[list, dict]]
def recursive_map(func: FuncType, it: Union[list, dict]) -> Union[list, dict]:
    """func(x, y) must have 2 params (key and value) and return a tuple (key, value).
    This will be added to new map. If None is returned, nothing is added"""
    new = list() if type(it) == list else dict()
    keys = range(len(list(it))) if type(it) == list else it.keys()

    for key in keys:
        ret = func(key, it[key])
        if ret is not None:
            new_key, new_value = ret
            if type(it) == list:
                new.append(new_value)
            else:
                new[new_key] = new_value

        if isinstance(it[key], dict) or type(it[key]) == list:
            new[key] = recursive_map(func, it[key])
    return new
