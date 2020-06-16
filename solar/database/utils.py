from solar.common.config import Config
from pathlib import Path


def format_string(format_string, row, **kwargs):
    return format_string.format(**row.__data__, **kwargs)


def prepend_root(path):
    return str(Path(Config["file_save_path"]) / path)
