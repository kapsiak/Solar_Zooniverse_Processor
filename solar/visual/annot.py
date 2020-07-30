import matplotlib.patches as patches
from matplotlib.transforms import IdentityTransform
from functools import wraps
import matplotlib.transforms as tr


def prop_trans(fig, point, angle):
    return fig.transFigure + tr.Affine2D().rotate_deg_around(
        *fig.transFigure.transform(point), angle
    )


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
                struct.x, struct.y, struct.w, struct.h, struct.a, **kwargs
            )

        if all([hasattr(struct, att) for att in point_attr]):
            return Circle_Annot(struct.x, struct.y, **kwargs)

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
            transform=prop_trans(fig, new, self.a),
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
        new = fig.transFigure.transform((self.x, self.y))
        circ = patches.Circle(
            new, radius=self.r, fill=True, transform=None, **self.props
        )
        fig.patches.append(circ)


class Text_Point(Annot):

    """Docstring for Rect_annot. """

    def __init__(self, x, y, text, r=10, **kwargs):
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
        self.text = text
        self.props = kwargs

    def draw(self, fig, ax):
        ax.annotate(
            self.text,
            xy=(self.x, self.y),
            xycoords="figure fraction",
            xytext=(10, 10),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
        )
