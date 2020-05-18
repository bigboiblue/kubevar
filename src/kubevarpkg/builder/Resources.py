from math import ceil

from ..util.yaml import load_yaml
from ..util.checking import err, warn
from benedict import benedict
from typing import List, Tuple, Any, Dict, Match
import yaml
import re
from ..util.dict import recursive_map
from ..token import Token
from ..function import Function


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

        def func(key: str, val: Any, key_path: list) -> tuple:
            new_key, new_value = key, val
            for token in Token:
                if token == Token.ESCAPE:
                    continue
                pattern = re.compile(token.value.token_reg)

                offset = 0
                key_matches = pattern.finditer(str(key))
                for match in key_matches:
                    new_key, offset = self.replace_token(token, str(key), new_key, match, offset, variables, is_key=True)

                offset = 0
                if type(val) not in [dict, list, benedict]:
                    value_matches = pattern.finditer(str(val))
                    for match in value_matches:
                        new_value, offset = self.replace_token(token, str(val), new_value, match, offset, variables, is_key=False)

            return new_key, new_value

        for i, res in enumerate(self.resources):
            self.resources[i] = recursive_map(func, res)


    @staticmethod
    def replace_token(token: Token, old: str, new: Any, match: Match, offset: int, variables: dict, *, is_key = True) -> Any:
        """
        Replaces a token that is located at "match" param in the "old" string. "new" refers to the object
        to the partially replaced new value. This will be modified and returned. "offset" refers to the current
        string offset (used to add and remove string elements in the right place in "new"). "variables"
        refers to the variables to check against the token for a match.
        If replacing a key, "is_key" should be true (the behaviour is slightly different)
        """

        ##### Check if escaped
        should_replace = True
        match_string = old[match.start():match.end()]
        pattern = re.compile(token.value.name_reg)
        label_match = pattern.search(match_string)
        token_label = match_string[label_match.start(): label_match.end()] if label_match is not None else ""
        before_match = old[:match.start()]
        escapes = re.search("\\\\+$", before_match)
        if escapes is not None:
            length = escapes.end() - escapes.start()
            # Escape backslashes (essentially half them)
            new = new[:escapes.start() + offset] + ("\\" * int(length / 2)) + new[escapes.end() + offset:]
            offset -= length - int(length / 2)
            if length % 2 != 0:  # odd
                should_replace = False  # Dont replace if ${{}} is escaped

        ### Replace
        if should_replace:
            if token == Token.FUNC:
                params = [token.value.get_param(match_string, i).strip() for i in range(match_string.count(',') + 1)]
                print(f"Function Name {token_label} --- params: {params}")
                if token_label == Function.BASE64.value:
                    pass
                elif token_label == Function.APPEND.value:
                    pass
            elif token == Token.VAR:
                for label, var_value in variables.items():
                    var_name = old[match.start() + 3:match.end() - 2].strip()  # Remove ${{ and }} // TODO Remove values 3 and -2, and calculate the number of chars until var_name instead
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

    def __str__(self):
        string = ""
        for res in self.resources:
            string += yaml.dump(dict(res), indent=2)
            if re.search("---\s*$", string) is None:
                string += "\n---\n"
        return string
