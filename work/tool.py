# tool.py
from .context import x, Context, r, Event

def csv_list(text, param= None):
    if param:
        load_text = f"{param}\n{text}"
    else:
        load_text = text

    try:
        return list(x.csv.DictReader(x.io.StringIO(load_text)))
    except:
        return []