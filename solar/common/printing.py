from threading import Lock

lprint_lock = Lock()

def lr_print(*a,**b):
    with lprint_lock:
        print(*a,**b,end='\r')

def l_print(*a,**b):
    with lprint_lock:
        print(*a,**b)
