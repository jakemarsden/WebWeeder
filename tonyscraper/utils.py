import json
import os
from datetime import date, datetime, timedelta
from typing import List, Optional, Set

BYTES: int = 1
KILOBYTES: int = (1024 * BYTES)
MEGABYTES: int = (1024 * KILOBYTES)
GIGABYTES: int = (1024 * MEGABYTES)
TERABYTES: int = (1024 * GIGABYTES)


def find_duplicates(test_list: List[object]) -> Set[object]:
    """
    :param test_list:
    :return: The set of items in the given list which were present more than once
    """
    duplicates = list(test_list)
    uniques = set(test_list)
    for unique in uniques:
        duplicates.remove(unique)  # Only removes first matching
    return set(duplicates)


def date_range(start: date, end: date = date.today()) -> List[date]:
    """
    :param start:
    :param end:
    :return: Every possible date between start and end, inclusive
    """
    delta = (end - start)
    return [(start + timedelta(days=i)) for i in range(delta.days + 1)]


def read_text_file(file_path: str, missing_ok: bool = True) -> Optional[str]:
    """
    :param file_path:
    :param missing_ok: If the file doesn't exist and this is set to True, the None will be returned. Otherwise, a
    FileNotFoundError will be thrown.
    :return:
    """
    if missing_ok:
        if not os.path.isfile(file_path):
            return None
    with open(file_path, 'r') as file:
        return file.read()


def write_text_file(file_path: str, content: str, create_parents: bool = True):
    """
    :param file_path:
    :param content:
    :param create_parents: If the file's parent directory doesn't exist and this is set to True, it will be created.
    Otherwise, a FileNotFoundError will be thrown.
    :return:
    """
    if create_parents:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(content)


def delete_directory(dir_path: str, preserve_dir: bool = False, missing_ok: bool = True):
    """
    Removes the specified directory recursively if it exists
    :param preserve_dir: Set to True to preserve the top-level directory
    :param dir_path: The path of the directory to delete
    :param missing_ok: If the specified directory doesn't exist and this is False, a FileNotFoundError will be thrown.
    :return:
    """
    if not os.path.exists(dir_path):
        if not missing_ok:
            raise FileNotFoundError
        return
    else:
        if not os.path.isdir(dir_path):
            raise FileNotFoundError  # It's a file?

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)
        else:
            delete_directory(item_path, preserve_dir=False, missing_ok=False)

    if not preserve_dir:
        os.rmdir(dir_path)


class DateTimeAwareJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        try:
            return super().default(obj)
        except TypeError:
            return obj.__dict__
