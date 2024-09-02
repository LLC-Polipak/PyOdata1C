from .fields import FilterResultField


def _not(s: FilterResultField):
    return FilterResultField(f"not({s})")


def isof():
    pass
