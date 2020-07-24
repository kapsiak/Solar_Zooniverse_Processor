from dataclasses import dataclass
from astropy.coordinates import SkyCoord
import json


@dataclass()
class ZBase:
    subject_id: int = 0
    user_id: int = 0
    workflow_id: int = 0
    class_id: int = 0

    fits_id: int = -1
    visual_id: int = -1
    frame: int = -1

    purpose: str = None


@dataclass
class ZBool(ZBase):
    val: bool = False


@dataclass
class ZRect(ZBase):
    x: float = -1
    y: float = -1
    w: float = -1
    h: float = -1
    a: float = -1

    def to_space(self):
        pass


@dataclass
class ZPoint(ZBase):
    x: float = -1
    y: float = -1


def bool_maker(value):
    purp = "See_Start"
    if value == "Yes":
        return [ZBool(val=True, purpose=purp)]
    else:
        return [ZBool(val=False, purpose=purp)]


def point_maker(value):
    return [
        ZPoint(x=v["x"], y=v["y"], frame=v["frame"], purpose=v["tool_label"])
        for v in value
    ]


def rect_maker(value):
    return [
        ZRect(
            x=v["x"],
            y=v["y"],
            w=v["width"],
            h=v["height"],
            a=v["angle"],
            frame=v["frame"],
            purpose=v["tool_label"],
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
    task_data = json.loads(z_row.loc["annotations"])

    ret = [task_allocator[t["task"]](t["value"]) for t in task_data]
    ret = [x for y in ret for x in y]
    for struct in ret:
        struct.subject_id = sid
        struct.user_id = uid
        struct.workflow_id = wid
        struct.class_id = cid
        struct.visual_id = frame_to_visid(meta, struct.frame)
        struct.fits_id = frame_to_fid(meta, struct.frame)

    return ret
