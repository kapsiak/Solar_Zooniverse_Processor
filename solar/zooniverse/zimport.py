import pandas as pd
from pathlib import Path
import json
from .structs import ZRect, ZPoint, ZBool


def read_class(path):
    im_path = Path(path)
    return pd.read_csv(im_path)


def json_annot(df, index):
    y = df.loc[index, "annotations"]
    return json.loads(y)


def bool_maker(value, s_data):
    purp = "See_Start"
    if value == "Yes":
        return [ZBool(val=True, purpose=purp)]
    else:
        return [ZBool(val=False, purpose=purp)]


def point_maker(value, s_data):
    return [
        ZPoint(x=v["x"], y=v["y"], frame=v["frame"], purpose=v["tool_label"]).scale(
            s_data["#width"], s_data["#height"]
        )
        for v in value
    ]


def rect_maker(value, s_data):
    return [
        ZRect(
            x=v["x"],
            y=v["y"],
            w=v["width"],
            h=v["height"],
            a=v["angle"],
            frame=v["frame"],
            purpose=v["tool_label"],
        ).scale(
            s_data["#width"], s_data["#height"]
        )
        for v in value
    ]


task_allocator = {
    "T0": bool_maker,
    "T1": point_maker,
    "T2": point_maker,
    "T3": rect_maker,
}


def frame_to_visid(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    frames = [data[f"#vis_db_{x}"] for x in range(total_frames)]
    return frames[frame]


def frame_to_fid(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    frames = [data[f"#fits_db_{x}"] for x in range(total_frames)]
    return frames[frame]


def make_row(z_row):
    uid = z_row.loc["user_id"]
    cid = z_row.loc["classification_id"]
    wid = z_row.loc["workflow_id"]
    sid = z_row.loc["subject_ids"]
    meta = json.loads(z_row.loc["subject_data"])
    s_data = next(iter(meta.items()))[1]
    task_data = json.loads(z_row.loc["annotations"])

    ret = [task_allocator[t["task"]](t["value"], s_data) for t in task_data]
    ret = [x for y in ret for x in y]
    for struct in ret:
        struct.subject_id = sid
        struct.user_id = uid
        struct.workflow_id = wid
        struct.class_id = cid
        struct.visual_id = frame_to_visid(meta, struct.frame)
        struct.fits_id = frame_to_fid(meta, struct.frame)

    return ret


def load_all(path):
    df = read_class(path)
    ret = [make_row(df.iloc[x]) for x in range(df.shape[0])]
    return [x for y in ret for x in y]


if __name__ == "__main__":
    d = load_all("solar/zooniverse/class.csv")
    for x in d:
        print(x)
