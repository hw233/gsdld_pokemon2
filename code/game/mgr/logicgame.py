#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from gevent import sleep, Timeout
from gevent.lock import Semaphore

from corelib.frame import log, spawn, Game

import app
import config

from game.define import constant

from game.rpc.bossRPC import BossLogicRpc
from game.rpc.chatRPC import ChatLogicRpc
from game.rpc.roomRPC import RoomLogicRpc
from game.rpc.groupPkRPC import GroupPKLogicRpc
from game.rpc.levelContestRPC import LevelContestLogicRpc
from game.mgr.guild import get_rpc_guild

_logic_free_time = 0
def logic_capacity_check(cell):
    """ 根据逻辑进程容量比率, 返回:
        1=需要增加
        0=不处理
        -1=需要减少
    """
    import config

    c = cell.get_count()

    logic_pool = config.logic_pool
    if c < logic_pool:
        return 1
    elif c == logic_pool:
        return 0

    # try:
    #     count = Game.rpc_player_mgr.get_count()
    #     c = Game.rpc_sub_player_mgr.count()
    # except:
    #     log.log_except()
    #     return 0
    #
    # total = c * config.logic_players
    # rate = float(total - count) / config.logic_players
    # if count >= total or rate < 0.2:
    #     return 1
    # global _logic_free_time
    # if rate > 1.5 and time.time() - _logic_free_time >= 20*60:
    #     _logic_free_time = time.time()
    #     return -1
    return 0




