from .fields import Field, FilterResultField


def _not(s: FilterResultField):
    return FilterResultField(f"not({s})")


def q(s: FilterResultField | Field):
    return s.__class__(f'({s})')


def isof():
    pass
