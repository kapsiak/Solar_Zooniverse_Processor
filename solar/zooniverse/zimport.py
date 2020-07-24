import pandas as pd
from pathlib import Path
import json
from .structs import make_row


def read_class(path):
    im_path = Path(path)
    return pd.read_csv(im_path)


def json_annot(df, index):
    y = df.loc[index, "annotations"]
    return json.loads(y)


def load_all(path):
    df = read_class(path)
    ret = [make_row(df.iloc[x]) for x in range(df.shape[0])]
    return [x for y in ret for x in y]


if __name__ == "__main__":
    d = load_all("zooniverse/class.csv")
    for x in d:
        print(x)
