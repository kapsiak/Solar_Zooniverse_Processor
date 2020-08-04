from __future__ import annotations
from typing import List, Dict, Any
from solar.common.config import Config
from pathlib import Path
from functools import wraps
import inspect


def dbformat(format_string: str, *args, **kwargs) -> str:
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
    if args:
        to_pass = {}
        for x in reversed(args):
            if hasattr(x, "__data__"):
                to_pass.update(dict(x.__data__))
            else:
                to_pass.update(x.__dict__())

        for k in kwargs:
            to_pass[k] = kwargs[k]

        return format_string.format(**to_pass)
    else:
        return format_string.format(**kwargs)


def dbpathformat(fname, fpath, *args, **kwargs):
    return dbroot(
        dbformat(fpath, *args, ffilename=dbformat(fname, *args, **kwargs), **kwargs)
    )


def dbroot(path):
    new_path = Path(Config.db_save) / path
    return new_path
