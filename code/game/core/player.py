#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import weakref
import time
import uuid
import copy
import random

from gevent import sleep
from gevent.event import Event
from gevent.lock import RLock

from corelib.message import observable
from corelib import spawn_later, log, spawn
from corelib.gtime import current_time, current_hour, get_days

from game.define import errcode, msg_define, constant
from game.mgr.guild import get_rpc_guild


import config

from game.rpc.rankRPC import RankPlayerRpc
from game.rpc.marryRPC import MarryPlayerRpc
from game.rpc.bossRPC import BossPlayerRpc


from game import Game
from game.models.player import ModelPlayer
from game.core.playerBag import PlayerBag
from game.core.playerAttr import PlayerAttr
from game.core.playerWallet import PlayerWallet
from game.core.playerBase import PlayerBase
from game.core.playerRank import PlayerRank
from game.core.playerHistory import PlayerHistory
from game.core.playerBattleArray import PlayerBattleArray
from game.core.playerMap import PlayerMap
from game.core.playerNiudan import PlayerNiudan
from game.core.playerCharge import PlayerCharge
from game.core.playerChargeDaily import PlayerChargeDaily
from game.core.playerZhuanpan import PlayerZhuanpan
from game.core.playerShop import PlayerShop
from game.core.playerRescue import PlayerRescue
from game.core.playerVip import PlayerVip
from game.core.playerTotem import PlayerTotem
from game.core.playerTask import PlayerTask
from game.core.playerPet import PlayerPet
from game.core.playerHouse import PlayerHouse
from game.core.playerMarry import PlayerMarry
from game.core.playerExam import PlayerExam
from game.core.playerBoss import PlayerBoss
from game.core.playerChenghao import PlayerChenghao
from game.core.playerMyhead import PlayerMyhead
from game.core.playerRelationship import PlayerRelationship
from game.core.playerDaoGuan import PlayerDaoGuan
from game.core.playerFuben import PlayerFuben
from game.core.playerZhudaoxunli import PlayerZhudaoxunli
from game.core.playerDaylyPVP import PlayerDaylyPVP
from game.core.playerHeti import PlayerHeti
from game.core.playerChat import PlayerChat
from game.core.playerGongcheng import PlayerGongcheng
from game.core.playerGuild import PlayerGuild
from game.core.playerYabiao import PlayerYabiao
from game.core.playerDiaoyu import PlayerDiaoyu

def _wrap_lock(func):
    def _func(self, *args, **kw):
        with self._lock:
            return func(self, *args, **kw)
    return _func

class BasePlayer(object):
    def __init__(self):
        self._handler = None
        #玩家锁,串行玩家操作
        self._lock = RLock()
        self.reconnected = False

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    @property
    def process_id(self):
        return self._handler.rpc.pid if not self.disconnected else 0

    @property
    def disconnected(self):
        """ 是否断线状态 """
        return not self._handler or self._handler.rpc is None

    def call(self, fname, data, noresult=False):
        """ 发送消息
        不能将player.send=self._handler.send,因为player对象使用grpc暴漏给其它进程,grpc有缓存,
        并且player对象也缓存长期存在;当断线重连,player会从新设置新的handler,新的send,
        但是通过grpc调用rpc_player.send一样会调用旧的方法
        """
        if self._handler:
            self._handler.call(fname, data, noresult=noresult)

    def getProcesserInfo(self):
        if self._handler:
            return self._handler.getProcesserInfo()

    def set_process(self, process):
        """ 设置processer """
        self._handler.set_rpc(process)
        if process:
            process.set_lock(self._lock)

    def set_handler(self, hd, process=None):
        """ 添加player handler """
        log.debug('player(%s)(%s) set_handler(%s, %s)', self.id, id(self), id(hd) if hd else hd,
                                                        id(process) if process else process)
        if self._handler is not None:
            self._handler.uninit()
        self._handler = hd
        if hd is not None:
            hd.player = self
            self.set_process(process)
        if 0:
            from game.protocal.player import PlayerHandler
            self._handler = PlayerHandler()

    def on_close(self):
        """ 网络关闭的处理,需要实现断线保护 """
        log.debug('player(%s)on_close', self.id)
        sleep(0.05)  # 等待其它接口完成
        self.logout()

    def reconnect(self, process):
        """ 重连 """
        log.debug('[player]玩家(%s)重连', self.id)
        if not self._handler:  # 已经释放不能重连
            sleep(0.5)  # 等待本对象释放
            return False
        self.reconnected = True
        self.set_process(process)
        return True