class LogicGame(BossLogicRpc, ChatLogicRpc, RoomLogicRpc, GroupPKLogicRpc, LevelContestLogicRpc):
    _rpc_name_ = 'rpc_logic_game'

    inited = False

    lock_count = 9999

    def __init__(self):
        self.stoping = False
        self.stoped = True
        self.stop_lock = Semaphore(self.lock_count)
        self.stop_mgrs = []
        self.logic = self

        self._update_addr_task = None

    def update_serverNo_addr(self):
        from game.mgr.levelContest import get_rpc_level_contest
        from game.mgr.groupPK import get_rpc_grouppk

        while True:
            sleep(60)
            try:
                proxy = get_rpc_level_contest()
                if proxy:
                    proxy.update_serverNo_addr(config.serverNo, app.addr, _no_result=True)

                proxy = get_rpc_grouppk()
                if proxy:
                    proxy.update_serverNo_addr(config.serverNo, app.addr, _no_result=True)
                sleep(600)
            except:
                log.log_except()


    def start(self):
        if not self.stoped:
            return False
        self.stoped = False
        # self._update_addr_task = spawn(self.update_serverNo_addr)
        for mgr in self.stop_mgrs:
            try:
                if not hasattr(mgr, 'start'):
                    continue
                mgr.start()
            except Exception as e:
                log.log_except('stop mgr(%s) error:%s', mgr, e)
        return True

    def _stop(self):
        pass

    def stop(self):
        """ 进程退出 """
        if self.stoping:
            return
        self.stoping = True
        log.info('game模块(%s)停止', self.__class__.__name__)

        def _stop_func():
            try:
                self._stop()
            except Exception:
                log.log_except()

            for mgr in self.stop_mgrs:
                try:
                    mgr.stop()
                except Exception as e:
                    log.log_except('stop mgr(%s) error:%s', mgr, e)
            sleep(0.5)  # 允许其它线程切换
            #等待其它完成
            while self.stop_lock.wait() < self.lock_count:
                sleep(0.1)
        try:
            #保证在30分钟内处理完
            with Timeout.start_new(60 * 30):
                _stop_func()
        except:
            log.log_except()
        log.info('[game]stoped!')
        self.stoped = True

    def add_mgr(self, mgr):
        self.stop_mgrs.append(mgr)


    def reloadConfig(self, tname):
        Game.res_mgr.loadByNames(tname)


    def spawncall(self, id, msg, data):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(id)
        if not proxy:
            return
        proxy.spawncall(msg, data)


    def getFightData(self, pids):
        from game.mgr.player import get_rpc_player
        fd = {}

        for pid in pids:
            player = get_rpc_player(pid)
            if player:
                fightdata = player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)
                if fightdata:
                    fd[pid] = fightdata

        return fd

    def getFightDataOne(self, pid):
        from game.mgr.player import get_rpc_player

        player = get_rpc_player(pid)
        if not player:
            return

        return player.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL)

    def sendMail(self, pid, title, content, attachment):
        Game.rpc_mail_mgr.sendPersonMail(pid, title, content, attachment, push=False)




    def crChargeNum(self, num):
        resp = {"num": num}
        Game.player_mgr.broadcast("PushCommonresCharge", resp)

    def crJJnum(self, msg):
        Game.player_mgr.broadcast("PushCommonresJinjie", msg)

    def broadcastChengzhangjijinNum(self, ChengzhangjijinNum):
        resp = {"num": ChengzhangjijinNum}
        Game.player_mgr.broadcast("PushChengzhangjijinNum", resp)



    def daylyPvpBeChallenge(self, pid, serverNo, addr, fightData, fightResult):
        from game.mgr.player import get_rpc_player
        other = get_rpc_player(pid)
        other.daylyPvpBeChallenge(serverNo, addr, fightData, fightResult, _no_result=True)


    def doCrossRankReward(self, rankId, rankType, rankInfo):
        Game.sub_cross_rank_mgr.acceptRankData({rankId: rankInfo})

        rankobj = Game.sub_cross_rank_mgr.getRank(rankType)
        if rankobj:
            rankobj.doCrossRankReward()


    def daylyPvpBeChallenge(self, pid, serverNo, addr, fightData, fightResult):
        from game.mgr.player import get_rpc_player
        other = get_rpc_player(pid)
        other.daylyPvpBeChallenge(serverNo, addr, fightData, fightResult, _no_result=True)

    def roomMsg(self,msgtype,ids,data):
        # print("******",msgtype,ids,data)

        if msgtype=="msg":
            if data["type"] == 3:
                pids = []
                for tid in ids:
                    pid = Game.player_mgr.getTeamid2pid(tid)
                    pids.append(pid)
            else:
                pids = ids
            resp = dict(rid=data["rid"], content=data["content"])
            Game.player_mgr.broadcast("worldMSGNotice", resp, keys=pids)
            return

        if data["type"]==1:
            if msgtype == "bye":
                Game.player_mgr.broadcast("pushHusongFinish", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "pushHusongFinish", {"id": data["id"]}, noresult=True)
        elif data["type"]==2:
            if msgtype == "bye":
                Game.player_mgr.broadcast("diaoyuExitPush", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "diaoyuExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("diaoyuStatusPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "diaoyuStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("diaoyuEntetPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "diaoyuEntetPush", {"list": data}, noresult=True)
        elif data["type"]==3:
            pids = []
            for tid in ids:
                pid = Game.player_mgr.getTeamid2pid(tid)
                pids.append(pid)

            if msgtype == "bye":
                Game.player_mgr.broadcast("wakuangExitPush", {"id": data["id"]}, keys=pids)
                # spawn(self.owner.call, "wakuangExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("wakuangStatusPush", {"list": data}, keys=pids)
                # spawn(self.owner.call, "wakuangStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("wakuangEntetPush", {"list": data}, keys=pids)
                # spawn(self.owner.call, "wakuangEntetPush", {"list": data}, noresult=True)
        elif data["type"]==4:
            if msgtype == "bye":
                Game.player_mgr.broadcast("kfbossExitPush", {"id": data["id"]}, keys=ids)
                # spawn(self.owner.call, "kfbossExitPush", {"id": data["id"]}, noresult=True)
            elif msgtype == "update":
                Game.player_mgr.broadcast("kfbossStatusPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossStatusPush", {"list": data}, noresult=True)
            elif msgtype == "hello":
                Game.player_mgr.broadcast("kfbossEntetPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossEntetPush", {"list": data}, noresult=True)
            elif msgtype == "gmsg":
                Game.player_mgr.broadcast("kfbossMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "kfbossMsgPush", {"list": data}, noresult=True)
        elif data["type"]==5:
            if msgtype == "gmsg":
                Game.player_mgr.broadcast("gongchengMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "gongchengMsgPush", {"list": data}, noresult=True)
                Game.rpc_guild_mgr.receive_gongcheng(data, _no_result=True)
        elif data["type"]==6:
            # if msgtype == "bye":
            #     Game.player_mgr.broadcast("jiujiyishouExitPush", {"id": data["id"]}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouExitPush", {"id": data["id"]}, noresult=True)
            # elif msgtype == "update":
            #     Game.player_mgr.broadcast("jiujiyishouStatusPush", {"list": data}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouStatusPush", {"list": data}, noresult=True)
            # elif msgtype == "hello":
            #     Game.player_mgr.broadcast("jiujiyishouEntetPush", {"list": data}, keys=ids)
            #     # spawn(self.owner.call, "jiujiyishouEntetPush", {"list": data}, noresult=True)
            
            if msgtype == "gmsg":
                Game.player_mgr.broadcast("jiujiyishouMsgPush", {"list": data}, keys=ids)
                # spawn(self.owner.call, "jiujiyishouMsgPush", {"list": data}, noresult=True)

    
    def gongchengCityReward(self,city,pid,type,num):
        res = Game.res_mgr.res_gongcheng.get(city, None)
        if not res:
            return False
        
        mailRes = Game.res_mgr.res_mail.get(type, None)
        if not mailRes:
            return False

        reward_org={}
        
        if type==constant.MAIL_ID_GONGCHENG_ATK_SUCC:
            reward_org=res.ATK_SUCC
        elif type==constant.MAIL_ID_GONGCHENG_DEF_FAIL:
            reward_org=res.DEF_FAIL
        elif type==constant.MAIL_ID_GONGCHENG_ATK_FAIL:
            reward_org=res.ATK_FAIL
        elif type==constant.MAIL_ID_GONGCHENG_DEF_SUCC:
            reward_org=res.DEF_SUCC
        
        reward=copy.deepcopy(reward_org)
        
        for k,v in reward.items():
            reward[k]=v*num

        # print('xxxxxxxxxx==1',num,reward_org)
        # print('xxxxxxxxxx==2',num,reward)
    
        if reward:
        
            title = mailRes.title % res.name
            content = mailRes.content % (res.name,num,num)

            Game.rpc_mail_mgr.sendPersonMail(pid, title, content, reward)

        return True



    def gongchengPersonScore(self,index,pid):
        
        res = Game.res_mgr.res_gongchengPersonrRank.get(index+1, None)
        if res:
        
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_PERSON, None)
            content = mailRes.content % str(index+1)


            Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def gongchengGuildScore(self,index,pids):
        
        res = Game.res_mgr.res_gongchengGangRank.get(index+1, None)
        if res:
        
            mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_GUILD, None)
            content = mailRes.content % str(index+1)

            for pid in pids:
                Game.rpc_mail_mgr.sendPersonMail(pid, mailRes.title, content, res.reward, push=False)

    def gongchengGuildReward(self,cityname,reward,pids):
        

        mailRes = Game.res_mgr.res_mail.get(constant.MAIL_ID_GONGCHENG_GUILDREWARD, None)
        title = mailRes.title % cityname
        content = mailRes.content % cityname

        for pid in pids:
            Game.rpc_mail_mgr.sendPersonMail(pid, title, content, reward, push=False)

    def gongchengNotiyGuild(self,guildid,cityid,atk):

        nowtime=time.time()
        rpc_guild = get_rpc_guild(guildid)
        if not rpc_guild:
            return

        from game.mgr.player import get_rpc_player

        members = rpc_guild.getMembers()
        for one in members:
            rid = one.get("rid", 0)
            if not rid:
                continue
            # isRobot = one.get("isRobot", 1)
            # if isRobot:
            #     continue
            rpc_player = get_rpc_player(rid)
            if not rpc_player:
                continue
            rpc_player.gongchengNotiyGuild(cityid,atk,nowtime)

        




    def robHusongCar(self,robid,data,fdata,historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.robHusongCar(robid,data,fdata,historydata)


    def revengeHusongCar(self,robid,data,fdata,historydata):
        from game.mgr.player import get_rpc_player
        proxy = get_rpc_player(data["id"])
        if not proxy:
            return

        return proxy.revengeHusongCar(robid,data,fdata,historydata)