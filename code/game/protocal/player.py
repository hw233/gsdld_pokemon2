#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
from gevent import sleep
import config

from corelib import log
from game.define import errcode, msg_define, constant, store_define
from game import Game
from game.common import utility

from game.gm import gmFunc
from game.common.gateway import AbsExport

from game.protocal.mapMixin import MapMixin
from game.protocal.niudanMixin import NiudanMixin
from game.protocal.zhuanpanMixin import ZhuanpanMixin
from game.protocal.shopMixin import ShopMixin
from game.protocal.rescueMixin import RescueMixin
from game.protocal.rankMixin import RankMixin
from game.protocal.vipMixin import VipMixin
from game.protocal.totemMinxin import TotemMixin
from game.protocal.petMixin import PetMixin
from game.protocal.yishouMixin import YishouMixin
from game.protocal.mailMixin import MailMixin
from game.protocal.friendMixin import FriendMixin
from game.protocal.houseMixin import HouseMixin
from game.protocal.marryMixin import MarryMixin
from game.protocal.examMixin import ExamMixin
from game.protocal.bossMixin import BossMixin
from game.protocal.chenghaoMinxin import ChenghaoMixin
from game.protocal.myheadMinxin import MyheadMixin
from game.protocal.daoguanMixin import DaoGuanMixin
from game.protocal.fubenMinxin import FubenRpcMixin
from game.protocal.zhudaoxunliMinxin import ZhudaoxunliRpcMixin
from game.protocal.daylyPVPMixin import DaylyPVPMixin
from game.protocal.roleMixin import RoleRpcMixin
from game.protocal.hetiMinxin import HetiRpcMixin
from game.protocal.chatMixin import ChatRpcMixin
from game.protocal.gongchengMinxin import GongchengRpcMixin
from game.protocal.guildMixin import GuildRpcMixin
from game.protocal.yabiaoMinxin import YabiaoRpcMixin
from game.protocal.diaoyuMinxin import DiaoyuRpcMixin

def _wrap_nolock(func):
    func._nolock_ = 1
    return func


class PlayerMgrHandler(AbsExport):
    """ 管理器的rpc处理类 """
    def __init__(self):
        self.logined = False

    def set_rpc(self, process):
        self.rpc = process
        if process:
            self.rpc.set_export(self)

    def on_close(self, process):
        """ 断线处理 """
        self.set_rpc(None)

    def stop(self):
        if self.rpc is not None:
            self.rpc.close()
            self.set_rpc(None)

    # def rc_register(self, account, password):
    #     """注册账号"""
    #     ok,data = Game.rpc_player_mgr.rc_register(account, password)
    #     if not ok:
    #         return 0, data
    #     return 1, data
    #
    # def rc_login(self, account, password):
    #     """ 登录接口 """
    #     ok, data = Game.rpc_player_mgr.rc_login(self.rpc, account, password)
    #     if not ok:
    #         return 0, data
    #     self.logined = True
    #     return 1, data

    def rc_relogin(self, pid, token):
        """ 玩家重连 """
        ok, data = Game.rpc_player_mgr.rc_relogin(self.rpc, pid, token)
        if not ok:
            return 0, data
        self.logined = True
        return 1, data

    def rc_tokenLogin(self, account, token, serverno, platform=""):
        """令牌登陆"""
        ok, data = Game.rpc_player_mgr.rc_tokenLogin(self.rpc, account, token, serverno, platform)
        if not ok:
            return 0, data
        self.logined = True
        return 1, data

class BasePlayerHander(AbsExport):
    DEBUG = 0
    MAIN_RPC = 1  # 是否rpc主连接

    if 0:
        from game.core import player as player_md

        player = player_md.Player()
        from game.common.gateway import Processer
        rpc = Processer()

    def __init__(self):
        setattr(self, 'player', None)
        setattr(self, 'rpc', None)

    @property
    def pid(self):
        return self.player.data.id if self.player else None

    @property
    def addr(self):
        return self.rpc.addr

    def uninit(self):
        setattr(self, 'player', None)
        self.set_rpc(None)

    def set_player(self, player):
        setattr(self, 'player', player)

    def set_rpc(self, process):
        log.debug('player(%s) handler(%s) set_rpc(%s)', self.pid, id(self),
                  id(process) if process is not None else process)
        if self.rpc:
            self.rpc.close(client=bool(self.MAIN_RPC))
        setattr(self, 'rpc', process)
        if process:
            self.rpc.set_export(self)

    def on_close(self, process):
        """ 断线处理 """
        log.debug('[handler]player(%s)on_close', self.pid)
        self.set_rpc(None)
        if self.player:
            self.player.on_close()

    def call(self, fname, data, noresult=False, timeout=None):
        if self.rpc is None:
            log.warning('***send(fname=%s, data=%s) error: player(%s).handler(%s) ?? handler(%s) rpc_is_None', fname, data,
                     id(self.player) if self.player else None,
                     id(self.player._handler) if self.player else None,
                     id(self))
            return
        if self.DEBUG:
            log.debug('send-- fname %s, data %s', fname, data)
        self.rpc.call(fname, data, noresult=noresult, timeout=timeout)

    def getProcesserInfo(self):
        if self.rpc is None:
            log.warning('***getProcesserInfo error: player(%s).handler(%s) ?? handler(%s) rpc_is_None',
                     id(self.player) if self.player else None,
                     id(self.player._handler) if self.player else None,
                     id(self))
            return
        return self.rpc.getProcesserInfo()

    def stop(self):
        log.debug('[handler]player(%s)stop', self.pid)
        self.set_rpc(None)

    def force_close(self):
        """ 服务器强制网关断开连接 """
        self.rpc.force_close()

    def router(self, addr_fnams):
        """
        添加gateway router
        addr_fnames为{"addr":["f1","f2"]}格式
        """
        if self.rpc:
            self.rpc.router(addr_fnams)

    def remove_router(self, addr):
        self.rpc.remove_router(addr)


