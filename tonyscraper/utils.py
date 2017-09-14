import os
from typing import Optional


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
