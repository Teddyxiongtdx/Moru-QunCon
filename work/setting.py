# setting.py
from .context import x, Context, r, Event
from . import tool

# --------------------------------
# Param loader. ------------------

def load_this(thing, alter= None):
    if alter:
        if thing ==alter[0]:
            return alter[1]
    return thing

def load_line(text, default= []):
    if not text.strip():
        return default
    
    parts = x.REM['setting_sep'].split(text)
    result = [(part.rstrip('\n'), tool.check_type(part)) for part in parts if part]
    if not result:
        return [(text, tool.check_type(text))]
    else:
        return result

def load_zzwd(text):
    zz = []
    wd = []
    if text:
        chars = text.split()
        for w in chars:
            if any(c in w for c in "[.$({+^*?"):
                zz.append(w)
            else:
                wd.append(w)
    return {'zz': zz, 'wd': wd}


# --------------------------------
# Setting. -----------------------

def setting(s= {}, x:Context= x):
    hate = x.pick(s,('23','selectStatus'),[True,False,False])

    return {
        'version': x.VERSION,
        'information': {
            'boards':   load_line(x.pick(s,('11','value'),"")),
            'welcomes': load_line(x.pick(s,('12','value'),"欢迎{uid}进群")),
            'leaves':   load_line(x.pick(s,('13','value'),"送行{uid}退群")),
            'judges':   load_this(x.pick(s,('14','selectStatus'),[False,False,False])),
            'deal': {
                're_group': load_this(
                    load_line(
                        x.pick(s,('51','value'),""), 
                        default= [("由于违反群规/群配置，此消息已经被拦截。{why}", "text")]
                    ),
                    alter= ([("/无提示", "text")], [])
                ), 
                're_user': tool.csv_list(x.pick(s,('51','value'),""), param= "msg,mode,to"),
                'dlt_warn': load_this(x.pick(s,('s1','value'),0) in (-1,0,1)),
                'dlt_hard': load_this(x.pick(s,('s1','value'),0) in (-1,0,2)),
            },
        },
        'defender': {
            'userV':    load_this(x.pick(s,('21.1','value'),"")),
            'userS':    load_this(x.pick(s,('21.2','value'),"")),
            'userF':    load_this(x.pick(s,('21.3','value'),"")),
            'cloudS':   load_this(x.pick(s,('s2','selectIndex'),0) in (-1,0,2)),
            'cloudF':   load_this(x.pick(s,('s2','selectIndex'),0) in (-1,0,1)),
            'Mad':      load_this(x.pick(s,('22','selectStatus'),(True,False,False))[0]),
            'Gad':      load_this(x.pick(s,('22','selectStatus'),(True,False,False))[1]),
            'Sad':      load_this(x.pick(s,('22','selectStatus'),(True,False,False))[2]),
            'scam':     load_this(x.pick(s,('23','selectStatus'),(True,False,False))[0]),
            'spam':     load_this(x.pick(s,('23','selectStatus'),(True,False,False))[1]),
            'seam':     load_this(x.pick(s,('23','selectStatus'),(True,False,False))[2]),
            'wordV':    load_zzwd(x.pick(s,('25','value'),'')),
            'wordF':    load_this(x.pick(s,('24','value'),'')),
        },
        'about': {
            'timestamp': x.time.time(),
            'count': 1,
        }
    }

def group_default_setting():
    return setting()

def group_default():
    return {}

def user_default():
    return {}

def group_memory_default():
    return {}

# --------------------------------
# Item processor. ----------------

