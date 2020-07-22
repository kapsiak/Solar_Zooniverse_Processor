from solar.database.tables.visual_file import Visual_File
from solar.database.tables.hek_event import Hek_Event
from solar.database.tables.fits_file import Fits_File
from solar.common.utils import into_number
import solar.visual as vis
import peewee as pw
from typing import List, Any


Img_Factories = {x.__name__.lower(): x for x in vis.Img_Factories}
Vid_Factories = {x.__name__.lower(): x for x in vis.Vid_Factories}


def sorter(val: List[List[Any]]) -> int:
    """
    Returns a value between 0 and 1, with values closer to 1 being mapped to larger values (with one being the max). 
    Zero is eliminated by giving it a negative value

    :param val: A value in a list
    :type val: List[Any, int]
    :return: The ranking
    :rtype: int
    """
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

    search_cols = [
        Hek_Event.id,
        Hek_Event.sol_standard,
        Fits_File.id,
        Fits_File.file_path,
        Fits_File.file_hash,
    ]

    table = Fits_File.select(Hek_Event, Fits_File).join(Hek_Event)

    found = []

    arg = into_number(arg)
    for col in search_cols:
        # We search string "fuzzily" and numbers exactly
        query_subpart = (
            col.contains(arg) if isinstance(col, pw.CharField) else (col == arg)
        )
        if not current_search:
            query = query_subpart
        else:
            query = current_search & query_subpart
        results = table.where(query)
        found.append([query, results.count()])
    found = sorted(found, key=sorter, reverse=True)
    if all(x[1] == 0 for x in found) or not found:
        return None
    if not args:
        return table.where(found[0][0])
    return recursive_search(*args, current_search=found[0][0])


def make_im_factory(name, *args, **kwargs):
    name = name.lower()
    return Img_Factories[name](*args, **kwargs)


def make_vid_factory(name, *args, **kwargs):
    name = name.lower()
    return Vid_Factories[name](*args, **kwargs)


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
    factory = (
        args.factory
        if args.factory
        else {"video": "basic_video", "image": "basic_image"}[v_type]
    )
    if not found:
        print("Didn't find anything")
        return None
    if found.count() > 1 and v_type != "video":
        raise ValueError

    if v_type == "image":
        im = im_maker(found, make_im_factory(factory, extension))
        if exp:
            im.export(exp)

    if v_type == "video":
        im = vid_maker(found, make_vid_factory(factory, extension))
        if exp:
            im.export(exp)


def vid_maker(fits, factory):
    for f in fits:
        f.update_single()
    im = Visual_File.create_new_visual(fits, factory)
    return im


def im_maker(fits, factory):
    fits = fits.get()
    fits.update_single()
    im = Visual_File.create_new_visual(fits, factory)
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
        "-f",
        "--factory",
        type=str,
        help=f"The 'miniprogram' used to make the image for images the available builders are {', '.join(list(Img_Factories.keys())+ list(Vid_Factories.keys()))}.",
    )

    visual_parser.add_argument(
        "search", help="The files from which the visuals will generated", nargs="+"
    )

    visual_parser.set_defaults(func=parse_v)