class PlayerHandler(BasePlayerHander, MapMixin, VipMixin, TotemMixin, PetMixin,
                    YishouMixin, MailMixin, FriendMixin, HouseMixin, MarryMixin,
                    ExamMixin, BossMixin, ChenghaoMixin, MyheadMixin, NiudanMixin,
                    ZhuanpanMixin, RankMixin, RescueMixin, DaoGuanMixin, ShopMixin,
                    FubenRpcMixin, ZhudaoxunliRpcMixin, DaylyPVPMixin, RoleRpcMixin,
                    HetiRpcMixin, ChatRpcMixin, GongchengRpcMixin, GuildRpcMixin,
                    YabiaoRpcMixin, DiaoyuRpcMixin):

    """ 玩家rpc处理类 """
    DEBUG = 1

    def __init__(self):
        BasePlayerHander.__init__(self)
        self.active = True

    def rc_heartbeat(self):
        return 1, None

    def rc_execGMCMD(self, cmd):
        """ 执行gm命令 """
        isGM = self.player.data.IsGm()
        if not isGM:
            return 0, errcode.EC_NOT_GM
        lcmd = cmd.split("|")
        for oneCmd in lcmd:
            loneCmd = oneCmd.split(" ")
            fname, args = loneCmd[0], loneCmd[1:]
            func = getattr(gmFunc, fname)
            if func:
                try:
                    func(self.player, *args)
                    Game.glog.log2File("ExecGM", "%s|%s|%s" % (self.pid, oneCmd, lcmd))
                except Exception as err:
                    Game.glog.log2File("ExecGM_Err", "%s|%s|%s|%s"%(self.pid, err, oneCmd, lcmd))
                    log.log_except("ExecGM_Err %s|%s|%s|%s", self.pid, err, oneCmd, lcmd)
                    return 0, errcode.EC_EXEC_GM_CMD
            else:
                return 0, errcode.EC_NOT_GM_CMD
        return 1, None

    def rc_createRole(self, name, sex):
        """创建角色"""
        if name=="":
            return 0, errcode.EC_NAME_REPEAT

        d = Game.store.query_loads(store_define.TN_P_PLAYER, dict(name=name))
        if d and d[0].get("id") != self.player.id:
            return 0, errcode.EC_NAME_REPEAT

        self.player.base.SetName(name)
        self.player.base.SetSex(sex)
        #vip
        # res = Game.res_mgr.res_roleinit.get("vipLv")
        # if res:
        #     self.player.vip.SetVipLv(res.i)
        # #背包物品
        # res = Game.res_mgr.res_roleinit.get("bagItem")
        # if res:
        #     self.player.bag.add(res.arrayint2, constant.ITEM_ADD_INIT)
        # #背包装备
        # res = Game.res_mgr.res_roleinit.get("bagEquip")
        # if res:
        #     self.player.bag.add(res.arrayint2, constant.ITEM_ADD_INIT)
        #清空离线时间
        self.player.data.SetLogoutTime(0)
        #强制存库
        self.player.save(forced=True)
        return 1, None

    def rc_RoleRename(self, name):
        # 改名
        if name=="":
            return 0, errcode.EC_NAME_REPEAT

        res = Game.res_mgr.res_common.get("changeNameCost")
        if not res:
            return 0, errcode.EC_NORES
        
        d = Game.store.query_loads(store_define.TN_P_PLAYER, dict(name=name))
        if d and d[0].get("id") != self.player.id:
            return 0, errcode.EC_NAME_REPEAT

        respBag = {}
        if self.player.data.renameCount!=0:
            respBag = self.player.bag.costItem(res.arrayint2, constant.ITEM_COST_RENAME, wLog=True)
            if not respBag.get("rs", 0):
                return 0, errcode.EC_RENAME_NOT_ENOUGH

        self.player.data.SetName(name)

        self.player.save(forced=True)

        dUpdate = self.player.packRespBag(respBag)
        dRole = dUpdate.setdefault("role", {})
        dRole["roleBase"] = self.player.base.to_init_data()
        resp = {
            "name": name,
            "allUpdate": dUpdate,
        }
        return 1,resp


    def rc_createRoleHasPet(self):
        if self.player.pet.all_pets:
            return 1, dict(has=1)
        else:
            return 1, dict(has=0)

    def rc_createRoleSetPet(self, itemNo):
        return 1, None
        """设置初始化宠物"""
        # if itemNo not in (20, 48, 70):#初始化的三只宠物
        #     return 0, errcode.EC_CREATE_ERR
        # _, resp_pets, _ = self.player.pet.addNewPet({itemNo: 1}, constant.ITEM_ADD_INIT)
        # if resp_pets:
        #     return 1, None
        # else:
        #     return 0, errcode.EC_NORES

    def rc_syncSystemTime(self):
        return 1, dict(sysTime=int(time.time()))

    def rc_clientlog(self,data):
        Game.glog.log2File("rc_clientlog", "%s|%s" % (self.player.id, data))
        return 1, {}

    def rc_CliConfig(self,config):
        self.player.base.SetCliConfig(config)
        return 1, {}

    def rc_entergame(self, channel=0):
        """进入游戏"""
        if self.player.isBlock():
            self.player._handler.on_close(None)
            return 0, errcode.EC_CLOSE

        self.player.safe_pub(msg_define.MSG_ENTER_GAME)

        rs = {}
        rs["isGM"] = self.player.data.IsGm()
        rs["token"] = self.player.relogin_token

        rs["base"] = self.player.base.to_init_data()  # 角色基础信息
        rs["bag"] = self.player.bag.to_init_data()  # 背包
        rs["attr"] = self.player.attr.to_init_data()  # 角色属性
        rs["wallet"] = self.player.wallet.to_init_data()  # 角色钱包
        rs["history"] = self.player.history.to_init_data()  # 玩家历史统计
        rs["battle_array"] = self.player.battle_array.to_init_data()  # 角色出战阵型
        rs["map"] = self.player.map.to_init_data() #地图
        rs["niudan"] = self.player.niudan.to_init_data() #扭蛋
        rs["charge"] = self.player.charge.to_init_data() #充值
        rs["chargeDaily"] = self.player.chargeDaily.to_init_data() #充值日常
        rs["zhuanpan"] = self.player.zhuanpan.to_init_data() #转盘
        rs["shop"] = self.player.shop.to_init_data() #商店
        rs["rescue"] = self.player.rescue.to_init_data() #救援队
        rs["vipInfo"] = self.player.vip.to_init_data() #vip
        rs["totem"] = self.player.totem.to_init_data() #图腾
        rs["pet"] = self.player.pet.to_init_data()  # 角色宠物
        rs["rank"] = self.player.rank.to_init_data()  # 角色排行
        #好友
        rs["friend"] = {
            "red": Game.rpc_friend_mgr.getRedPoint(self.player.id)
        }
        rs["marryInfo"] = self.player.marry.to_init_data() #结婚
        rs["houseInfo"] = self.player.house.to_init_data() #房子
        rs["boss"] = self.player.boss.to_init_data() #boss四合一
        rs["chenghao"] = self.player.chenghao.to_init_data() #称号
        rs["myhead"] = self.player.myhead.to_init_data() #头像
        rs["daoguan"] = self.player.daoguan.to_init_data()
        rs["fubenInfo"] = self.player.fuben.to_init_data()
        rs["zhudaoxunli"] = self.player.zhudaoxunli.to_init_data()
        rs["daylypvp"] = self.player.daylypvp.to_init_data()
        rs["heti"] = self.player.heti.to_init_data()
        rs["chat"] = self.player.chat.to_init_data()
        rs["gongcheng"] = self.player.gongcheng.to_init_data()
        rs["guildInfo"] = self.player.guild.to_init_data()
        rs["jiebiao"] = self.player.yabiao.to_init_data()
        rs["diaoyu"] = self.player.diaoyu.to_init_data()
        # rs["task"] = self.player.totem.to_init_data()  # 任务
        server_info = self.player.base.GetServerInfo()
        server_info["logintime"] = int(time.time())
        server_info["lastLoginTime"] = self.player.data.loginTime
        rs["serverInfo"] = server_info
        
        return 1, rs
