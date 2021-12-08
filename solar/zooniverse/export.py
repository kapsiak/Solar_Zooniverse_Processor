import csv
from pathlib import Path
from itertools import chain


def zooniverse_export(*files, export_dir="export", existing_csv=None):
    """Function zooniverse_export: Export a list of lists of lists of visual_files
    
    :param files: The list of files
    :type files: List[List[List[Visual_File]]]
    :param export_dir: The directory to export to , defaults to "export"
    :type export_dir: Path-like
    :param existing_csv: whether to append to an existing csv, defaults to None (! NOT CURRENTLY USED)
    :type existing_csv: bool
    :returns: None
    :type return: None


    Files is 

     [

    subject_2 ->   [[file1, file2,...] ,[file_1,file_2,...]] 

    subject 1->   ,[[file1, file2,...] ,[file_1,file_2,...]]

    ]
    """
    export = Path(export_dir)
    files_dir = export
    files_dir.mkdir(exist_ok=True, parents=True)
    data = [__prepare_row(x) for event in files for x in event]
    header = [x for x in data[0]]
    with open(export / "meta.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
#Write seperate csv file meta_reduced.csv for export to zooniverse Panoptes
    data = [__prepare_row(x,reduced=True) for event in files for x in event]
    header = [x for x in data[0]]
    with open(export / "meta_reduced.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(set([z for x in files for y in x for z in y]))
    for f in set([z for x in files for y in x for z in y]):
        f.export(export)


def __prepare_row(files,reduced=False):
    """
    Prepare a list of visual files for export.
    
    :param files: The collection of visual files
    :type files: List[Visual_File]
    :returns: A dictionary of csv data {Header : Value} 
    :type return: dict
    """

    file_names = ["file_name_{}".format(x) for x in range(len(files))]
    fits_db_id_names = ["fits_db_{}".format(x) for x in range(len(files))]
    vis_db_id_names = ["vis_db_{}".format(x) for x in range(len(files))]
    checksums = ["checksum_{}".format(x) for x in range(len(files))]

    fits_header_names = ["fits_header_{}".format(x) for x in range(len(files))]

    file_info = {f: val for f, val in zip(file_names, [x.file_name for x in files])}

    print(file_info)

    check_info = {
        check: val for check, val in zip(checksums, [x.file_hash for x in files])
    }

    fits_db_id = {
        f: val
        for f, val in zip(
            fits_db_id_names, [name.fits_join.get().fits_file.id for name in files]
        )
    }
    vis_db_id = {f: val for f, val in zip(vis_db_id_names, [name.id for name in files])}

    fits_header_info = {
        col: header
        for col, header in zip(
            fits_header_names,
            [name.fits_join.get().fits_file.get_header_as_json() for name in files],
        )
    }

    image = files[0]
    try:
        sol_standard = image.fits_join.get().fits_file.event.sol_standard
    except Exception:
        sol_standard = ""
    try:
        ssw_id = image.fits_join.get().fits_file.service_request.job_id
    except Exception:
        ssw_id = ""
    try:
        event_db_id = image.fits_join.get().fits_file.event.id
    except Exception:
        event_db_id = ""

    uniform = {
        "frame_per_sub": len(files),
        "event_db_id": event_db_id,
        "sol_standard": sol_standard,
        "ssw_id": ssw_id,
        "visual_type": image.visual_type,
        "description": image.description,
        "im_ll_x": image.im_ll_x,
        "im_ll_y": image.im_ll_y,
        "im_ur_x": image.im_ur_x,
        "im_ur_y": image.im_ur_y,
        "width": image.width,
        "height": image.height,
    }
    new_row = {
        **file_info,
        # **check_info,
        **fits_db_id,
        **vis_db_id,
        **uniform,
        **fits_header_info,
    }
    if reduced==True:
        new_row = {
            **file_info,
            #**check_info,
            **fits_db_id,
            **vis_db_id,
            **uniform,
            #**fits_header_info,
    }

    new_row = {"#" + x: y for x, y in new_row.items()}
    return new_row


def split(values, size, overlap=2):
    """Function split: Break an iterable into lists of lenth size with list overlap 'overlap'
    
    :param values: The list of values to splot
    :type values: iterable
    :param size: The length of each list
    :type size: int
    :param overlap: The overlap of list, defaults to 2
    :type overlap: int
    :returns: A list of the generated lists
    :type return: List[List]

    Example: split([1,2,3,4,5,6,7,8,9,10], 4, 2]) -> [[1,2,3,4] ,[3,4,5,6], [6,7,8,9], [7,8,9,10]]

    Notice that the last list has an overlap appropriate to ensure that it if of length size
    """
    step = size - overlap
    new = [values[i : i + size] for i in range(0, len(values) - overlap, step)]
    if len(new[-1]) < size:
        new[-1] = values[-size:]
    if new[-1] == new[-2]:
        new = new[:-1]
    return new


if __name__ == "__main__":
    A = list(range(0, 15))
    s = split(A, 6, 3)
    print(s)
