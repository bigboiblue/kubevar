from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from copy import deepcopy

FuncType = Callable[[str, Any, list], tuple]
def recursive_map(func: FuncType, it: Union[list, dict], key_path = []) -> Union[list, dict]:
    """func(x, y) must have 2 params (key and value) and return a tuple (key, value).
    This will be added to new map. If None is returned, nothing is added
    The list / dict passed is traversed using a breadth first traversal"""
    new = list() if type(it) == list else dict()
    keys = range(len(list(it))) if type(it) == list else it.keys()
    call_queue = []  # Cannot use call stack since breadth first is required (which needs queue) to delete unwanted keys

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

            if type(new) == list:
                new.append(new_value)
            elif type(new) == dict:
                new[new_key] = new_value

            if (isinstance(it[key], dict) or type(it[key]) == list):
                new_key_path = deepcopy([*key_path, key])
                # call_queue.append((key, func, it[key], new_key_path))
                new[new_key] = recursive_map(func, it[key], new_key_path)

    # print(key_path)
    # if len(call_queue) != 0:
    #     key, *args = call_queue.pop(0)
    #     new[key] = recursive_map(*args)

    return new