import requests
from concurrent.futures import ThreadPoolExecutor
import tqdm
from pathlib import Path


def download_single_file(url, save_path):
    p = Path(save_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True) as r:
        with open(p, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    with open(p, "rb") as r:
        h = hash(r.read())
    return h


def multi_downloader(download_struct):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(download_single_file, url, download_struct[url])
            for url in download_struct
        ]
