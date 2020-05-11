from enum import Enum

class Token(Enum):
    """Enum for tokens. This is iterable. When iterating, highest priority tokens are used first."""

    # __order__ <--  Order is automatically generated
    ESCAPE = "\\"
    FUNC = "\~.*\$\(\([^(${{)]*\)\)" #[^(${{)]*
    VAR = "\$\{\{[^(${{)]*\}\}"

