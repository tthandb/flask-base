from enum import Enum


def get_names_of_enum(enum_object):
    if issubclass(enum_object, Enum):
        return list(enum_object.__members__.keys())
    return []
