from .fields import FilterResultField


def _not(s: FilterResultField):
    return f"not({s})"


def isof():
    pass
