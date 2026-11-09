# context.py
import asyncio
from ErisPulse import sdk as r
from ErisPulse.Core import client, HttpRequest, StorageManager, Logger, BaseAdapter
from ErisPulse.Core.Event import message, command, notice, Event
env = r.config.getConfig('QunCon', {})

import re
import time
import json
import random
import secrets
import csv
import io
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# --------------------------------
# Tools. -------------------------

LOCKDATA = {}
VERSION = "0.0.0"
MY = "7384288"
MYCI = "867108240"

def lock(iid):
    if iid not in LOCKDATA:
        LOCKDATA[iid] = asyncio.Lock()
    return LOCKDATA[iid]

def pick_dm(data, key, default= None):
    valuedict = data.get(key)

    if valuedict.get('version') == VERSION:
        return valuedict
    else:
        return default

def tabulate(keys):
    if isinstance(keys, (str, bytes)) or not hasattr(keys, "__iter__"):
        return (keys,)
    else:
        return keys

def pick(data, keys, default= None):
    keys = tabulate(keys)
    current = data

    for key in keys:
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return default
        
    return current

def put(data, keys, value):
    *path, last = tabulate(keys)
    root = data

    for k in path:
        data = data.setdefault(k, {})
    data[last] = value

    return root

REM = {
    'setting_sep': re.compile(r'\n(?:={3,10}|\+{3,10}|%{3,10})\s?\n'),
    'defender_drive_search': re.compile(r'^(?!.*(?:诈骗|防诈|被骗|反诈)).*?(?:(?<![隐自无窃公])私(?![有自人事心密])|加我|加q|日进|处对象|贷款|低资费|接.*活|滴滴|挣米|赚米|兼职|(?<!\d)(?:\d+\.\d+|\d+)\s*[元米块])'),
    'link_match': re.compile(r'(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})(:\d{1,5})?(\/[\w\-./?%&=+#:@~]*)?')
}

# --------------------------------
# Context. -----------------------

class Context:
    def __init__(self, **kwargs):
        self.r = r
        self.logger:Logger = r.logger
        self.db:StorageManager = r.storage
        self.message = message
        self.command = command
        self.notice = notice

        self.env = env
        self.yh:BaseAdapter = None
        self.json = json
        self.csv = csv
        self.io = io
        self.time = time

        self.lock = lock
        self.pick_dm = pick_dm
        self.pick = pick
        self.put = put

        self.GList = []
        self.GS = {}
        self.US = {}
        self.Temp = {}

        self.REM = {}
        self.VERSION = VERSION
        self.MY = MY
        self.MYCI = MYCI

x = Context()

# --------------------------------
# Message. -----------------------

@dataclass
class GroupMessage:
    gid:      str
    sid:      str
    same:     str
    super:    str
    sava:     str
    mco:      str
    msg:      str
    mcomsg:   str
    msgid:    str
    type:     str
    time:     float
    cmdid:    int
    parent:   str
    parentid: str
    textual:  bool
    ep:       Event

    @classmethod
    def load(cls, ep:Event):
        raw = ep.get_raw()['event']

        ttype = raw['message']['contentType']
        mco = raw['message'].get('content', {})
        if ttype=="post":
            msg = mco.get('postContent', "")
        else:
            msg = mco.get('text', "")

        return cls(
            gid=      ep.get_group_id(),
            sid=      ep.get_user_id(),
            same=     ep.get_user_nickname() or "无名用户",
            super=    raw['sender'].get('senderUserLevel', ""),
            sava=     raw['sender'].get('senderAvatarUrl', ""),
            mco=      mco,
            msg=      msg,
            mcomsg=   msg or str(mco),
            msgid=    raw['message']['msgId'],
            type=     ttype,
            time=     raw['message']['sendTime']/1000,
            cmdid=    raw['message'].get('parentId', ""),
            parent=   mco.get('parent', ""),
            parentid= raw['message'].get('commandId', 0),
            textual=  ttype in ('text', 'markdown', 'html', 'post', 'form'),
            ep=       ep,
        )