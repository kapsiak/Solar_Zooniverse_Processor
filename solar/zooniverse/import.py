import pandas as pd
from pathlib import Path
import json


def read_class(path):
    im_path = Path(path)
    return pd.read_csv(im_path)


def json_annot(df, index):
    y = x.loc[index, "annotations"]
    return json.loads(y)


x = read_class("test-classifications-1.csv")
y = json_annot(x, 9)
print(x)
print(y)
print(x.loc[1, "subject_data"])
