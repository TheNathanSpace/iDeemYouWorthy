from logging import Logger
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
        original_path = original_path.replace(char, '_')

    return original_path


def shorten_android_path(file_path: Path, logger: Logger):
    file_name = file_path.name
    file_parent = file_path.parent.name
    windows_root = "This PC/12345678901234567890/Internal shared storage/Music/music/"

    combined_path = windows_root + file_parent + "/" + file_name
    if not len(combined_path) >= 260:
        return None

    stem = file_path.stem

    announce = True
    while len(combined_path) >= 260:
        if announce:
            logger.info("Renaming file: " + file_parent + "/" + file_name)
            announce = False

        if len(stem) == 1:
            # Should probably throw out some error message "bruh this isn't gonna work out waaaay too long"
            return None

        extension = file_path.suffix
        stem = stem[:-1]

        file_name = stem + extension
        combined_path = windows_root + file_parent + "/" + file_name

    new_path = file_path.parent / file_name
    try:
        file_path.rename(new_path)
    except Exception as e:
        logger.error("Couldn't rename file!")
        logger.error(e)
        return None

    return new_path
