import matplotlib.patches as patches
from matplotlib.transforms import IdentityTransform


class Annot:
    def draw(self, fig, ax):
        raise NotImplementedError


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
