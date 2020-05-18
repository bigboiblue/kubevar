from enum import Enum

class TokenType:
    def __init__(self, token_reg, name_reg):
        self.token_reg = token_reg
        self.name_reg = name_reg

class Token(Enum):
    """Enum for tokens. This is iterable. When iterating, highest priority tokens are used first."""

    # __order__ <--  Order is automatically generated
    ESCAPE = "\\"
    FUNC = TokenType("\~.*\$\(\([^(${{)]*\)\)", "(?<=\~).*(?=\$\(\([^(${{)]*\)\))") #[^(${{)]*
    VAR = TokenType("\$\{\{[^(${{)]*\}\}", "(?<=\$\{\{)[^(${{)]*(?=\}\})") # Will still need to strip the variable of whitespace

