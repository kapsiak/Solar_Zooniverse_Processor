class Visual_Builder:

    generator_name = "generic_visual"

    def __init__(self, im_type, metadata=None, annotations=(), dpi=300):
        self.extension = im_type
        self.im_ll_x = 0
        self.im_ll_y = 0
        self.im_ur_x = 0
        self.im_ur_y = 0
        self.width = 0
        self.height = 0
        self.dpi = dpi

        self.fig = None
        self.ax = None
        self.map = None

        self.metadata_list = metadata

        self.annotations = list(annotations)

    def add_annotation(self, *annot):
        self.annotations.extend(annot)

    def draw_annotations(self):
        for a in self.annotations:
            a.draw(self.fig, self.ax)

    def generate_metadata(self, fits):
        if self.metadata_list:
            keys = self.metadata_list
        else:
            keys = [x.key for x in fits]

        x = vars(fits)
        data = {
            **x["__data__"],
            **x["__rel__"],
            **{x.key: str(x.value) for x in fits.fits_keys},
        }
        ret = {}
        for key in keys:
            if "." not in key:
                ret.update({key: data[key]})
            else:
                key1, key2 = key.split(".")
                ret.update({key: getattr(data[key1], key2)})
        ret.update(
            {
                x: str(y)
                for x, y in {
                    "im_ll_x": self.im_ll_x,
                    "im_ll_y": self.im_ll_y,
                    "im_ur_x": self.im_ur_x,
                    "im_ur_y": self.im_ur_y,
                    "im_width": self.width,
                    "im_height": self.height,
                    "im_dpi": self.dpi,
                }.items()
            }
        )
        return ret

    def save_visual(self, save_path, clear_after=True):
        pass

    def create(self, file_path):
        pass

    def __hash__(self):
        return hash(
            (
                self.extension,
                self.im_ll_x,
                self.im_ll_y,
                self.im_ur_x,
                self.im_ur_y,
                self.width,
                self.height,
                self.dpi,
                self.map,
            )
        )

    def __dict__(self):
        return {
            "extension": self.extension,
            "im_ll_x": self.im_ll_x,
            "im_ll_y": self.im_ll_y,
            "im_ur_x": self.im_ur_x,
            "im_ur_y": self.im_ur_y,
            "width": self.width,
            "height": self.height,
            "dpi": self.dpi,
        }
