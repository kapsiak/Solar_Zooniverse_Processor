import hashlib
from pathlib import Path
from typing import Union


def checksum(
    string: Union[str, Path], hash_factory=hashlib.md5, chunk_num_blocks: int = 128
) -> str:
    """
    A simple checksum function.

    :param string: Checks is string is a file path, and, if so, returns a md5 checksum on the file contents. 
    If string is not a path, simply checksums the string
    :type string: Union[str, Path]
    :param hash_factory: The hasing function, defaults to hashlib.md5
    :type hash_factory: optional
    :param chunk_num_blocks: Number of chunks to read, defaults to 128
    :type chunk_num_blocks: int, optional
    :return: checksum      
    :rtype: str
    """
    h = hash_factory()
    if Path(string).is_file():
        with open(string, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_num_blocks * h.block_size), b""):
                h.update(chunk)
        return h.hexdigest()
    else:
        h.update(string.encode("utf-8"))
        return h.hexdigest()


def into_number(string: str) -> Union[float, int, str]:
    """
    Basic function to cast a string into an int, float, or str.

    :param string: The string
    :type string: str
    :return: Either an int, float or string
    :rtype: Union[float, int, str]
    """
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string
