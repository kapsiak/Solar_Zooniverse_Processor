import matplotlib.patches as patches
from matplotlib.transforms import IdentityTransform
from functools import wraps
import matplotlib.transforms as tr

class Annot:
    def draw(self, fig, ax):
        raise NotImplementedError

    @staticmethod
    def to_annot(struct, **kwargs):
        """TODO: Docstring for to_annot.

        :param struct: TODO
        :returns: TODO

        """

        rect_attr = ["x", "y", "w", "h", "a"]
        point_attr = ["x", "y"]

        if all([hasattr(struct, att) for att in rect_attr]):
            return Rect_Annot(
                struct.x, 1 - struct.y, struct.w, struct.h, struct.a, **kwargs
            )

        if all([hasattr(struct, att) for att in point_attr]):
            return Circle_Annot(struct.x, 1 - struct.y, **kwargs)

        try:
            if len(struct) == 2:
                return Circle_Annot(struct[0], struct[1], **kwargs)
            if len(struct) == 5:
                return Rect_Annot(
                    struct[0], struct[1], struct[2], struct[3], struct[4], **kwargs
                )
        except Exception:
            pass

        return None


class Rect_Annot(Annot):

    """Docstring for Rect_annot. """

    def __init__(self, x, y, w, h, a, **kwargs):
        """TODO: to be defined.

        :param x: TODO
        :param y: TODO
        :param w: TODO
        :param h: TODO
        :param a: TODO

        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.a = a
        self.props = kwargs

    def draw(self, fig, ax):
        new = (self.x, self.y)
        rect = patches.Rectangle(
            new,
            self.w,
            self.h,
            angle=0,
            fill=False,
            transform=tr.Affine2D().rotate(self.a) * fig.transFigure,
            **self.props
        )
        fig.patches.append(rect)


class Circle_Annot(Annot):

    """Docstring for Rect_annot. """

    def __init__(self, x, y, r=10, **kwargs):
        """TODO: to be defined.

        :param x: TODO
        :param y: TODO
        :param w: TODO
        :param h: TODO
        :param a: TODO

        """
        self.x = x
        self.y = y
        self.r = r
        self.props = kwargs

    def draw(self, fig, ax):
        new = tuple(fig.transFigure.transform((self.x, self.y)))
        new_r = fig.transFigure.transform((self.r, self.r))
        print(new)
        circ = patches.Circle(
            new,
            radius=self.r,
            fill=True,
            transform=None,
            # fig.transFigure,
            **self.props
        )
        fig.patches.append(circ)
