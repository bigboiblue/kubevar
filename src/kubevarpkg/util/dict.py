from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from copy import deepcopy
from .checking import err

FuncType = Callable[[str, Any, list], tuple]
def recursive_map(func: FuncType, it: Union[list, dict], key_path = []) -> Union[list, dict]:
    """func(x, y) must have 2 params (key and value) and return a tuple (key, value).
    This will be added to new map. If None is returned, nothing is added
    The list / dict passed is traversed using a breadth first traversal

    When key returned by the passed func is a dict or list, the value is ignored, and the list/dict
    is appended to the current dict/list being traversed in the recursive function
    """

    new = list() if type(it) == list else dict()
    keys = range(len(list(it))) if type(it) == list else it.keys()

    for key in keys:
        ret = func(key, it[key], [*key_path, key])
        if ret is None:
            if key in new:
                new.pop(key)
        else:
            new_key, new_value = ret

            if it[key] == new_value and type(new_value) == list:  # Nothing changed & list
                new_value = []
            elif it[key] == new_value and isinstance(new_value, dict): # Nothing changed & dict
                new_value = {}  # Dont add whole dict, will be traversed later anyway

            print(type(new_key) == list or isinstance(new_key, dict) or type(new_key) == dict)
            if type(new_key) == list or isinstance(new_key, dict) or type(new_key) == dict:
                new = append(new, new_key)
            else:
                new = append(new, new_value, new_key)

            if (isinstance(it[key], dict) or type(it[key]) == list):
                new_key_path = deepcopy([*key_path, key])  # Key path refers to old maps key path (new may be different due to changed keys)
                new[new_key] = recursive_map(func, it[key], new_key_path)

    return new


def append(it: Union[list, dict], val: Any, key = None) -> Union[list, dict]:
    """Appends val to it (whether it be a list or dict).
    If it is a dict, and no key is entered, the val dict and it map are shallow merged"""
    new_it = it
    if type(new_it) == list:
        new_it.append(val)
    elif isinstance(new_it, dict):
        if key is None:
            if isinstance(val, dict):
                new_it = {**new_it, **val}
            else:
                err("If no key is specified when appending to a dict, a the input should be a dict")
        else:
            new_it[key] = val
    return new_it