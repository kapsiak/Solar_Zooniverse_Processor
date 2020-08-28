class Visual_Builder:

    generator_name = "generic_visual"

    def __init__(self, im_type, metadata=None, annotations=(), dpi=300):
        """
        :param im_type: The extension of the image (ie jpeg, mp4, png, ...)
        :type im_type: str
        :param metadata: What metadata to append add to the generated image, defaults to None
        :type metadata: dict
        :param annotations: Annotations to be added to the image, defaults to ()
        :type annotations: List[Annot]
        :param dpi: The dpi of the generated image, defaults to 300
        :type dpi: int
        """
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
        """Function add_annotation: 

        Add annotations to this visual
        
        :param annot: Annotation objects
        :type annot: subclass of Annot
        :returns: None
        :type return: None
        """
        self.annotations.extend(annot)

    def draw_annotations(self):
        """Function draw_annotations: 
        Draw the annotations stored in this object
        """
        for a in self.annotations:
            a.draw(self.fig, self.ax)

    def generate_metadata(self, fits):
        """
        This function should probably be moved, as it actually doesn't fit well in this class
        """
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
        """
        Useful when using dbformat
        """
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
