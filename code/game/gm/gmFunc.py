#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time

from corelib import spawn
from game.define import constant, errcode

from corelib.frame import Game
from corelib import gtime

import app

def AddExp(who, add):
    add = int(add)
    iCurExp = who.base.GetExp()
    iNewExp = iCurExp + add
    who.base.SetExp(iNewExp)

    dUpdate = {}
    dUpdate["base"] = {"exp": who.base.GetExp()}
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)


def rescueScore(who,s):
    
    
    who.rescue.score=int(s)
    who.rescue.markDirty()

    dUpdate = {}
    dUpdate["rescue"] = who.rescue.to_init_data()
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)


def rescueKv(who,k,v):
    
    
    who.rescue.rescueSystemKey({int(k):int(v)})

    dUpdate = {}
    dUpdate["rescue"] = who.rescue.to_init_data()
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)

def rescueAuto(who):
    
    who.rescue.rescueAuto()

    dUpdate = {}
    dUpdate["rescue"] = who.rescue.to_init_data()
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)


def AddItem(who, dAdd):
    dAdd = eval(dAdd)
    respBag = who.bag.add(dAdd, constant.ITEM_ADD_GM)
    cost_update = who.packRespBag(respBag)
    resp = {
        "allUpdate": cost_update,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)

def charge(who, id, rmb="1"):
    # rid = int(rid)
    # from game.mgr.player import get_rpc_player
    # other = get_rpc_player(int(rid))
    retval = who.charge.charge(int(id),1, True)
    print("!!!!!!!!!!charge!!!!!!!!!!",retval)


def sendMail(who, title, content, attachment):
    pid = who.id
    attachment = eval(attachment)
    Game.rpc_mail_mgr.sendPersonMails(pid, title, content, attachment)

    mailList = Game.rpc_mail_mgr.getMailList(pid)
    print(mailList)


def rc(who, mod):
    app.frame.main_proxy.reload_modules("game.core.player"+mod)

def rp(who, mod):
    app.frame.main_proxy.reload_modules("game.protocal."+mod+"Mixin")

def reloadpy(who, *mod):
    app.frame.main_proxy.reload_modules(list(mod))


def SetAttr(who, dAttr):
    dAttr = eval(dAttr)
    who.attr.addAttr(dAttr, 0, 1)

    who.pet.do_login()
    who.attr.RecalFightAbility()

    # 打包返回信息
    dUpdate = {}
    dUpdate["base"] = {"fa": who.base.GetFightAbility()}
    dUpdate["attr"] = who.attr.to_update_data()
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleAllUpdate", resp, noresult=True)


def doProfile(who):
    import cProfile, lsprofcalltree
    profile = cProfile.Profile()
    profile.enable()

    AddItem(who, "{1001:100}")

    profile.disable()
    stats = lsprofcalltree.KCacheGrind(profile)
    stats.output(open('cProfile.callgrind', 'w'))

    # import yappi
    #
    # yappi.set_clock_type('cpu')
    # yappi.start(builtins=True)
    #
    #
    # with yappi.run():
    #     AddItem(who, "{1001:100}")
    #
    # yappi.stop()
    # stats = yappi.get_func_stats()
    # stats.save('./callgrind_%s.profile' % int(time.time()), type='callgrind')


