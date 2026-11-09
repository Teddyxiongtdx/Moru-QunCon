# main.py
import asyncio
from work.context import x, Context, r, Event, GroupMessage
from work import setting
import traceback

# --------------------------------
# 1. Initialize. -----------------

@r.lifecycle.on("core.init.complete")
async def fundo_execution(ep:Event, x:Context= x):
    x.yh = x.r.adapter.get('yunhu')

    # Loading Data: GList, GS, US
    keys = await x.db.aget_all_keys()

    x.GList = await x.db.aget('GList', [])

    gs_keys = [key for key in keys if key.startswith('GS_')]
    gs_data = await x.db.aget_multi(gs_keys)
    for gid, value in gs_data.items():
        x.GS[gid[3:]] = value
    
    us_keys = [key for key in keys if key.startswith('US_')]
    us_data = await x.db.aget_multi(us_keys)
    for uid, value in us_data.items():
        x.US[uid[3:]] = value

    x.logger.warning("[main.py/Init] init.complete")
    await x.yh.Send.To(x.MYCI,"group").Text("init.complete")


# --------------------------------
# 2. Settings. -------------------
@x.notice.on_notice()
async def fundo_notice_setting(ep:Event, x:Context= x):
    if ep.get('detail_type') !="yunhu_bot_setting":
        return

    try:
        gid = ep.get_group_id()
        s = x.json.loads(ep.get('yunhu_setting', '{}'))

        oldset = x.pick_dm(x.GS, gid)

        # groupset = setting.setting(ctx, gid, raw, oldset, time.time())

        # sdk.storage.set(f"groupset_{gid}", groupset)
        # INFOS.pop(gid, None)

    except:
        x.logger.error(traceback.format_exc())
        await ep.reply("A wrong occurred, which is unexpected.")


# --------------------------------
# 3. Group Msg. ------------------
@x.message.on_group_message()
async def fundo_normal_group_response(ep:Event, x:Context= x):
    m = GroupMessage.load(ep)
    gs = x.pick_dm(x.GS, m.gid, setting.group_default())
    ss = x.pick_dm(x.US, m.sid, setting.user_default())

    if gs['lead'] !=m.sid and m.slv =="owner":
        gs['lead'] = m.sid
    x.put(ss['G'], m.gid, m.slv)
    ss['credit'] += (ss['credit'] >=0)


# --------------------------------
# Start the program. -------------
async def main():
    await r.run(keep_running= True)

if __name__ =="__main__":
    asyncio.run(main())
