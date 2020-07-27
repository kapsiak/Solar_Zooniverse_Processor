import matplotlib.patches as patches
from matplotlib.transforms import IdentityTransform


class Annot:
    def draw(self, fig, ax):
        raise NotImplementedError

    @staticmethod
    def to_annot(struct):
        """TODO: Docstring for to_annot.

        :param struct: TODO
        :returns: TODO

        """

        rect_attr = ["x", "y", "w", "h", "a"]
        point_attr = ["x", "y"]

        if all([hasattr(struct, att) for att in rect_attr]):
            return Rect_Annot(struct.x, struct.y, struct.w, struct.h, struct.a)

        if all([hasattr(struct, att) for att in point_attr]):
            return Circle_Annot(struct.x, struct.y)

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
        rect = patches.Rectangle(
            (self.x, self.y), self.w, self.h, angle=self.a, fill=False, **self.props
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
        rect = patches.Circle((self.x, self.y), radius=self.r, fill=True, **self.props)
        fig.patches.append(rect)
