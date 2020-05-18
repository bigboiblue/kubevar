from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from copy import deepcopy
from .checking import err

class MapFlags:
    def __init__(self):
        self.append = False  # Append dict / list to current dict \ list being iterated
        self.omit = False  # Dont include returned key / val in new map


FuncType = Callable[[str, Any, list], tuple]
def recursive_map(func: FuncType, it: Union[list, dict], key_path = []) -> Union[list, dict]:
    """func(x, y) must have 2 params (key and value) and return a tuple (key, value, flags). (See MapFlags for flag info)
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
            new_key, new_value, flags = ret

            ### Ensures dicts / lists aren't added twice when keys change
            if it[key] == new_value and type(new_value) == list:  # Nothing changed & list
                new_value = []
            elif it[key] == new_value and isinstance(new_value, dict): # Nothing changed & dict
                new_value = {}  # Dont add whole dict, will be traversed later anyway

            if flags.append:
                if type(new) == list:
                    new = [*new, *new_value]
                elif isinstance(new, dict):
                    new = {**new, **new_value}
            else:
                new = append(new, new_value, new_key)

            if (isinstance(it[key], dict) or type(it[key]) == list):
                new_key_path = deepcopy([*key_path, key])  # Key path refers to old maps key path (new may be different due to changed keys)
                new[new_key] = recursive_map(func, it[key], new_key_path)

    return new


def append(it: Union[list, dict], val: Any, key = None) -> Union[list, dict]:
    new_it = it
    if type(new_it) == list:
        new_it.append(val)
    elif isinstance(new_it, dict):
        new_it[key] = val
    return new_it

