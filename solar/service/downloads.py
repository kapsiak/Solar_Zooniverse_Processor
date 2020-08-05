import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm
from pathlib import Path


def download_single_file(url, save_path):
    """
    Download a file from a url.

    :param url: The url where the file is stored
    :type url: str
    :param save_path: The same location
    :type save_path: Union[str,Path]
    """
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
    """
    Download multiple files concurrently

    :param download_struct: A structure describing the desired download
    :type download_struct: Dict[str,Union[str,Path]]
    """
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(download_single_file, url, download_struct[url])
            for url in download_struct
        ]
        for _ in tqdm.tqdm(
            as_completed(futures), total=len(futures), desc="Downloading fits files"
        ):
            pass
