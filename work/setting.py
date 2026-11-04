# setting.py
from .context import x, Context, r, Event

# --------------------------------
# Setting. -----------------------

def setting(x:Context= x):
    return {
        "version": x.VERSION,
        "information": {}
    }