from enum import Enum

class Token(Enum):
    """Enum for tokens. This is iterable. When iterating, highest priority tokens are used first."""

    # __order__ = "GRAVE FUNC VAR" <-- Order is automatically generated
    GRAVE = "`.*`"
    FUNC = "\~.*\$\(\(.*\)\)"
    VAR = "\$\{\{.*\}\}"

