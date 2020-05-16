from math import ceil

from ..util.yaml import load_yaml
from ..util.checking import err, warn
from benedict import benedict
from typing import List, Tuple, Any, Dict, Match
import yaml
import re
from ..util.dict import recursive_map


class Resources:
    def __init__(self, resource_names: List[str]):
        self.resources: List[benedict] = []
        for res_name in resource_names:
            yamls = load_yaml(res_name, multiple=True)
            for y in yamls:
                self.resources.append(benedict(y, keypath_separator=None))

    def add_common_attributes(self, attributes: dict):
        for res in self.resources:
            for key_path, value in attributes.items():

                replacements: List[Tuple[int, str]] = []
                for match in re.finditer('".*"', key_path):
                    index = key_path.count('.', 0, match.start())
                    attr = key_path[match.start() + 1:match.end() - 1]
                    print(attr)
                    replacements.append((index, attr))
                key_path = re.sub('".*"', "", key_path)
                key_path_list = key_path.split('.')  # Cannot use dot separator in benedict

                for index, attr in replacements:
                    key_path_list[index] = attr

                for index, path in enumerate(key_path_list):
                    if path.startswith('"'):
                        key_path_list[index] = path[1:]

                res[key_path_list] = value

    #
    # def replace_variables(self, variables: dict):
    #     for res in self.resources:
    #         self.replace_variables_for_res(variables, res)

    def replace_variables(self, variables: dict):
        """
        Replaces all occurrences of variables in a resource
        :param variables: a dictionary where first order keys are the var names,
        and their values correspond to the variables value
        """
        from ..token import Token

        def func(key: str, val: Any, key_path: list) -> tuple:
            def replace_var(old: str, new: Any, match: Match, offset: int, *, is_key = True) -> Any:
                ##### Check if escaped
                should_replace = True
                before_match = old[:match.start()]
                escapes = re.search("\\\\+$", before_match)
                if escapes is not None:
                    length = escapes.end() - escapes.start()
                    # Escape backslashes (essentially half them)
                    new = new[:escapes.start() + offset] + ("\\" * int(length / 2)) + new[escapes.end() + offset:]
                    offset -= length - int(length / 2)
                    if length % 2 != 0:  # odd
                        should_replace = False  # Dont replace if ${{}} is escaped

                if should_replace:
                    if token == Token.FUNC:
                        pass
                    if token == Token.VAR:
                        for label, var_value in variables.items():
                            var_name = old[match.start() + 3:match.end() - 2].strip()  # Remove ${{ and }}
                            if var_name == label:
                                if is_key:  # Key of an attribute
                                    if type(var_value) != str and not isinstance(var_value, dict):
                                        err(f"Cannot substitute the '{label}' in a key! Only strings or maps can be substituted into a key (maps will overwrite the value associated with the key)")
                                    if type(var_value) == str:
                                        new = new[:match.start() + offset] + var_value + new[match.end() + offset:]
                                        offset += len(var_value) - (match.end() - match.start())
                                    elif isinstance(var_value, dict):
                                        new = var_value
                                        warn(f"The variable {label} is a map, and replaces a key. This appends the variable (map) to the parent map.\nA preferred syntax that leads to the same behaviour is to use '~append$(( {label} ))' as the value and any placeholder as the key (the key will be overwritten so it does not matter)")
                                else:  # The value of an attribute
                                    if type(var_value) in [str, int, float, bool]:
                                        new = new[:match.start() + offset] + str(var_value) + new[match.end() + offset:]
                                        offset += len(str(var_value)) - (match.end() - match.start())
                                    elif isinstance(var_value, dict) or type(var_value) == list:
                                        new = var_value

                return new, offset

            # key_path = tuple(key_path)
            new_key, new_value = key, val
            for token in Token:
                if token == Token.ESCAPE:
                    continue
                pattern = re.compile(token.value)

                offset = 0
                key_matches = pattern.finditer(str(key))
                for match in key_matches:
                    new_key, offset = replace_var(str(key), new_key, match, offset, is_key=True)

                offset = 0
                value_matches = []
                if type(val) not in [dict, list, benedict]:
                    value_matches = pattern.finditer(str(val))
                    for match in value_matches:
                        new_value, offset = replace_var(str(val), new_value, match, offset, is_key=False)

            return new_key, new_value

        for i, res in enumerate(self.resources):
            self.resources[i] = recursive_map(func, res)

    def replace_variables_for_res(self, variables: dict, res: benedict,
                                  potentials=benedict({}, keypath_separator=None)) -> benedict:
        old_keys: list = []
        new_keys: list = []

        res = self.recurse_replace_variables_for_res(variables, res, cur_pass="value")
        res = self.recurse_replace_variables_for_res(variables, res, old_keys, new_keys, cur_pass="key")
        old_keys.reverse()
        new_keys.reverse()

        ### Implement ${{}} syntax
        for index, old_key in enumerate(old_keys):
            if new_keys[index][-1] == "":  # if ${{}}
                value = res.pop(old_key)
                if len(old_key) > 2 and isinstance(res[old_key[:-2]], list):
                    if not isinstance(value, list):
                        err("Using ${{}} syntax in an array means the value should also be an array")
                    res.pop(old_key[:-1])
                    for list_item in value:
                        res[old_key[:-2]].append(list_item)
                elif len(old_key) > 1 and isinstance(res[old_key[:-1]], dict):
                    if not isinstance(value, dict):
                        err("Using ${{}} syntax in a map means the value should also be a map")
                    res[old_key[:-1]] = {**res[old_key[:-1]], **value}
                elif len(old_key) == 1:  # This is top level
                    if not isinstance(value, dict):
                        err("Using ${{}} syntax in a map means the value should also be a map")
                    res = {**res, **value}
                else:
                    err("Only arrays or maps can be used with the ${{}} syntax")
            else:
                res[new_keys[index]] = res.pop(old_key)

        return res

    ## // TODO: convert recusion into loop
    def recurse_replace_variables_for_res(self, variables: dict, res: benedict, old_keys=[], new_keys=[], key_path=[],
                                          *, cur_pass="value"):
        iterable = res.keys()
        if key_path != []:
            iterable = range(len(res[key_path])) if type(res[key_path]) == list else res[key_path].keys()

        for key in iterable:  # Could be a list or dict
            key = [*key_path, key]
            pattern = re.compile("\$\{\{.*}\}")
            if cur_pass == "value":
                self.replace_res_values(res, key, pattern, variables)
            if cur_pass == "key":
                old, new = self.get_key_replacements(res, key, pattern, variables)
                for i in old:
                    old_keys.append(i)
                for i in new:
                    new_keys.append(i)

            if isinstance(res[key], dict) or isinstance(res[key], list):
                key_path.append(key[-1])
                self.recurse_replace_variables_for_res(variables, res, old_keys, new_keys, key_path, cur_pass=cur_pass)

        if len(key_path) > 0:
            key_path.pop()
        return res

    def replace_res_values(self, res: benedict, key: list, pattern, variables: dict):
        from copy import deepcopy

        if type(res[key]) == str:
            value_matches = pattern.finditer(res[key])
            for match in value_matches:
                var_name = res[key][match.start() + 3:match.end() - 2].strip()

                for label, value in variables.items():
                    if var_name == label:
                        if type(value) != str:
                            res[key] = deepcopy(value)
                        else:
                            res[key] = res[key][:match.start()] + str(value) + res[key][match.end():]
                        break

    def get_key_replacements(self, res, key, pattern, variables) -> Tuple[List, List]:
        new_keys, old_keys = [], []
        key_matches = pattern.finditer(str(key[-1]))
        for match in key_matches:
            var_name = key[-1][match.start() + 3:match.end() - 2].strip()
            if var_name == "":
                old_keys.append(key)
                new_keys.append([*key[:-1], ""])
            for label, value in variables.items():
                if var_name == label:
                    if type(value) != str:
                        err("Keys can only contain string variables...")
                    new_key_value = key[-1][:match.start()] + str(value) + key[-1][match.end():]
                    old_keys.append(key)
                    new_keys.append([*key[:-1], new_key_value])

        return old_keys, new_keys

    def __str__(self):
        string = ""
        for res in self.resources:
            string += yaml.dump(dict(res), indent=2)
            if re.search("---\s*$", string) == None:
                string += "\n---\n"
        return string
