from solar.database.tables.visual_file import Visual_File
from solar.database.tables.solar_event import Solar_Event
from solar.database.tables.fits_file import Fits_File
from solar.visual.img import Basic_Image
from pathlib import Path
import operator
from functools import reduce
import re
import math
from solar.common.utils import into_number
import peewee as pw


def sorter(val):
    l = val[1]
    if l == 1:
        return 1
    if l == 0:
        return -1
    else:
        return 1 / l


def recursive_search(arg, *args, current_search=None):
    """
    Arg and args are a series of strings. This system executes a basic algorithm to narrow the results. Expects to find either a single fits file, or a list of files. Returns None if the function cannot deduce reasonable file(s)
    """
    cols = [
        Solar_Event.id,
        Solar_Event.sol_standard,
        Fits_File.id,
        Fits_File.file_path,
        Fits_File.file_hash,
    ]
    table = Fits_File.select(Solar_Event, Fits_File).join(Solar_Event)
    found = []
    arg = into_number(arg)
    for col in cols:
        q_sub = col.contains(arg) if isinstance(col, pw.CharField) else (col == arg)
        if not current_search:
            q = q_sub
        else:
            q = current_search & q_sub
        search = table.where(q)
        found.append([q, search.count()])
    found = sorted(found, key=sorter, reverse=True)
    if all(x[1] == 0 for x in found) or not found:
        return None
    if not args:
        return table.where(found[0][0])
    return recursive_search(*args, current_search=found[0][0])


def parse_v(args):
    if args.type:
        if args.type in ["image", "img", "im"]:
            v_type = "image"
            extension = "png"
        elif args.type in ["video", "vid"]:
            v_type = "video"
            extension = "mp4"
    else:
        if args.extension in ["mp4", "gif"]:
            v_type = "video"
        else:
            v_type = "image"
        extension = args.extension

    found = recursive_search(*args.search)
    exp = args.export
    if not found:
        print("Didn't find anything")
        return None
    if found.count() > 1 and v_type != 'video':
        raise ValueError

    if v_type == 'image':
        im = im_maker(found, extension)
        if exp:
            im.export(exp)

    if v_type == 'video':
        pass

def vid_maker(fits,ext):
    pass

def im_maker(fits,ext):
    fits = fits.get()
    fits.update_single()
    bi = Basic_Image(ext)
    im = Visual_File.create_new_visual(fits, bi)
    return im


def make_v_parser(command_parser):
    visual_parser = command_parser.add_parser(
        "visual", help="Construct visuals from existing fits files"
    )
    visual_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch the interactive image builder.",
    )

    visual_parser.add_argument("--list", action="store_true")

    group1 = visual_parser.add_mutually_exclusive_group(required=True)
    group1.add_argument(
        "--extension",
        default="png",
        type=str,
        help="The extension to use for the genenerated image",
    )
    group1.add_argument("--type", default="image", type=str)

    visual_parser.add_argument(
        "-e", "--export", type=str, help="Location to export the image to"
    )

    visual_parser.add_argument(
        "search", help="The files from which the visuals will generated", nargs="+"
    )

    visual_parser.set_defaults(func=parse_v)
