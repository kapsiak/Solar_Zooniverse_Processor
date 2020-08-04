from threading import Lock
from solar.common.config import Config

lprint_lock = Lock()


def chat(*args, **kwargs):
    """
    A thin wrapper that allows for turning on or off messages. 
    Takes the same arguments are print()
    """
    if Config.chatty:
        print(*args, **kwargs)


# The following two functions are currently unused.


def lr_print(*a, **b):
    with lprint_lock:
        print(*a, **b, end="\r")


def l_print(*a, **b):
    with lprint_lock:
        print(*a, **b)
