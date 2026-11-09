# defender.py
from .context import x, Context, r, Event, GroupMessage
import asyncio
import zlib
from collections import deque
from rapidfuzz import fuzz
import traceback

# --------------------------------
# Root Defender. -----------------

async def _erase(m:GroupMessage, erase= True, middle= None, x:Context= x):
    if erase:
        await x.yh.Api.delete_message(m.msgid, chat_id= m.gid, chat_type= "group")

    # await PunishShowGroup(c, warn, reason, groupset, msgx, grouprecord, records)
    # await PunishToUser(c, groupset, msgx, reason)
    # if warn==2 and groupset.get("setting",{}).get("dropbot",True):
    #     await PunishBot(c, msgx)


async def root(m, method, gs, ss, gtemp, relay= True, x:Context= x):
    gs_def  = gs['defender']
    ss_cre  = ss['credit']

    try:
        if method =="user":
            _detect_user_risk(m, gs_def, ss_cre)
        else:
            _detect_content_risk(m, gs_def, ss_cre)
    except Hate as e:
        gs_deal = gs['information']['deal']
        gs_records = gs['records']
        if e.level ==2 or not gs_deal['dlt_warn']:
            return await _erase(m, erase= True)
        else:
            if len([r for r in gs_records if r['time'] >m.time -15 and r['sid'] ==m.sid]) >=4:
                return await _erase(m, erase= True, middle= _ban)


# --------------------------------
# Risk Detection. ----------------

def _detect_user_risk(m:GroupMessage, gs, credit, x:Context= x):
    # Group-V-user should be passed first.
    if m.gid in gs['userV']:
        return

    # And let's detect the ad content.
    if m.textual:
        msg = m.mcomsg.replace(r"\/", "/")   # prevent escape

        # has_sdk_ad
        if gs['Mad'] and "yunhu://ad?id=" in msg:
            raise Hate("[AD] Commercial AD Founded.")

        group_ad = ("yunhu://chat-add?id=", "yhfx.jwznb.com/share", "yhchat.com/group/homepage")
        if gs['Gad'] and any(ad in msg for ad in group_ad):
            raise Hate("[AD] Group AD (Engage) Founded.")

        # has_talk_ad
        if gs['Sad'] and "yunhu://alley-detail" in msg:
            raise Hate("[AD] Channel AD (Engage) Founded.")

    # Then S-user can be passed.
    if m.sid in gs['userS']:
        return
    if credit >20 and gs['cloudS']:
        return

    # And F-user should be blocked
    if m.sid in gs['userF']:
        raise Hate("[Isolate] The sender was left out by the whole group.")
    if credit <0 and gs['cloudF']:
        raise Hate("<Yunhu-Core> The sender was frozen out by yunhu-core.")

    return


def _detect_content_risk(m:GroupMessage, gs, credit, x:Context= x):
    # First, let's check content.
    if m.textual:
        # word detect
        if    any(w in m.mcomsg            for w in gs['wordV']['wd']) or \
              any(x.re.search(p, m.mcomsg) for p in gs['wordV']['zz']):
            pass
        elif  any(w in m.mcomsg            for w in gs['wordF']['wd']) or \
              any(x.re.search(p, m.mcomsg) for p in gs['wordF']['zz']):
            raise Hate("<Word> Word banned by group.", level= 1)
            # In reality, showing the banned word directly may let user escape it too easily.
            # And when user asks for help, admin can tell him the word by using setting permission.
    
    # Second, let's check frequent.
    histories = _detect_frequent(m)

    if gs['scam']:   # s-scam(lost money)
        scam_g = histories['s']['sames']
        if len(scam_g)>=3 and credit<20:         # >=3 within this group
            _detect_scam_content()

    if gs['spam']:   # g-spam(so much msg)
        sames, diffs = histories['g']['sames'], histories['g']['diffs']
        if   len(sames) >=6 or len(diffs) >=6:   # >=6 within this msg
            raise Hate("[Special] Spam(刷屏).")
        elif len(sames) >=4 or len(diffs) >=4:   # >=4 within this msg
            raise Hate("[Special] Looks like spam(刷屏).", level= 1)

        if m.textual:
            _detect_spam_content(m.msg)

    return

# --------------------------------
# Related Detect Function. -------

