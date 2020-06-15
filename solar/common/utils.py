import hashlib
from pathlib import Path


def checksum(string, hash_factory=hashlib.md5, chunk_num_blocks=128):
    h = hash_factory()
    if Path(string).is_file():
        with open(string, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_num_blocks * h.block_size), b""):
                h.update(chunk)
        return h.hexdigest()
    else:
        h.update(string.encode("utf-8"))
        return h.hexdigest()


def into_number(string):
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string
