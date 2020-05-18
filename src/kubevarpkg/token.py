from enum import Enum
from .util.checking import err

class TokenType:
    def __init__(self, token_reg, name_reg):
        self.token_reg = token_reg
        self.name_reg = name_reg

class FuncType(TokenType):
    def __init__(self, token_reg, name_reg, param_reg):
        super().__init__(token_reg, name_reg)
        self.param_reg = param_reg

    def get_param(self, func: str, pos = 0) -> str:
        import re
        match = re.search(self.param_reg, func)
        if match is not None:
            num_args = func.count(',', match.start()) + 1
            if pos >= num_args:
                err(f"Only {num_args} args exist in {func}. Cannot get arg at position {pos}")
            ret = list(re.finditer("(\(\(|,|\))", func))
            return func[ret[pos].end():ret[pos + 1].start()]
        else:
            return ""

class Token(Enum):
    """Enum for tokens. This is iterable. When iterating, highest priority tokens are used first."""

    # __order__ <--  Order is automatically generated
    ESCAPE = "\\"
    FUNC = FuncType("\~\w*\$\(\(.*\)\)", "(?<=\~)\w*(?=\$\(\(.*\)\))", "(?<=\$\(\().*(?=\)\))") # //TODO: Dissalow comma, $ { ( ) } [ ]
    VAR = TokenType("\$\{\{[^(${{)]*\}\}", "(?<=\$\{\{)[^(${{)]*(?=\}\})") # Will still need to strip the variable of whitespace