def _detect_frequent(m:GroupMessage):
    # Prepare data.
    msgcode = zlib.adler32(m.mcomsg.encode())
    histories = {
        'g': {'sames': set(), 'diffs': set()}, # g-spam(so much msg)
        's': {'sames': set(), 'diffs': set()}, # s-scam(lost money)
    }

    # You can do backup works elegantly in a loop.
    for key, kind, ts, td in ((m.gid, 'g', 3, 2), (m.sid, 's', 180, 0)):
        # Get data from Temp
        history = x.pick(x.Temp, ('history', key)) or deque(maxlen=10)
        if len(history) == 0:
            x.put(x.Temp, ('history', key), history)

        # Update the backup data
        history.append((msgcode, m.sid, m.gid, m.time, m.msgid))

        # Prepare data for scam or spam detect
        histories[kind]['all'] = history
        for hc, hs, hg, ht, hi in reversed(history):         # Conditions
            if ht <= m.time -ts:                             # 1: time window
                break                                        
            if (hs ==m.sid) if kind =='g' else (hg !=m.gid): # 2: match id
                if hc ==msgcode:                             # 3: same msg
                    histories[kind]['sames'].add(hi if kind =='g' else m.gid)
                if ht >m.time -td:                           # 3: not same msg & tight time window
                    histories[kind]['diffs'].add(hi)

    return histories


def _detect_scam_content(m:GroupMessage, gs, credit, x:Context= x):
    # To judge on different diversity, you can use the warning score.
    warn = 0

    # Diversity 1: User Credit
    warn += 14 if credit<0 else 0
    warn += 3 if m.same ==f"用户{m.sid}" else 0
    warn += 3 if "defalut-avatars" in m.sava else 0 

    # Diversity 2: Content
    if m.type in "text":
        if x.REM['defender_drive_search'].search(m.mcomsg):
            warn += 17
        elif _find_external_link(m.mcomsg):
            warn += 14

    # Diversity 3: Image
    # elif msgx["mode"] in 'image':
    #     pic_bytes = await c.tool.get_yunhu_picture(msgx['msgco'].get('imageUrl'))
    #     if pic_bytes:
    #         pic = Image.open(c.io.BytesIO(pic_bytes))
    #         warn += 17 if pyrxing.read_barcode(pic) else 0 # QRCode Inclueded

    # Final Grade settlement.
    if warn >15:
        raise Hate("[Special] Scam(诈骗).", level= 2 if warn >20 else 1)

    # reply = c.replies.admin['repeat'].format(sid=msgx['sid'], msg=msg, warn=warn, gs=gs, sayer=msgx['sayer'], count=len(gs))
    # buttons = {'buttons':[[{'text':'dlt',"actionType":2,'value':f'> 抹杀 {m.sid}\n{"\n".join(gid for gid,_ in gs)}'}]]}
    # await c.to.sends(reply, admingroups, "html", data=buttons)


def _detect_spam_content(msg):
    msglen = len(msg)
    if msglen <=20:
        return

    # Algorithm: Divide msg in half and detect similarity
    mid = msglen // 2
    score = fuzz.ratio(msg[:mid], msg[mid:])
    for (scorelv, msglenmed, msglenmin) in [(95,0,0),(89,100,0),(84,200,100)]:
        level = sorted([msglenmin, msglenmed, msglen]).index(msglen)
        if score >=scorelv and level >0:
            raise Hate("[Special] Spam(刷屏).", level= 1)

    # Prevent enter
    if "\n" in msg:
        counts = [len(line) for line in msg.split("\n")]
        med = sorted(counts)[len(counts)//2]
        if med<=5:
            return 2
    
    return 0


def _find_external_link(msg):
    match = x.REM['link_match'].search(msg)
    if match:
        url = match.group()
        if "jwznb.com" not in url and "yhchat.com" not in url:
            return True
    return False

# --------------------------------
# Middleware. --------------------

class Hate(Exception):
    def __init__(self, reason= "", level= 2, detail= None):
        self.reason = reason
        self.level = level
        self.detail = detail
        super().__init__(f"Defender: {reason}")

async def _ban(m):
    resp = await x.yh.Api.call("yunhu.ban", group_id= m.gid, user_id= m.sid, duration= 21600)


