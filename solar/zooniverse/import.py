import pandas as pd
from pathlib import Path


def read_class(path):
    im_path = Path(path)
    return pd.read_csv(im_path)


x = read_class("test-classifications-1.csv")
