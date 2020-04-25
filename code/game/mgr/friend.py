#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game import Game
from corelib.frame import MSG_FRAME_STOP
from game.define import constant, errcode
from game.models.friend import ModelFriend
from time import time
from corelib import log, spawn
from gevent import sleep, event
from game.common import utility
from game.core.cycleData import CycleDay
import random
import copy

class FriendMgr(object):
    _rpc_name_ = "rpc_friend_mgr"
    TIME_OUT = 0.1

    def __init__(self):
        self.playerFriend = {}
        self.online = {}
        self.outline = {}
        self.playerFlag = {}
        self.playerWait = {}

        self._save_loop_task = None

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def getPlayerFriend(self, pid):
        if pid not in self.playerFriend:
            if self.playerFlag.get(pid):
                wait = event.Event()
                waits = self.playerWait.setdefault(pid, [])
                waits.append(wait)
                self.playerWait[pid] = waits

                wait.wait()
                return self.playerFriend.get(pid, None)

            self.playerFlag[pid] = 1
            friend = Friend(pid)
            new = friend.load()
            self.playerFriend[pid] = friend
            if pid in self.playerFlag:
                self.playerFlag.pop(pid)
            waits = self.playerWait.get(pid, [])
            for wait in waits:
                wait.set()

            return friend
        else:
            return self.playerFriend.get(pid, None)

    def start(self):
        self._save_loop_task = spawn(self._saveLoop)

        table_name, key_name = Game.store.store.cls_infos[ModelFriend.TABLE_NAME][:2]
        table = Game.store.store.get_table(table_name)

        for one in table.aggregate([{"$sample": {"size": 100}}]):
            pid = one.get("_id", 0)
            pf = self.getPlayerFriend(pid)
            self.outline[pid] = pf

    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        self.save(forced=True, no_let=True)

    def _saveLoop(self):
        stime = 30 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def save(self, forced=False, no_let=False):
        keys = list(self.playerFriend.keys())
        for pid in keys:
            friend = self.playerFriend.get(pid)
            if friend:
                friend.save(forced=forced, no_let=no_let)
                if int(time()) - friend.getActiveTime() > 3 * 3600 and \
                        not friend.getOnline() and  \
                        len(self.playerFriend) > 100:
                    self.playerFriend.pop(pid, None)
                    self.online.pop(pid, None)
                    self.outline.pop(pid, None)
                if forced and no_let:
                    pass
                else:
                    sleep()

    def login(self, pid, info):
        pf = self.getPlayerFriend(pid)
        if pf:
            self.online[pid] = pf
            if pid in self.outline:
                self.outline.pop(pid)
            pf.login()
            pf.updateBaseInfo(info)

    def logout(self, pid, info):
        pf = self.getPlayerFriend(pid)
        if pf:
            self.outline[pid] = pf
            if pid in self.online:
                self.online.pop(pid)

            pf.logout()
            pf.updateBaseInfo(info)

    def getFollowList(self, pid):
        followList = []

        pf = self.getPlayerFriend(pid)
        if not pf:
            return followList, 0

        fl = pf.getFollowList()
        for fid in fl:
            targetPF = self.getPlayerFriend(fid)
            if not targetPF:
                continue

            info = targetPF.getBaseInfo()
            info["presentStatus"] = pf.getPresentStatus(fid)
            info["isFan"] = int(pf.isFan(fid))
            followList.append(info)

        return followList, pf.getPresentCount()

    def getFollowSize(self, pid):
        pf = self.getPlayerFriend(pid)
        if not pf:
            return 0
        return pf.getFollowSize()

    def getFanList(self, pid):
        fanList = []
        pf = self.getPlayerFriend(pid)
        if not pf:
            return fanList

        fl = pf.getFanList()
        for fid in fl:
            targetPF = self.getPlayerFriend(fid)
            if not targetPF:
                continue

            info = targetPF.getBaseInfo()
            info["receiveStatus"] = pf.getReceiveStatus(fid)
            info["canReceive"] = int(pf.canReceive(fid))
            info["isFollow"] = int(pf.isFollow(fid))

            fanList.append(info)

        return fanList, pf.getReceiveCount()

    def getBlackList(self, pid):
        blackList = []
        pf = self.getPlayerFriend(pid)
        if not pf:
            return blackList

        bl = pf.getBlackList()
        for fid in bl:
            targetPF = self.getPlayerFriend(fid)
            if not targetPF:
                continue

            info = targetPF.getBaseInfo()
            blackList.append(info)

        return blackList

    def getRecommendList(self, pid):
        recommendList = []

        idList = []
        pf = self.getPlayerFriend(pid)
        if not pf:
            return recommendList

        onlinePlayer = list(self.online.keys())
        fl = pf.getFollowList()
        bl = pf.getBlackList()
        exclude = copy.deepcopy(fl)
        exclude.extend([pid])
        exclude.extend(bl)
        onlinePlayer = list(set(onlinePlayer).difference(set(exclude)))
        recommendlimit = 20
        recommendlimitRes = Game.res_mgr.res_common.get("recommendlimit", None)
        if recommendlimitRes:
            recommendlimit = recommendlimitRes.i

        recommendlimit += 10 # 加10个是为让客户端可以补缺

        if len(onlinePlayer) <= recommendlimit:
            idList.extend(onlinePlayer)
        else:
            idList = random.sample(onlinePlayer, recommendlimit)

        left = recommendlimit - len(idList)
        if left > 0:
            outlinePlayer = list(self.outline.keys())
            outlinePlayer = list(set(outlinePlayer).difference(set(exclude)))
            if len(outlinePlayer) <= left:
                idList.extend(outlinePlayer)
            else:
                idList.extend(random.sample(outlinePlayer, left))

        for fid in idList:
            targetPF = self.getPlayerFriend(fid)
            if not targetPF:
                continue

            info = targetPF.getBaseInfo()
            recommendList.append(info)

        return recommendList

    def addFollow(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        targetpf = self.getPlayerFriend(targetPid)
        if not pf or not targetpf:
            return errcode.EC_NOFOUND, 0

        if pf.isFollow(targetPid):
            return errcode.EC_FRIEND_ALEADY_FOLLOW, 0

        followSize = pf.getFollowSize()
        followLimit = 50
        followLimitRes = Game.res_mgr.res_common.get("followLimit", None)
        if followLimitRes:
            followLimit = followLimitRes.i

        if followSize >= followLimit:
            return errcode.EC_FRIEND_FOLLOW_LIMIT, 0

        fanSize = targetpf.getFanSize()
        targetLv = targetpf.getLv()
        fanBaseCount = 50
        fanBaseCountRes = Game.res_mgr.res_common.get("fanBaseCount", None)
        if fanBaseCountRes:
            fanBaseCount = fanBaseCountRes.i

        if fanSize >= fanBaseCount + targetLv:
            return errcode.EC_FRIEND_FAN_LIMIT, 0

        pf.addFollow(targetPid)
        targetpf.addFan(pid)

        return 0, pf.getPresentStatus(targetPid)

    def delFollow(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        targetpf = self.getPlayerFriend(targetPid)
        if not pf or not targetpf:
            return errcode.EC_NOFOUND

        pf.delFollow(targetPid)
        targetpf.delFan(pid)

        return 0

    def addBlack(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        targetpf = self.getPlayerFriend(targetPid)
        if not pf or not targetpf:
            return errcode.EC_NOFOUND

        if pf.isBlack(targetPid):
            return errcode.EC_FRIEND_ALEADY_BLACK

        blackLimit = 20
        blackLimitRes = Game.res_mgr.res_common.get("blackLimit", None)
        if blackLimitRes:
            blackLimit = blackLimitRes.i

        if pf.getBlackSize() >= blackLimit:
            return errcode.EC_FRIEND_BLACK_LIMIT

        pf.addBlack(targetPid)
        pf.delFan(targetPid)
        pf.delFollow(targetPid)

        targetpf.delFan(pid)
        targetpf.delFollow(pid)

        return 0

    def delBlack(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        targetpf = self.getPlayerFriend(targetPid)
        if not pf or not targetpf:
            return errcode.EC_NOFOUND

        pf.delBlack(targetPid)

        return 0

    def presentFollow(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        targetpf = self.getPlayerFriend(targetPid)
        if not pf or not targetpf:
            return errcode.EC_NOFOUND

        if pf.getPresentStatus(targetPid):
            return errcode.EC_FRIEND_ALEADY_PRESENT

        if not pf.isFollow(targetPid):
            return errcode.EC_FRIEND_NOT_FOLLOW

        pf.setPresentStatus(targetPid)
        targetpf.addReceive(pid)

        from game.mgr.player import get_rpc_player
        targetPlayer = get_rpc_player(targetPid, offline=False)
        if targetPlayer:
            targetPlayer.sendFriendPresent(_no_result=1)

        return 0

    def oneKeyPresentFollow(self, pid):
        pf = self.getPlayerFriend(pid)
        if not pf:
            return errcode.EC_NOFOUND

        from game.mgr.player import get_rpc_player

        followList = pf.getFollowList()
        for targetPid in followList:
            targetpf = self.getPlayerFriend(targetPid)
            if not targetpf:
                continue

            pf.setPresentStatus(targetPid)
            targetpf.addReceive(pid)

            targetPlayer = get_rpc_player(targetPid, offline=False)
            if targetPlayer:
                targetPlayer.sendFriendPresent(_no_result=1)

        return 0

    def getPresentCount(self, pid):
        pf = self.getPlayerFriend(pid)
        if not pf:
            return 0
        return pf.getPresentCount()

    def receiveFan(self, pid, targetPid):
        pf = self.getPlayerFriend(pid)
        if not pf:
            return errcode.EC_NOFOUND

        receiveLimit = 10
        receiveLimitRes = Game.res_mgr.res_common.get("receiveLimit", None)
        if receiveLimitRes:
            receiveLimit = receiveLimitRes.i
        if pf.getReceiveCount() >= receiveLimit:
            return errcode.EC_FRIEND_RECEIVE_LIMIT

        if not pf.canReceive(targetPid):
            return errcode.EC_FRIEND_NOT_IN_RECEIVE

        if pf.getReceiveStatus(targetPid):
            return errcode.EC_FRIEND_ALEADY_RECEIVE

        pf.setReceiveStatus(targetPid)
        pf.delReceive(targetPid)

        return 0

    def oneKeyReceiveFan(self, pid, targetPidList):
        num = 0
        pf = self.getPlayerFriend(pid)
        if not pf:
            return errcode.EC_NOFOUND, num

        receiveLimit = 10
        receiveLimitRes = Game.res_mgr.res_common.get("receiveLimit", None)
        if receiveLimitRes:
            receiveLimit = receiveLimitRes.i

        for targetPid in targetPidList:
            if pf.getReceiveCount() >= receiveLimit:
                break

            if not pf.canReceive(targetPid):
                continue

            if pf.getReceiveStatus(targetPid):
                continue

            num += 1
            pf.setReceiveStatus(targetPid)
            pf.delReceive(targetPid)

        return 0, num

    def updateBaseInfo(self, pid, info):
        pf = self.getPlayerFriend(pid)
        if pf:
            pf.updateBaseInfo(info)

    def getRedPoint(self, pid):
        pf = self.getPlayerFriend(pid)
        if not pf:
           return 0

        receiveLimit = 10
        receiveLimitRes = Game.res_mgr.res_common.get("receiveLimit", None)
        if receiveLimitRes:
            receiveLimit = receiveLimitRes.i

        if pf.getReceiveCount() < receiveLimit and pf.getReceiveSize() > 0:
            return 1

        if not pf.getFollowSize() and not pf.getFanSize():
            return 1

        return 0
    
    def getToWay(self,pid):
        fans,x=self.getFanList(pid)
        follow,x=self.getFollowList(pid)

        fansid=[]
        for x in fans:
            fansid.append(x["pid"])
        
        followid=[]
        for x in follow:
            followid.append(x["pid"])
        
        

        toway = list(set(fansid).intersection(set(followid)))
        return toway

    def isToway(self,pid,other):
        fans,x=self.getFanList(pid)
        follow,x=self.getFollowList(pid)

        fansid=[]
        for x in fans:
            fansid.append(x["pid"])
        
        followid=[]
        for x in follow:
            followid.append(x["pid"])
        
        if other in fansid:
            if other in followid:
                return 1
        
        return 0
    
class Friend(utility.DirtyFlag):
    DATA_CLS = ModelFriend

    def __init__(self, pid):
        utility.DirtyFlag.__init__(self)

        self.pid = pid                # 玩家id
        self.name = ""
        self.fa = 0
        self.lv = 0
        self.vip = 0
        self.portrait = 0
        self.headframe = 0
        self.sex = 0
        self.online = 0
        self.lastActiveTime = int(time())

        self.followList = []
        self.fanList = []
        self.blackList = []
        self.receiveList = []             # 可接收的玩家列表

        self.cycleData = CycleDay(self)

        self.data = None
        self.save_cache = {}

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def markActive(self):
        self.lastActiveTime = int(time())

    def getActiveTime(self):
        return self.lastActiveTime

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["name"] = self.name
            self.save_cache["fa"] = self.fa
            self.save_cache["lv"] = self.lv
            self.save_cache["vip"] = self.vip
            self.save_cache["portrait"] = self.portrait
            self.save_cache["headframe"] = self.headframe
            self.save_cache["sex"] = self.sex
            self.save_cache["followList"] = self.followList
            self.save_cache["fanList"] = self.fanList
            self.save_cache["blackList"] = self.blackList
            self.save_cache["receiveList"] = self.receiveList
            self.save_cache["cycleData"] = self.cycleData.to_save_bytes()

        return self.save_cache

    def load_from_dict(self, data):
        self.name = data.get("name", "")
        self.fa = data.get("fa", 0)
        self.lv = data.get("lv", 0)
        self.vip = data.get("vip", 0)
        self.portrait = data.get("portrait", 0)
        self.headframe = data.get("headframe", 0)
        self.sex = data.get("sex", 0)
        self.followList = data.get("followList", [])
        self.fanList = data.get("fanList", [])
        self.blackList = data.get("blackList", [])
        self.receiveList = data.get("receiveList", [])
        self.cycleData.load_from_dict(data.get("cycleData", ""))

    def load(self):
        self.data = self.DATA_CLS.load(Game.store, self.pid)
        new = False
        if not self.data:
            self.data = self.DATA_CLS()
            new = True
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.setOwner(self)
        return new

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def getBaseInfo(self):
        info = {}
        info["pid"] = self.pid
        info["name"] = self.name
        info["fa"] = self.fa
        info["lv"] = self.lv
        info["vip"] = self.vip
        info["portrait"] = self.portrait
        info["headframe"] = self.headframe
        info["sex"] = self.sex
        info["online"] = self.online
        return info

    def updateBaseInfo(self, info):
        self.name = info.get("name", "")
        self.fa = info.get("fa", 0)
        self.lv = info.get("lv", 0)
        self.vip = info.get("vip", 0)
        self.headframe = info.get("headframe", 0)
        self.portrait = info.get("portrait", 0)
        self.sex = info.get("sex", 0)
        self.markDirty()

    def getLv(self):
        return self.lv

    def getFollowSize(self):
        return len(self.followList)

    def getFollowList(self):
        self.markActive()
        return self.followList

    def addFollow(self, pid):
        self.markActive()
        self.markDirty()
        self.followList.append(pid)
        self.followList = list(set(self.followList))
        self.markDirty()

    def delFollow(self, pid):
        self.markActive()
        self.markDirty()
        if pid in self.followList:
            self.followList.remove(pid)
        self.markDirty()

    def isFollow(self, pid):
        return pid in self.followList

    def getFanList(self):
        self.markActive()
        return self.fanList

    def getFanSize(self):
        return len(self.fanList)

    def addFan(self, pid):
        self.markActive()
        self.markDirty()
        self.fanList.append(pid)
        self.fanList = list(set(self.fanList))
        self.markDirty()

    def delFan(self, pid):
        self.markActive()
        self.markDirty()
        if pid in self.fanList:
            self.fanList.remove(pid)
        self.markDirty()

    def isFan(self, pid):
        return pid in self.fanList

    def getBlackList(self):
        self.markActive()
        return self.blackList

    def getBlackSize(self):
        return len(self.blackList)

    def isBlack(self, pid):
        return pid in self.blackList

    def addBlack(self, pid):
        self.markActive()
        self.markDirty()
        self.blackList.append(pid)
        self.blackList = list(set(self.blackList))
        self.markDirty()

    def delBlack(self, pid):
        self.markActive()
        self.markDirty()
        if pid in self.blackList:
            self.blackList.remove(pid)
        self.markDirty()

    def addReceive(self, pid):
        self.markActive()
        self.markDirty()
        self.receiveList.append(pid)
        self.receiveList = list(set(self.receiveList))
        self.markDirty()

    def delReceive(self, pid):
        self.markActive()
        if pid in self.receiveList:
            self.receiveList.remove(pid)
        self.markDirty()

    def getReceiveSize(self):
        return len(self.receiveList)

    def canReceive(self, pid):
        self.markActive()
        return pid in self.receiveList and not self.getReceiveStatus(pid)

    def getPresentStatus(self, pid):
        self.markActive()
        status = self.cycleData.Query("presentStatus", {})
        return status.get(pid, 0)

    def setPresentStatus(self, pid):
        self.markActive()
        status = self.cycleData.Query("presentStatus", {})
        status[pid] = 1
        self.cycleData.Set("presentStatus", status)
        self.markDirty()

    def getPresentCount(self):
        status = self.cycleData.Query("presentStatus", {})
        return len(status)

    def getReceiveStatus(self, pid):
        self.markActive()
        status = self.cycleData.Query("receiveStatus", {})
        return status.get(pid, 0)

    def setReceiveStatus(self, pid):
        self.markActive()
        status = self.cycleData.Query("receiveStatus", {})
        status[pid] = 1
        self.cycleData.Set("receiveStatus", status)
        self.markDirty()

    def getReceiveCount(self):
        status = self.cycleData.Query("receiveStatus", {})
        return len(status)

    def login(self):
        self.online = 1

    def logout(self):
        self.online = 0

    def getOnline(self):
        return self.online


