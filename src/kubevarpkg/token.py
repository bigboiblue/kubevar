from enum import Enum
from os import path
from .util.yaml import load_yaml, clean_escapes, recursive_map
from .util.checking import err
from yaml import dump

token_path = path.normpath(path.realpath(path.join(path.dirname(__file__), "../tokens.yaml")))
tokens = {}
try:
    tokens = load_yaml(token_path)["tokens"]
except Exception as e:
    err("'tokens' attribute should be at root of tokens.yaml file")

# tokens = clean_escapes(tokens)
def test(x, y):
    if type(y) == str:
        return "key_" + str(x), "NUGGET-" + str(y)
    return x, y

someMap = {
    "Hello": {
        "oi": "U WOT",
        "well well": {
            "wella": "cool"
        },
        "sick": [1, 2, 4]
    },
    "Cheeky": {
        "monkeh": "ok so basically im monkeh",
        "col": "dwad"
    },
    "Beet": "root",
    "ARRRR": ["dwad", "|dwa", "dwaoijdoij"]
}

someMap = recursive_map(test, someMap)
# print(type(someMap["ARRRR"]))
# someMap["ARRRR"] = list(someMap["ARRRR"])
print(dump(someMap, indent=2))

# Token = Enum("")