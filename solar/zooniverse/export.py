import csv
from pathlib import Path


def zooniverse_export(files, export_dir="export"):
    export = Path("export")
    files_dir = export
    files_dir.mkdir(exist_ok=True, parents=True)
    data = [prepare_row(x) for x in files]
    header = [x for x in data[0]]
    print(header)
    with open(export / "meta.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    for f in set([x for y in files for x in y]):
        f.export(export)


def prepare_row(files, export_dir="export"):
    files_dir = Path(export_dir)
    files_dir.mkdir(exist_ok=True, parents=True)
    data = [[], []]
    file_names = ["file_name_{}".format(x) for x in range(len(files))]
    checksums = ["checksum_{}".format(x) for x in range(len(files))]
    header = [
        *file_names,
        "sol_standard",
        "visual_type",
        "description",
        "im_ll_x",
        "im_ll_y",
        "im_ur_x",
        "im_ur_y",
        "width",
        "height",
        *checksums,
    ]
    file_info = {f: val for f, val in zip(file_names, [x.file_name for x in files])}
    check_info = {
        check: val for check, val in zip(checksums, [x.file_hash for x in files])
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

    uniform = {
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
    new_row = {**file_info, **check_info, **uniform}
    return new_row


def split(values, size, overlap=2):
    step = size- overlap
    new = [values[i:i+size] for i in range(0, len(values)-overlap, step)]
    if len(new[-1]) < size:
        new[-1] = values[-size:]
    if new[-1] == new[-2]:
        new = new[:-1]
    return new


if __name__ == "__main__":
    A = list(range(0, 15))
    s = split(A, 6,3 )
    print(s)
