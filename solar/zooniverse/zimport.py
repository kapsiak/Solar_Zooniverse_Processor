import pandas as pd
from pathlib import Path
import json
from .structs import ZRect, ZPoint, ZBool
import math
from solar.common.utils import into_number
from numpy.linalg import norm


def load_all(path, row=None):
    """Function load_all: Load an entire csv file an get all the classifications as python structures
    
    :param path: The path to the csv
    :type path: Path-like
    :param row: If given, work on only a single row, defaults to None
    :type row: int
    :returns: A list of all the classification as :class:`~solar.zooniverse.structs.ZBase`.
    :type return: List[:class:`~solar.zooniverse.structs.ZBase`]
    """
    if isinstance(row, int):
        df = __read_class(path).iloc[row]
        ret = [__make_row(df)]
    else:
        df = __read_class(path)
        ret = [__make_row(df.iloc[x]) for x in range(df.shape[0])]
    return [x for y in ret for x in y]


def f(x):
    return into_number(x)


def __read_class(path):
    """Function __read_class: Read a zooniverse classification file 
    
    :param path: The location of the file
    :type path: Path-like
    :returns: pandas dataframe containing the data
    :type return: pd.dataframe
    """
    im_path = Path(path)
    return pd.read_csv(im_path)


def json_annot(df, index):
    y = df.loc[index, "annotations"]
    return json.loads(y)


def __rotate(origin, point, angle):
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


def __rectangle_transform(x, y, w, h, angle):
    """Function __rectangle_transform: Convert a rectangle from x,y,w,h as given by the zooniverse classification file to 
    x,y,w,h as needed for this program. 
    
    :returns: Transformed rectangle coordinates
    :type return: dict
    """
    center = (x + w / 2, y + h / 2)
    # x, y = __rotate(center, (x, y), angle)
    return {"x": x, "y": y, "w": w, "h": h, "a": angle}


def load_image_info(struct, s_data):
    """Function load_image_info: Load the image data from zooniverse classification and add it to struct
    
    :param struct: The struct to add the data to
    :type struct: ZStruct
    :param s_data: Dictionary containing the data required to describe the image
    :type s_data: dict-like
    :returns: The structure with the data appended
    :type return: ZStruct
    """
    struct.im_ll_x = f(s_data["#im_ll_x"])
    struct.im_ll_y = f(s_data["#im_ll_y"])
    struct.im_ur_x = f(s_data["#im_ur_x"])
    struct.im_ur_y = f(s_data["#im_ur_y"])
    struct.width = f(s_data["#width"])
    struct.height = f(s_data["#height"])
    return struct


def bool_maker(value, s_data):
    """Function bool_maker: Create a ZBool from the subject data
    
    :param value: the value of the boolean (True or False)
    :type value: bool
    :param s_data: Dictionary containing the zooniverse subject data
    :type s_data: dict
    :returns: A list of the created booleans
    :type return: List[ZBool]
    """
    purp = "See_Start"
    if value == "Yes":
        return [ZBool(val=True, purpose=purp)]
    else:
        return [ZBool(val=False, purpose=purp)]


def point_maker(value, s_data):
    """Function point_maker: Create a ZPoint from the subject data
   
    :param value: The values from the universe classification
    :type value: dict
    :param s_data: Dictionary containing the zooniverse subject data
    :type s_data: dict
    :returns: A list of the created Point
    :type return: List[ZPoint]
    """
    return [
        load_image_info(
            ZPoint(
                x=float(v["x"]) / float(s_data["#width"]),
                y=1 - (float(v["y"]) / float(s_data["#height"])),
                frame=v["frame"],
                purpose=v["tool_label"],
            ),
            s_data,
        )
        for v in value
    ]


def rect_maker(value, s_data):
    """Function rect_maker: Create a ZRect from the subject data
   
    :param value: The values from the universe classification
    :type value: dict
    :param s_data: Dictionary containing the zooniverse subject data
    :type s_data: dict
    :returns: A list of the created rect
    :type return: List[ZRect]
    """
    ret = []
    for v in value:
        w = v["width"] / float(s_data["#width"])
        h = v["height"] / float(s_data["#height"])
        x = v["x"] / float(s_data["#width"])
        y = (1 - (v["y"] / float(s_data["#height"]))) - h
        a = v["angle"]
        x = x + w / 2
        y = y + h / 2
        ret.append(ZPoint(x=x + w / 2, y=y + h / 2))
        new_dict = __rectangle_transform(x, y, w, h, a)
        new_rect = ZRect(**new_dict, frame=v["frame"], purpose=v["tool_label"])
        ret.append(load_image_info(new_rect, s_data))
        ret.append(ZPoint(x=new_dict["x"], y=new_dict["y"]))
    return ret


#: This dict tells us which factory to use based on the 'tool' value
task_allocator = {
    "T0": bool_maker,
    "T1": point_maker,
    "T2": point_maker,
    "T3": rect_maker,
}


# The following three functions use the frame to get different data from the classification file
def __frame_to_visid(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    frames = [data[f"#vis_db_{x}"] for x in range(total_frames)]
    return frames[frame]


def __frame_to_fid(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    frames = [data[f"#fits_db_{x}"] for x in range(total_frames)]
    return frames[frame]


def __frame_to_fits_data(meta, frame):
    data = next(iter(meta.items()))[1]
    total_frames = int(data["#frame_per_sub"])
    header_data = [json.loads(data[f"#fits_header_{x}"]) for x in range(total_frames)]
    return header_data[frame]


def __make_row(z_row):
    """Function __make_row: Create a list of zooniverse data structs from a given classification
    
    :param z_row: A row if the zooniverse csv file
    :type z_row: pd.dataframe
    :returns: A list of all the structs contained in that classification
    :type return: List[ZStruct]
    """
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
        struct.visual_id = __frame_to_visid(meta, struct.frame)
        struct.fits_id = __frame_to_fid(meta, struct.frame)
        struct.fits_dict = __frame_to_fits_data(meta, struct.frame)

    return ret


if __name__ == "__main__":
    d = load_all("solar/zooniverse/class.csv")
    for x in d:
        print(x)
