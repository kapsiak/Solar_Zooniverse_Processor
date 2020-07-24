from .structs import make_row
from .zimport import read_class


def main():
    """
    :returns: TODO

    """
    data = read_class("zooniverse/class.csv")
    row = make_row(data.iloc[-1])
    for r in row:
        print(r)


if __name__ == "__main__":
    main()
