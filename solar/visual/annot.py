import matplotlib.patches as patches
from matplotlib.transforms import IdentityTransform
from functools import wraps
import matplotlib.transforms as tr


def prop_trans(fig, point, angle):
    return fig.transFigure + tr.Affine2D().rotate_deg_around(
        *fig.transFigure.transform(point), angle
    )


class Annot:
    """
    Base class for annotations to be added to images
    """

    def draw(self, fig, ax):
        raise NotImplementedError

    @staticmethod
    def to_annot(struct, **kwargs):
        """
        Convert a zooniverse struct to an annotation.
        Also can construct an annotation from arbitrary tuples of data.        

        :param struct: Data structure
        :type struct: any
        :param kwargs: Passed to constructor of individual annotations
        :returns: Annot
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
    """
    A rectangular annotation
    """

    def __init__(self, x, y, w, h, a, **kwargs):
        """Function __init__: 
        
        :param x: x position of bottom left corner (in normalized image coordinates)
        :type x: float
        :param y: y coord of bottom left corner (in normalized image coordinates)
        :type y: float
        :param w: width of rectangle (in normalized image coordinates)
        :type w: float
        :param h: height or rectangle (in normalized image coordinates)
        :type h: float
        :param a: angle of rectangle relative to horizontal (degrees)
        :type a: float
        :param kwargs: parameters passed to matplotlib.patches.Rectangle
        """
        self.x = x  # Of Center
        self.y = y  # Of Center
        self.w = w
        self.h = h
        self.a = a
        self.props = kwargs

    def draw(self, fig, ax):
        """Function draw: Draw this rectangle of the image fig
        
        :param fig: The matplotlib figure to draw on
        :type fig: matplotlib Figure
        :param ax: UNUSED
        """
        new = (self.x - self.w / 2, self.y - self.h / 2)
        rect = patches.Rectangle(
            new,
            self.w,
            self.h,
            angle=0,
            fill=False,
            transform=prop_trans(fig, (self.x, self.y), self.a),
            **self.props
        )
        fig.patches.append(rect)


class Circle_Annot(Annot):
    """
    A circular annotation (also used to draw points).
    """

    def __init__(self, x, y, r=10, **kwargs):
        """Function __init__: 
        
        :param x: x position of bottom left corner (in normalized image coordinates)
        :type x: float
        :param y: y coord of bottom left corner (in normalized image coordinates)
        :type y: float
        :param r: Radius of the circle
        :type r: float
        :param kwargs: parameters passed to matplotlib.patches.Circle
        """

        self.x = x
        self.y = y
        self.r = r
        self.props = kwargs

    def draw(self, fig, ax):
        """Function draw: Draw this circle of the image fig
        
        :param fig: The matplotlib figure to draw on
        :type fig: matplotlib Figure
        :param ax: UNUSED
        :returns: None
        :type return: None
        """

        new = fig.transFigure.transform((self.x, self.y))
        circ = patches.Circle(
            new, radius=self.r, fill=True, transform=None, **self.props
        )
        fig.patches.append(circ)


class Text_Point(Annot):

    """
    Draw an arrow pointing to a point, with a text description.
    """

    def __init__(self, x, y, text, r=10, **kwargs):
        """Function __init__: 
        
        :param x: x position of bottom left corner (in normalized image coordinates)
        :type x: float
        :param y: y coord of bottom left corner (in normalized image coordinates)
        :type y: float
        :param r: Radius of the circle
        :type r: float
        :param text: The text to write
        :type text: str

        """

        self.x = x
        self.y = y
        self.r = r
        self.text = text
        self.props = kwargs

    def draw(self, fig, ax):
        """Function draw: Draw this text_point.
        
        :param fig: The matplotlib figure to draw on
        :type fig: matplotlib Figure
        :param ax: UNUSED
        :returns: None
        """
        ax.annotate(
            self.text,
            xy=(self.x, self.y),
            xycoords="figure fraction",
            xytext=(10, 10),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
        )
