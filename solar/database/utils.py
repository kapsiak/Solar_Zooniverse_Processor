from __future__ import annotations
from typing import List, Dict, Any
from solar.common.config import Config
from pathlib import Path


def format_string(format_string: str, row: object, **kwargs) -> str:
    """
    Helper method to format a string given a database model instance.

    :param format_string: The string describing the format
    :type format_string: str
    :param row: The model instance
    :type row: object
    :param kwargs: Other formatting keys
    :return: The formatted string
    :rtype: str
    """
    return format_string.format(**row.__data__, **kwargs)


def prepend_root(path: Union[Path, str]) -> str:
    """
    Prepend the file save path and return the new path

    :param path: Original path
    :type path: Union[Path, str]
    :return: the path with the database save file prepended
    :rtype: str
    """
    return str(Path(Config["file_save_path"]) / path)
