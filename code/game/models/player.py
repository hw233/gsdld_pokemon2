#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define.store_define import TN_P_PLAYER

from store.store import StoreObj

from game import Game

import config

class ModelPlayer(StoreObj):
    """玩家数据"""
    TABLE_NAME = TN_P_PLAYER

    def init(self):
        self.id = None  # rid
        self.account = '' #账号
        self.password = '' #密码
        self.gm = 0 if int(config.serverNo) >= 60000 else 1 #是否gm 先默认都是GM
        self.newTime = 0  # 创建时间
        self.loginTime = 0  # 最后一次登录时间
        self.logoutTime = 0  # 最后一次退出时间
        self.itemTranceNo = 0 #用于生成物品唯一id的自增值
        self.mailTranceNo = 0 #用于生成邮件唯一id的自增值
        self.petTranceNo = 0  # 用于生成宠物唯一id的自增值
        self.loginNum = 0 #角色历史登陆次数
        self.shutuped = False     # 禁言
        self.blocked = False      # 封号
        self.onlineTimeTotal = 0  # 累计在线时长
        self.channel = 0  # 玩家渠道
        self.platform = "" # android  ios

        self.baseDict = {} #角色基础数据
        self.attrDict = {}  # 角色属性
        self.historyDict = {}  # 历史统计
        self.bagDict = {}  # 角色背包
        self.walletDict = {}  # 角色钱包
        self.rankDict = {}  # 角色排行
        self.battleArrayDict = {}  # 角色出战阵型
        self.mapDict = {}  # 角色地图
        self.niudanDict = {}  # 扭蛋
        self.chargeDict = {}  # 充值
        self.chargeDailyDict = {}  # 充值日常
        self.zhuanpanDict = {}  # 转盘
        self.shopDict = {}  # 商店
        self.rescueDict = {}  # 救援队
        self.vipDict = {}  # vip
        self.totemDict = {}  # 图腾
        self.petDict = {}  # 角色宠物
        self.marryDict = {} # 婚姻
        self.houseDict = {} # 房子
        self.examDict = {}  # 答题
        self.bossDict = {}  # boss 四合一
        self.chenghaoDict = {}  # 称号
        self.myheadDict = {}  # 头像
        self.relationshipDict = {}  # 连协 羁绊 队伍加成
        self.daoguanDict = {} #道馆
        self.taskDict = {}  # 任务
        self.fubenDict = {} #副本
        self.zhudaoxunliDict = {} #诸岛巡礼
        self.daylypvpDict = {}  # 日常pvp抢夺
        self.hetiDict = {} #合体
        self.chatDict = {} #玩家聊天
        self.gongchengDict = {} #攻城
        self.guildDict = {} #公会
        self.yabiaoDict = {} #押镖
        self.diaoyuDict = {} #钓鱼



    def set_owner(self, owner):
        self.owner = owner

    def to_save_dict(self, copy=False, forced=False):
        save = {}
        save['id'] = self.id
        save['account'] = self.account
        save['password'] = self.password
        save['gm'] = self.gm
        save['newTime'] = self.newTime
        save['loginTime'] = self.loginTime
        save['logoutTime'] = self.logoutTime
        save['itemTranceNo'] = self.itemTranceNo
        save['mailTranceNo'] = self.mailTranceNo
        save['petTranceNo'] = self.petTranceNo
        save['loginNum'] = self.loginNum
        save['shutuped'] = self.shutuped
        save['blocked'] = self.blocked
        save['onlineTimeTotal'] = self.onlineTimeTotal
        save['channel'] = self.channel
        save['platform'] = self.platform

        save['baseDict'] = self.owner.base.to_save_dict(forced=forced) #角色基础信息
        save['attrDict'] = self.owner.attr.to_save_dict(forced=forced)  # 角色属性
        save['historyDict'] = self.owner.history.to_save_dict(forced=forced)  # 历史统计
        save['bagDict'] = self.owner.bag.to_save_dict(forced=forced)  # 角色背包
        save['walletDict'] = self.owner.wallet.to_save_dict(forced=forced)  # 角色钱包
        save['rankDict'] = self.owner.rank.to_save_dict(forced=forced)  # 角色排行
        save['battleArrayDict'] = self.owner.battle_array.to_save_dict(forced=forced)  # 角色出战阵型
        save['mapDict'] = self.owner.map.to_save_dict(forced=forced)  # 地图
        save['niudanDict'] = self.owner.niudan.to_save_dict(forced=forced)  # 扭蛋
        save['chargeDict'] = self.owner.charge.to_save_dict(forced=forced)  # 充值
        save['chargeDailyDict'] = self.owner.chargeDaily.to_save_dict(forced=forced)  # 充值日常
        save['zhuanpanDict'] = self.owner.zhuanpan.to_save_dict(forced=forced)  # 转盘
        save['shopDict'] = self.owner.shop.to_save_dict(forced=forced)  # 商店
        save['rescueDict'] = self.owner.rescue.to_save_dict(forced=forced)  # 救援队
        save['vipDict'] = self.owner.vip.to_save_dict(forced=forced)  # vip
        save['totemDict'] = self.owner.totem.to_save_dict(forced=forced)  # 图腾
        save['petDict'] = self.owner.pet.to_save_dict(forced=forced)  # 角色宠物
        save["marryDict"] = self.owner.marry.to_save_dict(forced=forced)  # 婚姻
        save["houseDict"] = self.owner.house.to_save_dict(forced=forced)  # 房子
        save["examDict"] = self.owner.exam.to_save_dict(forced=forced)  # 答题
        save['bossDict'] = self.owner.boss.to_save_dict(forced=forced)  # boss 四合一
        save['chenghaoDict'] = self.owner.chenghao.to_save_dict(forced=forced)  # 称号
        save['myheadDict'] = self.owner.myhead.to_save_dict(forced=forced)  # 头像
        save['relationshipDict'] = self.owner.relationship.to_save_dict(forced=forced)  # 连协 羁绊 队伍加成
        save["daoguanDict"] = self.owner.daoguan.to_save_dict(forced=forced)  # 道馆
        save['fubenDict'] = self.owner.fuben.to_save_dict(forced=forced)  # 副本
        save['zhudaoxunliDict'] = self.owner.zhudaoxunli.to_save_dict(forced=forced)  # 诸岛巡礼
        save["daylypvpDict"] = self.owner.daylypvp.to_save_dict(forced=forced)  # 日常pvp抢夺
        save['hetiDict'] = self.owner.heti.to_save_dict(forced=forced)  # 合体
        save["chatDict"] = self.owner.chat.to_save_dict(forced=forced)  # 玩家聊天
        save['gongchengDict'] = self.owner.gongcheng.to_save_dict(forced=forced)  # 攻城
        save['guildDict'] = self.owner.guild.to_save_dict(forced=forced)  # 任务
        save['yabiaoDict'] = self.owner.yabiao.to_save_dict(forced=forced)  # 押镖
        save['diaoyuDict'] = self.owner.diaoyu.to_save_dict(forced=forced)  # 钓鱼
        # save['taskDict'] = self.owner.task.to_save_dict(forced=forced)  # 任务
        return save

    #overwrite
    def save(self, store, forced=False, no_let=False):
        StoreObj.save(self,store, forced=forced, no_let=no_let)
        self.owner.base.cleanDirty()  # 角色基础信息
        self.owner.attr.cleanDirty()  # 角色属性
        self.owner.history.cleanDirty()  # 历史统计
        self.owner.bag.cleanDirty()  # 角色背包
        self.owner.wallet.cleanDirty()  # 角色钱包
        self.owner.rank.cleanDirty()  # 角色排行
        self.owner.battle_array.cleanDirty()  # 角色出战阵型
        self.owner.map.cleanDirty()  # 地图
        self.owner.niudan.cleanDirty()  # 扭蛋
        self.owner.charge.cleanDirty()  # 充值
        self.owner.chargeDaily.cleanDirty()  # 充值日常
        self.owner.zhuanpan.cleanDirty()  # 转盘
        self.owner.shop.cleanDirty()  # 商店
        self.owner.rescue.cleanDirty()  # 救援队
        self.owner.vip.cleanDirty()  # vip
        self.owner.totem.cleanDirty()  # 图腾
        self.owner.pet.cleanDirty()  # 角色宠物
        self.owner.marry.cleanDirty() #婚姻
        self.owner.house.cleanDirty() #房子
        self.owner.exam.cleanDirty()  # 答题
        self.owner.boss.cleanDirty()  # boss 四合一
        self.owner.chenghao.cleanDirty()  # 称号
        self.owner.myhead.cleanDirty()  # 头像
        self.owner.relationship.cleanDirty()  # 连协 羁绊 队伍加成
        self.owner.daoguan.cleanDirty()  # 道馆
        self.owner.fuben.cleanDirty()  # 副本
        self.owner.zhudaoxunli.cleanDirty()  # 诸岛巡礼
        self.owner.daylypvp.cleanDirty()  # 日常pvp抢夺
        self.owner.heti.cleanDirty()  # 合体
        self.owner.chat.cleanDirty()  # 玩家聊天
        self.owner.gongcheng.cleanDirty()  # 攻城
        self.owner.guild.cleanDirty()  # 公会
        self.owner.yabiao.cleanDirty()  # 押镖
        self.owner.diaoyu.cleanDirty()  # 钓鱼
        # self.owner.task.cleanDirty()  # 任务

    def GetLoginTime(self):
        return self.loginTime

    def GetLogoutTime(self):
        return self.logoutTime

    def SetLoginTime(self, iTime):
        self.loginTime = iTime
        self.modify()

    def SetLogoutTime(self, iTime):
        self.logoutTime = iTime
        self.onlineTimeTotal += self.logoutTime - self.loginTime
        if self.onlineTimeTotal < 0:
            self.onlineTimeTotal = 0
        self.modify()

    def AddLoginNum(self):
        self.loginNum += 1
        self.modify()

    def IsGm(self):
        return self.gm

    def GenerateItemTranceNo(self):
        self.itemTranceNo += 1
        self.modify()
        return self.itemTranceNo

    def GeneratePetTranceNo(self):
        self.petTranceNo += 1
        self.modify()
        return self.petTranceNo

    @classmethod
    def name_to_id(cls, name):
        rs = Game.store.values(cls.TABLE_NAME, None, dict(name=name))
        if rs:
            return rs[0]['id']

    @classmethod
    def id_to_name(cls, pid):
        rs = Game.store.values(cls.TABLE_NAME, ['name'], dict(id=pid))
        if rs:
            return rs[0]['name']
