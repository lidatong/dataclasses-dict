from typing import Collection, Optional

from dataclasses import asdict, fields, is_dataclass


class DataclassDictMixin:
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, kvs):
        return _decode_dataclass(cls, kvs)


def _decode_dataclass(cls, kvs):
    init_kwargs = {}
    for field in fields(cls):
        field_value = kvs[field.name]
        if is_dataclass(field.type):
            init_kwargs[field.name] = _decode_dataclass(field.type, field_value)
        elif _is_supported_generic(field.type) and field.type != str:
            init_kwargs[field.name] = _decode_generic(field.type, field_value)
        else:
            init_kwargs[field.name] = field_value
    return cls(**init_kwargs)


def _is_supported_generic(type_):
    is_collection = _issubclass_safe(type_, Collection)
    is_optional = (_issubclass_safe(type_, Optional)
                   or _hasargs(type_, type(None)))
    return is_collection or is_optional


def _decode_generic(type_, value):
    if not value:
        res = value
    elif _issubclass_safe(type_, Collection):
        # this is a tricky situation where we need to check both the annotated
        # type info (which is usually a type from `typing`) and check the
        # value's type directly using `type()`.
        #
        # if the type_arg is a generic we can use the annotated type, but if the
        # type_arg is a typevar we need to extract the reified type information
        # hence the check of `is_dataclass(value)`
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            xs = (_decode_dataclass(type_arg, v) for v in value)
        elif _is_supported_generic(type_arg):
            xs = (_decode_generic(type_arg, v) for v in value)
        else:
            xs = value
        # get the constructor if using corresponding generic type in `typing`
        # otherwise fallback on the type returned by
        try:
            res = type_.__extra__(xs)
        except TypeError:
            res = type_(xs)
    else:  # Optional
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            res = _decode_dataclass(type_arg, value)
        elif _is_supported_generic(type_arg):
            res = _decode_generic(type_arg, value)
        else:
            res = value
    return res


def _issubclass_safe(cls, classinfo):
    try:
        result = issubclass(cls, classinfo)
    except Exception:
        return False
    else:
        return result


def _isinstance_safe(o, t):
    try:
        result = isinstance(o, t)
    except Exception:
        return False
    else:
        return result


def _hasargs(type_, *args):
    try:
        res = all(arg in type_.__args__ for arg in args)
    except AttributeError:
        return False
    else:
        return res
