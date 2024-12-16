#
# Copyright 2024 Tabs Data Inc.
#

from enum import Enum, auto


class Status(Enum):
    DELAYED = auto()
    TODO = auto()
    DOING = auto()
    DONE = auto()
    TESTING = auto()
    TESTED = auto()


def status(enum_value: Status):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