def testFight(who, barrID):
    import time
    t1 = time.time()
    barrID = int(barrID)

    from game.fight import createFight

    # position = [{1: '38030013-1', 2: '38030013-2', 3: '38030013-3'}]
    # who._handler.rc_uploadBattleArray (1, position)

    fightobj = createFight(constant.FIGHT_TYPE_100)
    rs = fightobj.init_data(who.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL), barrID)
    if not rs:
        return 0, errcode.EC_INIT_BARR_FAIL
    fightLog = fightobj.doFight()
    log_end = fightLog.get("end", {})
    winerList = log_end.get("winerList", [])
    fightResult = 1 if who.id in winerList else 0


    barrRes = Game.res_mgr.res_barrier.get(barrID)
    rewardRes = Game.res_mgr.res_reward.get(barrRes.rewardId)
    respBag = {}
    if fightResult:
        dReward = rewardRes.doReward()
        respBag = who.bag.add(dReward, constant.ITEM_ADD_MORMAL_SCENE_FIGHT, wLog=True)

    # 打包返回信息
    dUpdate = who.packRespBag(respBag)
    resp = {
        "fightLog": fightLog,
        "allUpdate": dUpdate,
    }
    spawn(who.call, "mapNormalFight", resp, noresult=True)

    t2 = time.time()

    import ujson
    dump_log = ujson.dumps(fightLog)

    t3 = time.time()

    import config
    if config.serverNo == '030013':
        fp = open("D:\\work\\pokemon2\\server\\code\\log\\testFight.log", "a")
        fp.write(dump_log)
        fp.write("\n")
        fp.write(str(t2-t1))
        fp.write("\n")
        fp.write(str(t3-t2))
        fp.write("\n")
        fp.close()
    from corelib import log
    log.debug(t2-t1)
    log.debug(t3-t2)



def hetistart(who):
    who.heti.start()

def heticao(who):
    who.heti.cao()

def hetihebing(who,v):
    who.heti.hebing(v)

def hetidel(who,v):
    who.heti.delv(v)

def hetidone(who):
    who.heti.donetest()


def setxlys(who, v):
    v = int(v)
    who.fuben.setXlysMaxLevelId(v)

def setxlysbuff(who):

    for key in Game.res_mgr.res_xlysBuff.keys():
        who.fuben.addXlysBuff(key)
    

def setttsl(who, v):
    v = int(v)
    who.fuben.setTtslTodayMaxLevelId(v)
    
    m = who.fuben.getTtslMaxLevelId()
    if m<v:
        who.fuben.setTtslMaxLevelId(v)

def setlwbz(who, v):
    v = int(v)

    for l in range(v+1):

        res = Game.res_mgr.res_lwbz.get(l, None)
        if not res:
            continue

        cangbaotu = who.fuben.getCangbaotu(res.baotuId)
        cangbaotu.markDailyStatus(l)
        cangbaotu.setLevelStar(l, 3)

def AddExpAndUpgrade(who, add):
    add = int(add)
    iCurExp = who.base.GetExp()
    iNewExp = iCurExp + add
    who.base.SetExp(iNewExp)
    for i in range(300):
        rs, resp = who._handler.rc_roleUpgrade()
        if not rs:
            break
    # 打包返回信息
    dRole = {}
    dRole["roleBase"] = {"fa": who.base.fa,
                         "lv": who.base.GetLv(),
                         "exp": who.base.GetExp()}
    dRole["roleAttr"] = who.attr.to_update_data()

    dUpdate = {}
    dUpdate["role"] = dRole
    resp = {
        "allUpdate": dUpdate,
    }
    spawn(who.call, "roleUpgrade", resp, noresult=True)

def gongchengCount(who):
    who.gongcheng.gongchengCount()
def gongchengNew(who):
    who.gongcheng.gongchengNew()
def gongchengMsg(who):
    who.gongcheng.gongchengMsg()
def gongchengFucknpc(who):
    who.gongcheng.gongchengFucknpc()

def gongchengno(who,no):
    who.gongcheng.serverNo=no

def AddGuildExp(who, add):
    add = int(add)
    guildId = who.guild.GetGuildId()
    if not guildId:
        return
    from game.mgr.guild import get_rpc_guild
    rpc_guild = get_rpc_guild(guildId)
    if not rpc_guild:
        return
    exp, level = rpc_guild.addExp(add)
    resp = {
        "exp": exp,
        "level": level,
    }
    spawn(who.call, "guildDonate", resp, noresult=True)