# main.py
import asyncio
from work.context import x, Context, r, Event
from work import setting
import traceback

# --------------------------------
# 1. Initialize. -----------------

@r.lifecycle.on("core.init.complete")
async def fundo_execution(ep:Event, x:Context= x):
    x.yh = x.r.adapter.get("yunhu")

    # Loading Data: GList, GS, US
    keys = await x.db.aget_all_keys()

    x.GList = await x.db.aget("GList", [])

    gs_keys = [key for key in keys if key.startswith("GS_")]
    gs_data = await x.db.aget_multi(gs_keys)
    for gid, value in gs_data.items():
        x.GS[gid[3:]] = value
    
    us_keys = [key for key in keys if key.startswith("US_")]
    us_data = await x.db.aget_multi(us_keys)
    for uid, value in us_data.items():
        x.US[uid[3:]] = value

    x.logger.warning("[main.py/Init] init.complete")
    await x.yh.Send.To("867108240","group").Text("init.complete")

# --------------------------------
# 2. Settings. -------------------

@x.notice.on_notice()
async def fundo_notice_setting(ep:Event, x:Context= x):
    if ep.get('detail_type')!="yunhu_bot_setting":
        return

    try:
        gid = ep.get("group_id")
        raw = ep.get("yunhu_setting",{})

        oldset = x.pick_dm(x.GS, gid)

        # groupset = setting.setting(ctx, gid, raw, oldset, time.time())

        # sdk.storage.set(f"groupset_{gid}", groupset)
        # INFOS.pop(gid, None)

    except:
        x.logger.error(traceback.format_exc())
        await ep.reply("A wrong occurred, which is unexpected.")

# --------------------------------
# Start the program. -------------

async def main():
    await r.run(keep_running=True)

if __name__ == "__main__":
    asyncio.run(main())
