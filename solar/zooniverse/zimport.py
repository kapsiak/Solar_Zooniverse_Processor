import pandas as pd
from pathlib import Path
import json
from .structs import ZRect, ZPoint, ZBool
import math
from solar.common.utils import into_number


def f(x):
    return into_number(x)


def read_class(path):
    im_path = Path(path)
    return pd.read_csv(im_path)


def json_annot(df, index):
    y = df.loc[index, "annotations"]
    return json.loads(y)


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def rectangle_transform(x, y, w, h, angle):
    center = (x + w / 2, y + h / 2)
    x, y = rotate(center, (x, y), angle)
    return {"x": x, "y": y, "w": w, "h": h, "a": angle}


def load_image_info(struct, s_data):
    struct.im_ll_x = f(s_data["#im_ll_x"])
    struct.im_ll_y = f(s_data["#im_ll_y"])
    struct.im_ur_x = f(s_data["#im_ur_x"])
    struct.im_ur_y = f(s_data["#im_ur_y"])
    struct.width = f(s_data["#width"])
    struct.height = f(s_data["#height"])
    return struct


def bool_maker(value, s_data):
    purp = "See_Start"
    if value == "Yes":
        return [ZBool(val=True, purpose=purp)]
    else:
        return [ZBool(val=False, purpose=purp)]


def point_maker(value, s_data):
    return [
        load_image_info(
            ZPoint(
                x=float(v["x"]) / float(s_data["#width"]),
                y= 1 - (float(v["y"]) / float(s_data["#height"])),
                frame=v["frame"],
                purpose=v["tool_label"],
            ),
            s_data,
        )
        for v in value
    ]


def rect_maker(value, s_data):
    ret = []
    for v in value:
        w = v["width"] / float(s_data["#width"])
        h = v["height"] / float(s_data["#height"])
        x = v["x"] / float(s_data["#width"])
        y = (1 - (v["y"] / float(s_data["#height"]))) - h
        a = v["angle"]
        new_dict = rectangle_transform(x, y, w, h, a)
        new_rect = ZRect(**new_dict, frame=v["frame"], purpose=v["tool_label"])
        ret.append(load_image_info(new_rect, s_data))
        ang = math.radians(a)
        c_x, c_y = rotate((x, y), (x + w / 2, y + h / 2), ang)
    return ret


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


def frame_to_fits_data(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    header_data = [json.loads(data[f"#fits_header_{x}"]) for x in range(total_frames)]
    return header_data[frame]


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
        struct.fits_dict = frame_to_fits_data(meta, struct.frame)

    return ret


def load_all(path, row=None):
    if isinstance(row, int):
        df = read_class(path).iloc[row]
        ret = [make_row(df)]
    else:
        df = read_class(path)
        ret = [make_row(df.iloc[x]) for x in range(df.shape[0])]
    return [x for y in ret for x in y]


if __name__ == "__main__":
    d = load_all("solar/zooniverse/class.csv")
    for x in d:
        print(x)
