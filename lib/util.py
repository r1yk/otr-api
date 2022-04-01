from typing import List
from sqlalchemy import inspect


class Settable():
    """
    A simple mixin that assigns the values of any kwargs as class attributers.
    """

    def __init__(self, *args, **properties):
        if properties:
            for property in properties.keys():
                setattr(self, property, properties.get(property))


def get_key_value_pairs(items: List[any], key: str, value: str = None, strict: bool = False) -> dict:
    """
    Accept a list of database rows, and return a mapping from the value in the `key` column
    to the value in the `value` column.
    """
    key_value_pairs = {}
    for item in items:
        if hasattr(item, key) and (not strict or hasattr(item, value)):
            key_value_pairs[getattr(item, key)] = getattr(
                item, value) if value else item
        else:
            raise AttributeError(item)
    return key_value_pairs


def get_name_to_id(rows: List[any]) -> dict:
    """Accept a list of database rows, and return a mapping from their name to their ID."""
    return get_key_value_pairs(key='name', value='id', items=rows, strict=True)


def get_name_to_self(rows: List[any]) -> dict:
    """Accept a list of database rows, and return a mapping from their name to themselves."""
    return get_key_value_pairs(items=rows, key='name')


def get_changes(model) -> dict:
    """
    Return a dictionary containing changes made to the model since it was 
    fetched from the database.
    """
    state = inspect(model)
    changes = {}
    for attr in state.attrs:
        hist = state.get_history(attr.key, True)

        if not hist.has_changes():
            continue

        old_value = hist.deleted[0] if hist.deleted else None
        new_value = hist.added[0] if hist.added else None
        changes[attr.key] = (old_value, new_value)

    return changes