@observable
class Player(BasePlayer, RankPlayerRpc, MarryPlayerRpc, BossPlayerRpc):
    DATA_CLS = ModelPlayer

    def __init__(self):
        BasePlayer.__init__(self)
        self.logined = False
        self.uninited = False
        self.loaded = False
        self.save_time = current_time()
        self.relogin_token = "" #重连令牌
        self.player = self

        self.data = None  # 玩家数据模型

        #属性有初始化优先级依赖
        self.attr = PlayerAttr(self)  # 角色属性
        self.history = PlayerHistory(self) #历史统计
        self.base = PlayerBase(self) #角色基础信息
        self.bag = PlayerBag(self) #角色背包
        self.wallet = PlayerWallet(self) #角色钱包
        self.battle_array = PlayerBattleArray(self) #角色出战阵型
        self.map = PlayerMap(self) #地图
        self.niudan = PlayerNiudan(self) #扭蛋
        self.charge = PlayerCharge(self) #充值
        self.chargeDaily = PlayerChargeDaily(self) #充值 日常
        self.zhuanpan = PlayerZhuanpan(self) #转盘
        self.shop = PlayerShop(self) #商店
        self.rescue = PlayerRescue(self) #救援队
        self.vip = PlayerVip(self) #Vip
        self.totem = PlayerTotem(self)  # 角色图腾
        self.pet = PlayerPet(self)  # 角色宠物
        self.marry = PlayerMarry(self) # 婚姻
        self.house = PlayerHouse(self) # 房子
        self.exam = PlayerExam(self)  # 答题
        self.boss = PlayerBoss(self) #boss 四合一
        self.chenghao = PlayerChenghao(self)  # 称号
        self.myhead = PlayerMyhead(self)  # 头像
        self.relationship = PlayerRelationship(self) #连协 羁绊 队伍加成
        self.daoguan = PlayerDaoGuan(self) #道馆
        self.fuben = PlayerFuben(self) #副本
        self.rank = PlayerRank(self) #角色排行
        self.zhudaoxunli = PlayerZhudaoxunli(self) #诸岛巡礼
        self.daylypvp = PlayerDaylyPVP(self) #日常pvp抢夺
        self.heti = PlayerHeti(self) #合体
        self.chat = PlayerChat(self) #玩家聊天
        self.gongcheng = PlayerGongcheng(self) #攻城
        self.guild = PlayerGuild(self) #公会
        self.yabiao = PlayerYabiao(self) #押镖
        self.diaoyu = PlayerDiaoyu(self) #钓鱼
        # self.task = PlayerTask(self)  # 角色任务
        #凌晨12点更新推送
        Game.sub(msg_define.MSG_WEE_HOURS, self.event_player_wee_hours)

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.base.name

    def markDirty(self):
        self.data.modify()

    def block(self):
        self.data.blocked = True
        if self.logined:
            self._handler.on_close(None)

    def unBlock(self):
        self.data.blocked = False

    def isBlock(self):
        return self.data.blocked

    def shutup(self):
        self.data.shutuped = True

    def unShutup(self):
        self.data.shutuped = False

    def isShutup(self):
        return self.data.shutuped

    @_wrap_lock
    def save(self, forced=False):
        log.debug('player(%s) save', self.id)
        self.save_time = current_time()
        self.data.save(Game.store, forced=forced)

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        log.debug('player(%s) load', self.id)

        self.base.load_from_dict(self.data.baseDict) #角色基础信息
        self.bag.load_from_dict(self.data.bagDict) #角色背包
        self.attr.load_from_dict(self.data.attrDict) #角色属性
        self.wallet.load_from_dict(self.data.walletDict) #角色钱包
        self.history.load_from_dict(self.data.historyDict) #玩家历史统计
        self.battle_array.load_from_dict(self.data.battleArrayDict) #角色出战阵型
        self.map.load_from_dict(self.data.mapDict) #地图
        self.niudan.load_from_dict(self.data.niudanDict) #扭蛋
        self.charge.load_from_dict(self.data.chargeDict) #充值
        self.chargeDaily.load_from_dict(self.data.chargeDailyDict) #充值日常
        self.zhuanpan.load_from_dict(self.data.zhuanpanDict) #转盘
        self.shop.load_from_dict(self.data.shopDict) #商店
        self.rescue.load_from_dict(self.data.rescueDict) #救援队
        self.vip.load_from_dict(self.data.vipDict) #vip
        self.totem.load_from_dict(self.data.totemDict)  # 图腾
        self.pet.load_from_dict(self.data.petDict)  # 角色宠物
        self.marry.load_from_dict(self.data.marryDict) #婚姻
        self.house.load_from_dict(self.data.houseDict) #房子
        self.exam.load_from_dict(self.data.examDict)  # 答题
        self.boss.load_from_dict(self.data.bossDict)  # boss 四合一
        self.chenghao.load_from_dict(self.data.chenghaoDict)  # 称号
        self.myhead.load_from_dict(self.data.myheadDict)  # 头像
        self.relationship.load_from_dict(self.data.relationshipDict) # 连协 羁绊 队伍加成
        self.daoguan.load_from_dict(self.data.daoguanDict)  # 道馆
        self.fuben.load_from_dict(self.data.fubenDict)  # 副本
        self.rank.load_from_dict(self.data.rankDict)  # 角色排行
        self.zhudaoxunli.load_from_dict(self.data.zhudaoxunliDict)  # 诸岛巡礼
        self.daylypvp.load_from_dict(self.data.daylypvpDict)  # 日常pvp抢夺
        self.heti.load_from_dict(self.data.hetiDict)  # 合体
        self.chat.load_from_dict(self.data.chatDict) #玩家聊天
        self.gongcheng.load_from_dict(self.data.gongchengDict)  # 攻城
        self.guild.load_from_dict(self.data.guildDict) #公会
        self.yabiao.load_from_dict(self.data.yabiaoDict)  # 押镖
        self.diaoyu.load_from_dict(self.data.diaoyuDict)  # 钓鱼
        #任务放在最后，会依赖其他模块的数据
        # self.task.load_from_dict(self.data.taskDict)  # 任务

    @classmethod
    def load_player(cls, pid):
        """ 根据pid加载Player对象 """
        data = cls.DATA_CLS.load(Game.store, pid)
        if data is None:
            return
        p = cls()
        p.data = data
        p.data.set_owner(p)
        p.load()
        return p

    @classmethod
    def login_player(cls, player, pid):
        """ 玩家登陆 """
        if player is None:
            player = cls()
            player.data = cls.DATA_CLS.load(Game.store, pid)
            player.data.set_owner(player)
            player.load()
        return player

    def wait_for_login(self):
        """ 等待前端新建角色,并登陆 """
        return True

    def login(self):
        """ 登陆 """
        if self.logined:
            return
        if self.isBlock():
            return
        self.logined = True
        log.debug('plyaer(%s) login', self.id)
        self.data.SetLoginTime(current_time())
        self.data.AddLoginNum()
        #读取服务器信息
        self.base.GetServerInfo()

        # 更新一下公会数据
        playerInfo = self.guild.to_guild_update()
        guildId = self.guild.GetGuildId()
        from game.mgr.guild import get_rpc_guild
        rpc_guild = get_rpc_guild(guildId)
        if rpc_guild:
            rpc_guild.update_playerInfo(playerInfo, _no_result=1)

        #生成重连令牌
        self.relogin_token = str(uuid.uuid1())
        # 重算属性
        self.attr.recalAttr()
        # 连协 羁绊 队伍加成
        self.relationship.do_login()
        # 宠物战力重算
        self.pet.do_login()

        # 注册一下自己的日常pvp镜像 今天没注册过
        if self.base.GetLv() >= 15:
            spawn(self.daylypvp.registerRobotData, config.serverNo, self.GetFightData(constant.BATTLE_ARRAY_TYPE_NORMAL))

        #遭遇战数据处理
        self.map.initPassEncounterId()
        #判断道馆是否开启
        self.daoguan.event_lv_uprade()

        #好友
        Game.rpc_friend_mgr.login(self.id, self.packbaseInfo())
        # 排行榜更新
        self.rank.do_login()
        #记录日志
        Game.glog.packLogin(self)
        Game.glog.packDaylyPVP(self)
        log.debug('plyaer(%s) login finish', self.id)

    def logout(self):
        """ 退出 """
        if not self.logined:
            return False
        self.logined = False
        log.debug('plyaer(%s) logout', self.id)
        self.data.SetLogoutTime(current_time())


        
        try:
            #好友状态更新
            Game.rpc_friend_mgr.logout(self.id, self.packbaseInfo())
            # 更新一下公会数据
            playerInfo = self.guild.to_guild_update()
            iTime = current_time()
            playerInfo["time"] = iTime
            guildId = self.guild.GetGuildId()
            from game.mgr.guild import get_rpc_guild
            rpc_guild = get_rpc_guild(guildId)
            if rpc_guild:
                rpc_guild.update_playerInfo(playerInfo, _no_result=1)
            #记录日志
            Game.glog.packLogout(self)
            Game.glog.packDaoGuan(self)
            
            self.diaoyu.exitdiaoyu()

            #退出攻城
            self.gongcheng.exit()
        except:
            log.log_except()
        finally:
            self.set_handler(None)
            Game.player_mgr.del_player(self)
            self.save(forced=True)

        log.debug('plyaer(%s) logout finish', self.id)
        return True


    def uninit(self):
        """ 释放 """
        if self.uninited:
            return
        self.uninited = True
        self.loaded = False
        log.debug('player(%s)uninit', self.id)
        self.attr.uninit() #角色属性
        self.base.uninit() #角色基础信息
        self.bag.uninit() #角色背包
        self.wallet.uninit() #角色钱包
        self.history.uninit() #玩家历史统计
        self.battle_array.uninit() #角色出战阵型
        self.map.uninit() #地图
        self.niudan.uninit() #扭蛋
        self.charge.uninit() #充值
        self.chargeDaily.uninit() #充值日常
        self.zhuanpan.uninit() #转盘
        self.shop.uninit() #商店
        self.rescue.uninit() #救援队
        self.vip.uninit() #vip
        self.totem.uninit() #角色图腾
        self.pet.uninit()  # 角色宠物
        self.marry.uninit()  #婚姻
        self.house.uninit()  #房子
        self.exam.uninit() #答题
        self.boss.uninit() #boss四合一
        self.chenghao.uninit() #称号
        self.myhead.uninit() #头像
        self.relationship.uninit() # 连协 羁绊 队伍加成
        self.daoguan.uninit()
        self.zhudaoxunli.uninit()
        self.daylypvp.uninit()
        self.rank.uninit() #角色排行
        self.heti.uninit()
        self.gongcheng.uninit()
        self.yabiao.uninit()
        self.diaoyu.uninit()
        # self.task.uninit() #角色任务
        Game.unsub(msg_define.MSG_WEE_HOURS, self.event_player_wee_hours)
        if self._handler:
            self.set_handler(None)

    def event_player_wee_hours(self):
        rs = {}

        rs["map"] = self.map.to_wee_hour_data()
        rs["niudan"] = self.niudan.to_wee_hour_data()
        rs["chargeInfo"] = self.charge.to_wee_hour_data()
        rs["chargeDaily"] = self.chargeDaily.to_wee_hour_data()
        rs["zhuanpan"] = self.zhuanpan.to_wee_hour_data()
        rs["shop"] = self.shop.to_wee_hour_data()
        rs["rescue"] = self.rescue.to_wee_hour_data()
        rs["vipInfo"] = self.vip.to_wee_hour_data()
        rs["totem"] = self.totem.to_wee_hour_data()
        rs["boss"] = self.boss.to_wee_hour_data()
        rs["base"] = self.base.to_wee_hour_data()
        rs["daoguan"] = self.daoguan.to_wee_hour_data()
        rs["fubenInfo"] = self.fuben.to_wee_hour_data()
        rs["guildInfo"] = self.guild.to_wee_hour_data()        
        resp = {
            "allUpdate": rs,
        }
        spawn(self.call, "WeeHourUpdate", resp, noresult=True)

    def packbaseInfo(self):
        info = {
            "name": self.name,
            "fa": self.base.GetFightAbility(),
            "lv": self.base.GetLv(),
            "sex": self.base.GetSex(),
            "vip": self.vip.GetVipLv(),
            "portrait": self.myhead.getPortrait(),
            "headframe": self.myhead.getHeadframe(),
            "title": self.chenghao.getUse()
        }
        return info


    def getDiaoyuInfo(self):
        role = {}
        
        role["showList"] = self.getShowList()
        role["title"] = self.chenghao.getUse()
        role["fashion"] = self.shizhuang.getUse()
        role["sex"] = self.base.GetSex()
        role["outfit"] = 0
        role["yulou"] = self.diaoyu.yulou
        role["catch"] = self.diaoyu.getDiaoyuBerob()
        role["status"] = self.diaoyu.status
        role["fa"] = self.base.fa
        role["portrait"] = self.myhead.getPortrait()
        role["headframe"] = self.myhead.getHeadframe()

    def diaoyuRob(self,robid,data,fdata,historydata):
        return self.diaoyu.diaoyuRob(robid,data,fdata,historydata)

    def diaoyuCleanScore(self):
        self.diaoyu.diaoyuCleanScore()

    def getGongchengInfo(self):
        role = {}
        
        ghname = ""
        ghcolor = 0
        guildRpc = get_rpc_guild(self.guild.GetGuildId())
        if guildRpc:
            ghname = guildRpc.getName()
            ghcolor = guildRpc.getColor()


        role["name"] = self.name
        role["ghname"] = ghname
        role["ghcolor"] = ghcolor

        # role["showList"] = self.getShowList()
        # role["title"] = self.chenghao.getUse()
        # role["fashion"] = self.shizhuang.getUse()
        # role["sex"] = self.base.GetSex()
        # role["outfit"] = 0
        # role["fa"] = self.base.fa

        # role["lv"] = self.base.GetLv()

        role["ghid"] = self.guild.GetGuildId()

        return role


    def gongchengNotiyGuild(self,cityid,atk,nowtime):
        return self.gongcheng.gongchengNotiyGuild(cityid,atk,nowtime)

    def broadcast_gongcheng_atkwin(self):
        self.safe_pub(msg_define.MSG_GET_GONGCHENG_ATK_WIN)

    def broadcast_gongcheng_defwin(self):
        self.safe_pub(msg_define.MSG_GET_GONGCHENG_DEF_WIN)


    def daylyPvpBeChallenge(self, serverNo, addr, fightData, fightResult):
        #今日被挑战次数已达到上限
        beChallengeNumRes = Game.res_mgr.res_common.get("pvpBeChallengeNumMax")
        if not beChallengeNumRes:
            return
        beChallengeNum = self.daylypvp.GetTodayBeChallengeNum()
        if beChallengeNum >= beChallengeNumRes.i:
            return
        beChallengeData = self.daylypvp.GetBeChallengeData()
        pid = fightData.get("pid", 0)
        for _data in beChallengeData:
            if not _data:
                continue
            if pid == _data.get("fightData", {}).get("pid", 0):
                return


        self.daylypvp.SetTodayBeChallengeNum(beChallengeNum+1)

        oneData = {
            "serverNo": serverNo,
            "addr": addr,
            "fightData": fightData,
            "fightTime": int(time.time()),
            "isWin": fightResult,
        }
        beChallengeData.append(oneData)
        self.daylypvp.SetBeChallengeData(beChallengeData)
        if fightResult:
            winRes = Game.res_mgr.res_common.get("pvpChallengeWinReward")
            if not winRes:
                return
            # 扣道具
            iNum = self.wallet.getCurrencyNum(constant.CURRENCY_DAYLY_PVP_COIN)
            if iNum >= winRes.i:
                cost = {constant.CURRENCY_DAYLY_PVP_COIN: winRes.i}
            else:
                cost = {constant.CURRENCY_DAYLY_PVP_COIN: iNum}
            if iNum:
                respBag = self.bag.costItem(cost, constant.ITEM_COST_DAYLY_PVP_CHALLENGE_FAIL, wLog=True)
                dUpdate = self.packRespBag(respBag)
                resp = {
                    "allUpdate": dUpdate,
                }
                spawn(self.call, "roleAllUpdate", resp, noresult=True)


    def packRespBag(self, respBag):
        exp = respBag.get("exp", 0)
        wallet = respBag.get("wallet", [])
        pets = respBag.get("pets", [])
        items = respBag.get("items", [])
        equips = respBag.get("equips", [])
        yishou = respBag.get("yishou", [])

        dUpdate = {}
        if exp:
            dUpdate["base"] = {"exp": self.base.GetExp(), "fa": self.base.GetFightAbility()}
        if wallet:
            dUpdate["wallet"] = self.wallet.to_update_data(wallet)
        if pets:
            dUpdate["pet"] = {"add_pets": [one.to_init_data() for one in pets]}
        if items:
            dUpdate["bag"] = {}
            dUpdate["bag"]["item_bag"] = self.bag.item_bag.to_update_data(items)
        if equips:
            dUpdate["bag"] = {}
            dUpdate["bag"]["equip_bag"] = self.bag.equip_bag.to_update_data(equips)
        if yishou:
            dUpdate["bag"] = {}
            dUpdate["bag"]["yishou_bag"] = self.bag.yishou_bag.to_update_data(yishou)
        return dUpdate


    def mergeRespBag(self, one, two):
        #exp1 = one.get("exp", 0)
        wallet1 = one.get("wallet", [])
        add_pets1 = one.get("pets", [])
        items1 = one.get("items", [])
        equips1 = one.get("equips", [])
        yishou1 = one.get("yishou", [])

        exp2 = two.get("exp", 0)
        wallet2 = two.get("wallet", [])
        add_pets2 = two.get("pets", [])
        items2 = two.get("items", [])
        equips2 = two.get("equips", [])
        yishou2 = two.get("yishou", [])

        resp = {}
        resp["exp"] = exp2

        wallet1.extend(wallet2)
        resp["wallet"] = list(set(wallet1))

        add_pets1.extend(add_pets2)
        resp["pets"] = list(set(add_pets1))

        items1.extend(items2)
        resp["items"] = list(set(items1))

        equips1.extend(equips2)
        resp["equips"] = list(set(equips1))

        yishou1.extend(yishou2)
        resp["yishou"] = list(set(yishou1))
        return resp


    def sendExamReward(self, rank, score, reward):
        respBag = self.bag.add(reward, constant.ITEM_ADD_EXAM_REWARD, wLog=True)

        dUpdate = self.packRespBag(respBag)
        resp = {
            "rank": rank,
            "score": score,
            "allUpdate": dUpdate,
        }
        spawn(self.call, "examRewardPush", resp, noresult=True)
        return 1


    def spawncall(self,msg,data):
        spawn(self.call, msg, data, noresult=True)


    def sendMail(self, mailData):
        resp = mailData
        resp["show"] = int(resp["show"])
        spawn(self.call, "mailPush", resp, noresult=True)


    def checkOpenLimit(self, openId):
        res = Game.res_mgr.res_open.get(openId)
        if not res:
            return False

        ilv = self.base.GetLv() #等级
        iVipLv = self.vip.GetVipLv()  # vip等级
        passDict = self.task.GetPassMainTaskDict()
        iOpenServiceDay = self.base.GetServerOpenDay()  # 开服天数
        retval = False
        # 条件类型 1 条件是且的关系 2 等级或vip
        if res.type == constant.NUMBER_1:
            if ilv >= res.level and iVipLv >= res.vip:
                if res.taskID:
                    if passDict.get(res.taskID, 0):
                        retval =  True
                else:
                    retval = True

        elif res.type == constant.NUMBER_2:
            if ilv >= res.level or iVipLv >= res.vip:
                retval = True

        if iOpenServiceDay < res.openServiceDay:
            retval = False

        alreadyOpenIdReward = False
        if openId in self.base.OpenIdReward:
            alreadyOpenIdReward = True

        if retval and len(res.reward)!=0 and not alreadyOpenIdReward:
            respBag = self.bag.add(res.reward, constant.ITEM_ADD_ADVANCE_NOTICE, wLog=True)
            dUpdate = self.packRespBag(respBag)
            spawn(self.call, "PushOpenID", {"ID":openId,"allUpdate": dUpdate}, noresult=True)
            self.base.AppendOpenIdReward(openId)

        if retval and res.openTaskId and res.openTaskId not in self.task.alreadyOpenTaskId:
            self.task.AppendOpenTaskId(res.openTaskId)
        return retval



    def GetFightData(self, battletype):
        """打包战斗需要的数据"""
        fightData = {}
        fightData["pid"] = self.id
        fightData["fa"] = self.base.GetFightAbility()
        fightData["name"] = self.name
        fightData["sex"] = self.base.sex
        # fightData["attr"] = self.attr.to_container_data()
        fightData["vipLv"] = self.vip.GetVipLv()
        fightData["lv"] = self.base.GetLv()
        fightData["portrait"] = self.myhead.getPortrait()
        fightData["headframe"] = self.myhead.getHeadframe()
        fightData["title"] = self.chenghao.getUse()
        #宠物
        fightData["pet"] = self.pet.to_fight_data(battletype)

        return fightData

    def sendFriendPresent(self):
        spawn(self.call, "presentPush", {}, noresult=True)


    def costItem(self, dCost, reason, force=False, wLog=False):
        return self.bag.costItem(dCost, reason, force, wLog)
        
    def getName(self):
        return self.name

    def toChatInfo(self):
        info = {}
        info["rid"] = self.id
        info["name"] = self.name
        info["lv"] = self.base.GetLv()
        info["fa"] = self.base.fa
        info["sex"] = self.base.GetSex()
        info["vipLv"] = self.vip.GetVipLv()
        info["portrait"] = self.myhead.getPortrait()
        info["headframe"] = self.myhead.getHeadframe()
        return info

    def privateChatReceive(self, rid, chatinfo, content, sendTime):
        self.chat.privateChatReceive(rid, chatinfo, content, sendTime)
        #推送
        resp = {}
        resp.update(chatinfo)
        resp["content"] = content
        resp["sendTime"] = sendTime
        spawn(self.call, "privateChatPush", resp, noresult=True)
        return self.toChatInfo()



    def sendEnterGuild(self, guildId):
        self.guild.SetGuildId(guildId)
        self.guild.reSetRefTime()
        # self.task.initGuildActTasks()
        # self.task.initGuildActRewardTasks()
        dUpdate = {}
        dUpdate["guildInfo"] = self.guild.to_init_data()
        resp = {
            "allUpdate": dUpdate,
        }
        spawn(self.call, "guildPush", resp, noresult=True)
        # 抛事件
        self.safe_pub(msg_define.MSG_JOIN_GUILD)

    def sendGuildRed(self, guildInfo):
        dUpdate = {}
        dUpdate["guildInfo"] = guildInfo
        resp = {
            "allUpdate": dUpdate,
        }
        spawn(self.call, "guildRedPush", resp, noresult=True)

    def sendGuildOperPush(self, type, guildInfo):
        if type == constant.GUILD_OPER_TYPE_4:  # 4=踢出
            self.guild.SetGuildId(0)
            guildInfo = {}
        dUpdate = {}
        dUpdate["guildInfo"] = guildInfo
        resp = {
            "type": type,
            "allUpdate": dUpdate,
        }
        spawn(self.call, "guildOperPush", resp, noresult=True)

    def isInGuild(self):
        return self.guild.GetGuildId()

    def sendGuildSxPush(self, guildInfo):
        spawn(self.call, "guildSxPush", guildInfo, noresult=True)

    def robHusongCar(self,robid,data,fdata,historydata):
        return self.yabiao.robHusongCar(robid,data,fdata,historydata)

    def revengeHusongCar(self,robid,data,fdata,historydata):
        return self.yabiao.revengeHusongCar(robid,data,fdata,historydata)

#---------------------
#---------------------
#---------------------


