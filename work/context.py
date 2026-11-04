# context.py
import asyncio
from ErisPulse import sdk as r
from ErisPulse.Core import client, HttpRequest, StorageManager, Logger
from ErisPulse.Core.Event import message, command, notice, Event
env = r.config.getConfig("QunCon", {})

import re
import time
import json
import random
import secrets
from datetime import datetime, timedelta

# --------------------------------
# Fun. ---------------------------

LOCKDATA = {}
VERSION = ""

def lock(iid):
    if iid not in LOCKDATA:
        LOCKDATA[iid] = asyncio.Lock()
    return LOCKDATA[iid]

def pick_dm(data, key, default= None):
    valuedict = data.get(key)

    if valuedict.get("version") == VERSION:
        return valuedict
    else:
        return default

def pick(data, keys, default= None):
    current = data
    for key in keys:
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return default
    return current

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
        self.yh = None

        self.lock = lock
        self.pick_dm = pick_dm
        self.pick = pick

        self.GList = []
        self.GS = {}
        self.US = {}

        self.VERSION = VERSION

x = Context()