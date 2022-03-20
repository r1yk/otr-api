from typing import List


class Settable():
    """
    A simple mixin that assigns the values of any kwargs as class attributers.
    """

    def __init__(self, *args, **properties):
        if properties:
            for property in properties.keys():
                setattr(self, property, properties.get(property))


def get_key_value_pairs(items: List[any], key: str, value: str = None, strict: bool = False) -> dict:
    key_value_pairs = {}
    for item in items:
        if hasattr(item, key) and (not strict or hasattr(item, value)):
            key_value_pairs[getattr(item, key)] = getattr(
                item, value) if value else item
        else:
            raise AttributeError(item)
    return key_value_pairs


def get_name_to_id(rows: List[any]) -> dict:
    return get_key_value_pairs(key='name', value='id', items=rows, strict=True)


def get_name_to_self(rows: List[any]) -> dict:
    return get_key_value_pairs(items=rows, key='name')
