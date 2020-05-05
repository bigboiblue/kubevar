from typing import Dict, List, Tuple, Union, Optional, Any, Callable

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