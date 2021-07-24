from pathlib import Path


def dict_to_set(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(key)
    return returned_set


def dict_to_set_values(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(dict_to_convert[key])
    return returned_set


def clean_path(original_path):
    if not isinstance(original_path, Path):
        original_path = Path(original_path)

    child_to_clean = original_path.name

    invalid_chars = '\/:*?"<>|'
    for char in invalid_chars:
        child_to_clean = child_to_clean.replace(char, '')

    cleaned_path = original_path.parent / child_to_clean

    return cleaned_path


def clean_path_child(original_path):
    invalid_chars = '\/:*?"<>|'
    for char in invalid_chars:
        original_path = original_path.replace(char, '')

    return original_path
