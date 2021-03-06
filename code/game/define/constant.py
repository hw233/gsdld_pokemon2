#!/usr/bin/env python3
#-*- coding:utf-8 -*-


MAX_SAFE_INTEGER = 9007199254740991

#属性定义
#=============== 属性定义 请一定要按顺序往后面加，否则出问题===============
#客户端展示属性
ATTR_HP = "hp" #生命
ATTR_MAXHP = "maxHP" #最大血量
ATTR_SHIELD = "shield" #初始护盾
ATTR_MAXSHIELD = "maxShield"  # 最大护盾
ATTR_MP = "mp" #初始魔法值
ATTR_MAXMP = "maxMP"  # 最大魔法值
#计算属性
ATTR_ATK = "atk" #攻击
ATTR_DEFE = "defe" #防御
ATTR_SPEED = "speed" #速度
ATTR_HIT = "hit" #命中
ATTR_MISS = "miss" #闪避
ATTR_CIRT = "cirt" #暴击
ATTR_CIRTSUB = "cirtSub" #抗暴
ATTR_HITRATE = "hitRate" #命中率 万分比
ATTR_MISSRATE = "missRate" #闪避率 万分比
ATTR_CIRTRATE = "cirtRate" #暴击率 万分比
ATTR_CIRTSUBRATE = "cirtSubRate" #抗暴率 万分比
ATTR_CIRTDAMRATE = "cirtDamRate" #暴击伤害附加 万分比
ATTR_CIRTDAMSUBRATE = "cirtDamSubRate" #暴击伤害减免 万分比
ATTR_PHYADDRATE = "phyAddRate" #物伤加深 万分比
ATTR_PHYSUBRATE = "phySubRate" #物伤减免 万分比
ATTR_MAGICADDRATE = "magicAddRate" #法伤加深 万分比
ATTR_MAGICSUBRATE = "magicSubRate" #法伤减免 万分比
ATTR_DAMADDRATE = "damAddRate" #伤害加深 万分比
ATTR_DAMSUBRATE = "damSubRate" #伤害减免 万分比
ATTR_ABNORMALRATE = "abnormalRate" #异常成功率 万分比
ATTR_ABNORMALSUBRATE = "abnormalSubRate" #异常抗性 万分比
ATTR_UNDEFRATE = "unDefRate" #无视防御率 万分比
ATTR_DAMADD = "damAdd" #附加伤害
ATTR_DAMSUB = "damSub" #附加伤害减免
ATTR_REALDAM = "realDam" #纯粹伤害
ATTR_HPRECOVER = "hpRecover" #生命回复
ATTR_VAMPIRERATE = "vampireRate" #吸血率 万分比
ATTR_LUCK = "luck" #幸运值
ATTR_SKDAMRATE = "skDamRate" #技能伤害加深 万分比
ATTR_SKDAMSUBRATE = "skDamSubRate" #技能伤害减免 万分比
ATTR_PVPDAMRATE = "pvpDamRate" #PVP伤害加成 万分比
ATTR_PVPDAMSUBRATE = "pvpDamSubRate" #PVP伤害减免 万分比
ATTR_PVEDAMRATE = "pveDamRate" #PVE伤害加成 万分比
ATTR_PVEDAMSUBRATE = "pveDamSubRate" #PVE伤害减免 万分比
ATTR_HPRATE = "hpRate" #生命加成 万分比
ATTR_ATKRATE = "atkRate" #攻击加成 万分比
ATTR_DEFERATE = "defeRate" #防御加成 万分比
ATTR_SPEEDRATE = "speedRate" #速度加成 万分比
ATTR_GRASSADD = "grassAddition"  # 草系增伤 万分比
ATTR_WATERADD = "waterAddition"  # 水系增伤 万分比
ATTR_FIREADD = "fireAddition"  # 火系增伤 万分比
ATTR_LIGHTADD = "lightAddition"  # 光系增伤 万分比
ATTR_DARKADD = "darkAddition"  # 暗系增伤 万分比
ATTR_GRASSSUB = "grassSub"  # 草系伤减 万分比
ATTR_WATERSUB = "waterSub"  # 水系伤减 万分比
ATTR_FIRESUB = "fireSub"  # 火系伤减 万分比
ATTR_LIGHTSUB = "lightSub"  # 光系伤减 万分比
ATTR_DARKSUB = "darkSub"  # 暗系伤减 万分比
ATTR_TREATRATE = "TreatRate" #治疗效果加成 万分比
ATTR_BETREATRATE = "beTreatRate" #受治疗效果加成 万分比
#=============== 属性定义 请一定要按顺序往后面加，否则出问题===============

ALL_ATTR = [ATTR_HP, ATTR_MAXHP, ATTR_SHIELD, ATTR_MAXSHIELD, ATTR_MP, ATTR_MAXMP, ATTR_ATK, ATTR_DEFE, ATTR_SPEED,
            ATTR_HIT, ATTR_MISS, ATTR_CIRT, ATTR_CIRTSUB, ATTR_HITRATE, ATTR_MISSRATE, ATTR_CIRTRATE, ATTR_CIRTSUBRATE,
            ATTR_CIRTDAMRATE, ATTR_CIRTDAMSUBRATE, ATTR_PHYADDRATE, ATTR_PHYSUBRATE, ATTR_MAGICADDRATE, ATTR_MAGICSUBRATE,
            ATTR_DAMADDRATE, ATTR_DAMSUBRATE, ATTR_ABNORMALRATE, ATTR_ABNORMALSUBRATE, ATTR_UNDEFRATE, ATTR_DAMADD,
            ATTR_DAMSUB, ATTR_REALDAM, ATTR_HPRECOVER, ATTR_VAMPIRERATE, ATTR_LUCK, ATTR_SKDAMRATE, ATTR_SKDAMSUBRATE,
            ATTR_PVPDAMRATE, ATTR_PVPDAMSUBRATE, ATTR_PVEDAMRATE, ATTR_PVEDAMSUBRATE, ATTR_HPRATE, ATTR_ATKRATE,
            ATTR_DEFERATE, ATTR_SPEEDRATE, ATTR_GRASSADD, ATTR_WATERADD, ATTR_FIREADD, ATTR_LIGHTADD, ATTR_DARKADD,
            ATTR_GRASSSUB, ATTR_WATERSUB, ATTR_FIRESUB, ATTR_LIGHTSUB, ATTR_DARKSUB, ATTR_TREATRATE, ATTR_BETREATRATE]

#宠物加成属性
PET_ADD_ATTR = [ATTR_HPRATE, ATTR_ATKRATE, ATTR_DEFERATE, ATTR_SPEEDRATE]

MAP_ATTRRATE_ATTR = {
    ATTR_HPRATE: ATTR_HP,
    ATTR_ATKRATE: ATTR_ATK,
    ATTR_DEFERATE: ATTR_DEFE,
    ATTR_SPEEDRATE: ATTR_SPEED,
}

#神装属性
GOD_EQUIP_ATTR = (ATTR_HP, ATTR_ATK, ATTR_HIT, ATTR_CIRT, ATTR_SPEED, ATTR_DEFE, ATTR_MISS,
            ATTR_CIRTSUB)

#元素属性
PKM2_ELE_TYPE_NONE = 0 #无属性
PKM2_ELE_TYPE_WATER = 1 #水
PKM2_ELE_TYPE_GRASS = 2 #草
PKM2_ELE_TYPE_FIRE = 3 #火
PKM2_ELE_TYPE_LIGHT = 4 #光
PKM2_ELE_TYPE_DARK = 5 #暗

ALL_ELE_TYPE = (PKM2_ELE_TYPE_WATER, PKM2_ELE_TYPE_GRASS, PKM2_ELE_TYPE_FIRE,
                PKM2_ELE_TYPE_LIGHT, PKM2_ELE_TYPE_DARK)

#职业类型
PKM2_JOB_TYPE_MAGIC = 1 #法攻型
PKM2_JOB_TYPE_PHY = 2 #物攻型
PKM2_JOB_TYPE_DEF = 3 #防御型
PKM2_JOB_TYPE_AUXILIARY = 4 #辅助型

#角色属性容器类型
PKM2_ATTR_CONTAINER_GLOBAL = 1 # 全局增加属性
PKM2_ATTR_CONTAINER_FIRE = 2 # 火系增加属性
PKM2_ATTR_CONTAINER_WATER = 3 # 水系增加属性
PKM2_ATTR_CONTAINER_GRASS = 4 # 草系增加属性
PKM2_ATTR_CONTAINER_LIGHT = 5 # 光系增加属性
PKM2_ATTR_CONTAINER_DARK = 6 # 暗系增加属性
PKM2_ATTR_CONTAINER_MAGIC = 7 # 法攻型增加属性
PKM2_ATTR_CONTAINER_PHY = 8 # 物攻型增加属性
PKM2_ATTR_CONTAINER_DEF = 9 # 防御型增加属性
PKM2_ATTR_CONTAINER_AUXILIARY = 10 # 辅助型增加属性

MAP_ELETYPE_ATTR_CONTAINER = {
    PKM2_ELE_TYPE_FIRE: PKM2_ATTR_CONTAINER_FIRE,
    PKM2_ELE_TYPE_WATER: PKM2_ATTR_CONTAINER_WATER,
    PKM2_ELE_TYPE_GRASS: PKM2_ATTR_CONTAINER_GRASS,
    PKM2_ELE_TYPE_LIGHT: PKM2_ATTR_CONTAINER_LIGHT,
    PKM2_ELE_TYPE_DARK: PKM2_ATTR_CONTAINER_DARK,
    PKM2_ELE_TYPE_NONE: PKM2_ATTR_CONTAINER_GLOBAL,
}

MAP_JOBTYPE_ATTR_CONTAINER = {
    PKM2_JOB_TYPE_MAGIC: PKM2_ATTR_CONTAINER_MAGIC,
    PKM2_JOB_TYPE_PHY: PKM2_ATTR_CONTAINER_PHY,
    PKM2_JOB_TYPE_DEF: PKM2_ATTR_CONTAINER_DEF,
    PKM2_JOB_TYPE_AUXILIARY: PKM2_ATTR_CONTAINER_AUXILIARY,
}


#宠物属性组成模块
PET_ATTR_MODULE_ALL = 1 #全部
PET_ATTR_MODULE_INIT = 2 #初始属性
PET_ATTR_MODULE_LV_EVOLVE = 3 #等级属性 进化属性
PET_ATTR_MODULE_SKILL = 4 #技能
PET_ATTR_MODULE_PECULIARITY = 5 #特性
PET_ATTR_MODULE_EQUIP = 6 #装备
PET_ATTR_MODULE_YISHOU = 7 #异兽
PET_ATTR_MODULE_RELATION_1 = 8 #连协
PET_ATTR_MODULE_RELATION_2 = 9 #队伍加成
PET_ATTR_MODULE_RELATION_3 = 10 #羁绊 上阵激活
PET_ATTR_MODULE_RELATION_4 = 11 #羁绊 不上阵也激活


#战斗力组成类型
PKM2_FA_TYPE_1 = 1 #图鉴-火
PKM2_FA_TYPE_2 = 2 #图鉴-水
PKM2_FA_TYPE_3 = 3 #图鉴-草
PKM2_FA_TYPE_4 = 4 #图鉴-光
PKM2_FA_TYPE_5 = 5 #图鉴-暗
PKM2_FA_TYPE_6 = 6 #图鉴-总收集
PKM2_FA_TYPE_7 = 7 #法宝
PKM2_FA_TYPE_8 = 8 #神装
PKM2_FA_TYPE_9 = 9 #图腾
PKM2_FA_TYPE_10 = 10 #房子
PKM2_FA_TYPE_11 = 11 #称号
PKM2_FA_TYPE_12 = 12 #头像
PKM2_FA_TYPE_13 = 13 #边框


MAP_ELETYPE_ALBLUM_FA = {
    PKM2_ELE_TYPE_FIRE: PKM2_FA_TYPE_1,
    PKM2_ELE_TYPE_WATER: PKM2_FA_TYPE_2,
    PKM2_ELE_TYPE_GRASS: PKM2_FA_TYPE_3,
    PKM2_ELE_TYPE_LIGHT: PKM2_FA_TYPE_4,
    PKM2_ELE_TYPE_DARK: PKM2_FA_TYPE_5,
    PKM2_ELE_TYPE_NONE: PKM2_FA_TYPE_6,
}


QUESTION_NUM = 20   # 答题数量

# #充值http返回码 充值内部错误码
CHARGE_INSIDE_OK = 1                        #充值成功
CHARGE_INSIDE_ERR_NOT_FOUND_ID = 2          #未找到商品
CHARGE_INSIDE_ERR_RMB = 3                   #商品价格对不上
CHARGE_INSIDE_ERR_PLATFORMID = 4            #平台ID对不上
CHARGE_INSIDE_ERR_NOTFOUND_PLAYER = 5       #找不到玩家
CHARGE_INSIDE_ERR_NOTOPEN = 6               #活动时间未到
CHARGE_INSIDE_ERR_MODRES = 7                #没有模块资源
CHARGE_INSIDE_ERR_MODRESID = 7              #没有模块资源ID
CHARGE_INSIDE_ERR_MODDEF = 8                #没有模块处理方法


#背包初始化大小
PET_SIZE = 255
EQUIP_BAG_SIZE = 200
YI_SHOU_BAG_SIZE = 200

#各类物品最大资源编号
CURRENCY_MAX_NO = 999 #货币
PET_MAX_NO = 9999 #宠物
ITEM_MAX_NO = 199999 #道具
EQUIP_START_NO = 299999 #装备结束编号
YISHOU_EQUIP_START_NO = 1700000 #异兽装备起始编号
YISHOU_EQUIP_END_NO = 1799999 #异兽装备结束编号


#特殊货币道具id
CURRENCY_EXP = 1 #经验
CURRENCY_COIN = 2  # 银币
CURRENCY_BINDGOLD = 3  # 绑定元宝
CURRENCY_GOLD = 4  # 元宝
CURRENCY_GUILD_COIN = 5 #帮贡
CURRENCY_EXPLORE = 6  # 探索点 上限exploreMax
CURRENCY_FRIEND_COIN = 7 #好友币
CURRENCY_PETEXP = 8  # 宠物经验
CURRENCY_DAYLY_PVP_COIN = 20 #日常抢夺资金

#道具类型
ITEM_TYPE_CURRENCY = 1 #货币道具 Currency
ITEM_TYPE_NORMAL = 2 #普通道具 Nomal
ITEM_TYPE_BOX = 3 #宝箱道具 Box
ITEM_TYPE_SELECT_BOX = 7 #可选宝箱 SelectBoxItem
ITEM_TYPE_PET = 8 #宠物激活卡

#装备类型
EQUIP_TYPE_EQUIP = 2 # 2=白色到金色
EQUIP_TYPE_FABAO = 3 # 3=法宝
EQUIP_TYPE_SHENZHUANG = 16 # 16=人物神装
EQUIP_TYPE_YISHOU = 17 # 17=异兽之灵


#道具限时类型 1=指定某年某月某时某分结束 2=从生成时刻开始倒计时
ITEM_TIME_TYPE1 = 1
ITEM_TIME_TYPE2 = 2

#=============本地排行榜=============

#排行榜相关
RANK_SIZE = 100
RANK_TYPE_FA = 1    # 战力榜
RANK_TYPE_LV = 2    # 等级榜
RANK_TYPE_PET = 3   # 宠物总榜



RANK_TYPE_TX = 7    # 天仙榜
RANK_TYPE_SQ = 8    # 神兵榜


RANK_TYPE_LWBZ = 17 # 龙王宝藏榜
RANK_TYPE_XLYS = 18 # 小雷音寺榜
RANK_TYPE_TTSL = 19 # 天庭试炼榜
RANK_TYPE_MAP = 20 # 地图关卡排行榜

RANK_TYPE_PET_ALBUM = 26   # 宠物图鉴榜



RANK_TYPE_PET_QA_FA = 30 #所有激活宠物按种族值换算继承后的战力榜
RANK_HETI = 31 #合体排行榜
RANK_TYPE_ATTR_FA = 32 #属性池子战力榜
RANK_TYPE_COST = 33 #消费排行
RANK_TYPE_CHARGE = 34 #充值排行
RANK_TYPE_NEWYEAR_CHARGE = 35 #元旦充值排行
RANK_TYPE_CHARGE_HEFU = 36 #元旦充值排行 - 合服
RANK_TYPE_CATCHPET_HEFU = 37 #抓宠大赛积分排行 - 合服

RANK_MAX_TYPE = 37  #最大排行榜 读取数据库用

MAP_FA_RANK_TYPE = {

}


#=============跨服排行榜=============
CROSS_RANK_TYPE_PET_WATER = 1 # 水系宠物
CROSS_RANK_TYPE_PET_LIGHT = 2 # 光系宠物
CROSS_RANK_TYPE_PET_GRASS = 3 # 草系宠物
CROSS_RANK_TYPE_PET_DARK = 4 # 暗系宠物
CROSS_RANK_TYPE_PET_FIRE = 5 # 火系宠物
CROSS_RANK_TYPE_PET_BEST = 6 # 最强宠物
CROSS_RANK_TYPE_NEWYEAR_CHARGE = 7 #元旦充值排行
CROSS_RANK_TYPE_PET_WATER_HEFU = 11 # 合服水系宠物
CROSS_RANK_TYPE_PET_LIGHT_HEFU = 12 # 合服光系宠物
CROSS_RANK_TYPE_PET_GRASS_HEFU = 13 # 合服草系宠物
CROSS_RANK_TYPE_PET_DARK_HEFU = 14 # 合服暗系宠物
CROSS_RANK_TYPE_PET_FIRE_HEFU = 15 # 合服火系宠物
CROSS_RANK_TYPE_PET_BEST_HEFU = 16 # 合服最强宠物




#========物品添加原因===============
ITEM_ADD_GM = 1 #GM
ITEM_ADD_INIT = 2 #角色初始化
ITEM_ADD_OPEN_BOX = 3 #开宝箱
ITEM_ADD_MAP_REWARD = 4 #地图-物件
ITEM_ADD_MAP_OBJ = 5 #地图-物件
ITEM_ADD_FRIEND_RECEIVE = 6 # 好友接收
ITEM_ADD_PET_EVOLVE_BACK = 7 #宠物进化消耗返还
ITEM_ADD_MAIL_ATTACHMENT = 8  #邮件
ITEM_ADD_MARRY_POWER = 9 #结婚亲密度等级
ITEM_ADD_EXAM_REWARD = 10 # 答题奖励
ITEM_ADD_GRBOSS_REWARD = 11 #个人Boss
ITEM_ADD_QMBOSS_REWARD = 12 #全民boss
ITEM_ADD_YWBOSS_REWARD = 13 #野外boss
ITEM_ADD_SSJBOSS_REWARD = 14 #生死劫boss
ITEM_ADD_NIUDAN_ROLL = 15 #扭蛋
ITEM_ADD_ZHUANPAN_ROLL = 16 #转盘转
ITEM_ADD_NIUDAN_XIANSHI_REWARD = 17 #扭蛋-限时扭蛋奖励
ITEM_ADD_MAP_QUICK_FREE = 18 #地图-快速免费
ITEM_ADD_MAP_QUICK_USE = 18 #地图-快速收费
ITEM_ADD_CHARGE = 19 #充值
ITEM_ADD_MORMAL_SCENE_PASS = 20 #过关领奖
ITEM_ADD_MORMAL_SCENE_FIGHT = 21 #过关奖励
ITEM_ADD_RESCUE_REWARD = 22 #救援奖励
ITEM_ADD_RESCUE_SENT = 23 #派遣奖励
ITEM_ADD_COMPOUND = 24 #物品合成
ITEM_ADD_ENCOUNTER_FIGHT = 25 #遭遇战
ITEM_ADD_DAOGUAN_FIRST = 26 #道馆首通奖励
ITEM_ADD_DAOGUAN = 27 #道馆奖励
ITEM_ADD_ZHUANPAN_REWARD = 28 #转盘领奖
ITEM_ADD_SHOP = 29 #商店购买
ITEM_ADD_ZHUDAOXUNLI_REWARD = 30 #诸岛巡礼-奖励
ITEM_ADD_DAYLY_PVP_CHALLENGE_WIN = 31 #日常pvp挑战胜利
ITEM_ADD_DAYLY_PVP_REVENGE_WIN = 32 #日常pvp复仇胜利
ITEM_ADD_DAYLY_PVP_WINSTREAK_REWARD = 33 #日常pvp连胜奖励
ITEM_ADD_DAYLY_PVP_WEEK_RANK_REWARD = 34 #日常pvp周排行奖励
ITEM_ADD_DAYLY_PERSON_CHARGE = 35 #单人累积充值活动
ITEM_ADD_HETI_REWARD = 36 #合体
ITEM_ADD_GONGCHENG_LOGIN_REWARD = 37 #全民攻城 登陆奖励
ITEM_ADD_GONGCHENG_LIMIT_REWARD = 38 #全民攻城 限购礼包
ITEM_ADD_GONGCHENG_TASK_REWARD = 39 #全民攻城 任务奖励
ITEM_ADD_GONGCHENG_SHOP_REWARD = 40 #全民攻城 商店购买
ITEM_ADD_GONGCHENG_QUANMING_RANK = 41 #攻城全民排行榜
ITEM_ADD_GUILD_CREATE_FAIL = 42 # 创建公会失败返还
ITEM_ADD_GUILD_SX_FAIL = 43 #帮会上香失败返还
ITEM_ADD_GUILD_SX = 44 #帮会上香
ITEM_ADD_GUILD_SX_REWARD = 45 #领取帮会香火值奖励
ITEM_ADD_GUILD_ACT_UPGRADE = 46 #帮会活跃升级
ITEM_ADD_GUILD_EXCHANGE = 47 #帮会兑换
ITEM_ADD_GUILD_TASK = 48 #帮会任务
ITEM_ADD_GUILD_BARR_REWARD = 49 #帮会副本
ITEM_ADD_GUILD_ACT_TASK = 50 #帮会活跃任务
ITEM_ADD_HUSONGREWARD = 51 # 押镖护送奖励
ITEM_ADD_DIAOYUREWARD = 67 # 钓鱼奖励
ITEM_ADD_DIAOYU_ROBREWARD = 68 # 枪鱼奖励

#========物品消耗原因===============
ITEM_COST_OPEN_BOX = 1 #开宝箱
ITEM_COST_TOTEM_UPGRADE = 2 #图腾升级
ITEM_COST_TOTEM_ACT = 3 #图腾激活
ITEM_COST_PET_UPGRADE = 4 #宠物升级
ITEM_COST_PET_EVOLVE = 5 #宠物进化
ITEM_COST_MARRY_POWER = 6 #结婚亲密度赠送
ITEM_COST_MARRY_GIFT = 7 #结婚礼包
ITEM_COST_MARRY = 8 #结婚
ITEM_COST_HOUSE_UPGRADE = 9 #房子升阶
ITEM_COST_QMBOSS_BUY = 10 #全民boss购买挑战次数
ITEM_COST_QMBOSS_REBORN = 11 #全民boss复活
ITEM_COST_YWBOSS_FIGHT = 12 #野外boss挑战
ITEM_COST_CHENGHAO_MAKE = 13 #称号激活
ITEM_COST_CHENGHAO_UP = 14 #称号升级
ITEM_COST_MYHEAD_MAKE = 15 #头像激活
ITEM_COST_NIUDAN_ROLL = 16 #扭蛋
ITEM_COST_PET_WASH = 17 #宠物洗练
ITEM_COST_ZHUANPAN_ROLL = 18 #转盘
ITEM_COST_ZHUANPAN_RESET = 19 #转盘重置
ITEM_COST_SENT_REFRESH = 20 #派遣刷新
ITEM_COST_SENT_PET = 21 #派遣宠物
ITEM_COST_SENT_FAST = 22 #加速进度
ITEM_COST_COMPOUND = 23 #物品合成
ITEM_COST_ADD_BAGSIZE = 24 #装备背包扩容
ITEM_COST_DAOGUAN_BUG_NUM = 25 #道馆购买挑战次数
ITEM_COST_SHOP = 26 #商店购买
ITEM_COST_ZHUDAOXUNLI_BUYSOCRE = 27 #诸岛巡礼-购买分数
ITEM_COST_DAYLY_PVP_CHALLENGE_FAIL = 28 #pvp日常挑战被击败
ITEM_COST_DAYLY_PVP_BUY_CHALLENGE_NUM = 29 #pvp日常挑战购买次数
ITEM_COST_DAYLY_PVP_REFRESH = 30 #pvp日常挑战更换对手
ITEM_COST_HETI = 31 #合体购买
ITEM_COST_GONGCHENG_REBORN = 32 #攻城 复活消耗
ITEM_COST_CREATE_GUILD = 33 #创建帮会
ITEM_COST_GUILD_SX = 34 #帮会上香
ITEM_COST_GUILD_TASK_FINISH = 35 #帮会任务一键完成
ITEM_COST_GUILD_TASK_RESET = 36 #帮会任务重置
ITEM_COST_GUILD_DONATE = 37 #帮会捐献
ITEM_COST_GUILD_SKULL_UP = 38 #帮会技能升级
ITEM_COST_GUILD_EXCHANGE = 39 #帮会兑换
ITEM_COST_GUILD_EXCHANGE_REFE = 40#帮会兑换刷新




# 邮箱最大邮件数量
MAX_MAIL = 100

# 邮件状态
MAIL_STATUS_1 = 1   # 未读未领取
MAIL_STATUS_2 = 2   # 已读未领取
MAIL_STATUS_3 = 3   # 已读已领取

##========邮件模板===============

MAIL_ID_MARRY_REWARD = 1                # 结婚奖励
MAIL_ID_MARRY_GIFT = 2                  # 结婚礼金
MAIL_ID_MARRY_RETGIFT = 3               # 结婚回礼
MAIL_ID_DIVORCE = 4                     # 分手通知
MAIL_ID_ARENA_RANK_REWARD = 5           # 竞技场排名奖励
MAIL_ID_EXAM_REWARD = 6                 # 答题奖励
MAIL_ID_BAG_FULL = 7                    # 背包已满
MAIL_ID_BOSS_KILL_REWARD = 8            # 全民boss击杀奖励
MAIL_ID_BOSS_PART_REWARD = 9            # 全民boss参与奖励
MAIL_ID_MONTH_CARD_FULI = 10            # 月卡福利
MAIL_ID_WEEK_CARD_FULI = 11             # 周卡福利
MAIL_ID_MONTH_CARD_REWARD = 12          # 月卡奖励
MAIL_ID_WEEK_CARD_REWARD = 13           # 周卡奖励
MAIL_ID_SSJ_FIRST = 14                  # 生死劫首通奖励
MAIL_ID_LEICHONG = 15                   # 累充回馈
MAIL_ID_GODPET= 16                      # 神宠来袭
MAIL_ID_RANK_REWRAD = 17                # 排行榜奖励
MAIL_ID_SHITU_SHIFU_REWARD = 18         # 师徒-师傅-毕业奖励
MAIL_ID_SHITU_SHIFU_WANMEIREWARD = 19   # 师徒-师傅-毕业完美奖励
MAIL_ID_SHITU_TUDI_REWARD = 20          # 师徒-徒弟-毕业奖励
MAIL_ID_SHITU_TUDI_WANMEIREWARD = 21    # 师徒-徒弟-毕业完美奖励
MAIL_ID_SHITU_SHIFU_TASK = 22           # 师徒-师傅-徒弟完成任务奖励
MAIL_ID_DIAOYU_REWARD = 23              # 钓鱼-奖励
MAIL_ID_CYCLENIUDAN_RANK_REWARD = 24    # 限时扭蛋排行榜奖励
MAIL_ID_CLCYENIUDAN_BX_REWARD = 25      # 限时扭蛋宝箱奖励
MAIL_ID_JITIANFANLI_DAY_REWARD = 26     # 积天返利每日奖励
MAIL_ID_JITIANFANLI_SUPER_REWARD = 27   # 积天返利超级大奖
MAIL_ID_WAKUANG_DAY_REWARD = 28         # 挖矿日排
MAIL_ID_WAKUANG_MONTH_REWARD = 29       # 挖矿月排
MAIL_ID_TXDY_ROUNDROBIN_REWARD1 = 30    # 循环赛奖励(晋级16强)
MAIL_ID_TXDY_ROUNDROBIN_REWARD2 = 31    # 循环赛奖励(未能晋级)
MAIL_ID_TXDY_8_REWARD = 32              # 天下第一8强奖励
MAIL_ID_TXDY_4_REWARD = 33              # 天下第一4强奖励
MAIL_ID_TXDY_2_REWARD = 34              # 天下第一前2奖励
MAIL_ID_TXDY_1_REWARD = 35              # 天下第一冠军奖励
MAIL_ID_TXDY_BET = 36                   # 天下第一押注
MAIL_ID_KFBOSS_REWARD = 37              # 跨服boss
MAIL_ID_LINGYUANGOU = 38                # 0元购活动
MAIL_ID_CHARGESING = 39                 # 充值签到


MAIL_ID_KFKH_RANK_7001 = 40                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7001 = 41                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7002 = 42                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7002 = 43                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7003 = 44                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7003 = 45                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7004 = 46                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7004 = 47                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7005 = 48                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7005 = 49                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7006 = 50                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7006 = 51                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7007 = 52                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7007 = 53                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7008 = 54                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7008 = 55                 # 开服狂欢-非排行奖励

MAIL_ID_RANK_REWRAD_HETI = 56                # 排行榜奖励
MAIL_ID_RANK_HUALIDASAI = 57    # 华丽大赛

MAIL_ID_GONGCHENG_ATK_SUCC = 58    # 攻城-ATK_SUCC
MAIL_ID_GONGCHENG_DEF_FAIL = 59    # 攻城-DEF_FAIL
MAIL_ID_GONGCHENG_ATK_FAIL = 60    # 攻城-ATK_FAIL
MAIL_ID_GONGCHENG_DEF_SUCC = 61    # 攻城-DEF_SUCC

MAIL_ID_GONGCHENG_PERSON = 62    # 攻城个人榜
MAIL_ID_GONGCHENG_GUILD = 63    # 攻城公会榜
MAIL_ID_GONGCHENG_GUILDREWARD = 64    # 攻城占城奖励

MAIL_ID_KFKH_RANK_7009 = 65                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7009 = 66                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7010 = 67                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7010 = 68                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7011 = 69                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7011 = 70                 # 开服狂欢-非排行奖励
MAIL_ID_KFKH_RANK_7012 = 71                 # 开服狂欢-排行奖励
MAIL_ID_KFKH_NONE_7012 = 72                 # 开服狂欢-非排行奖励

#跨服排行榜奖励邮件
MAIL_ID_CROSS_RANK_1 = 73                 # 水系宠物-排行奖励
MAIL_ID_CROSS_NONE_1 = 74                 # 水系宠物-非排行奖励
MAIL_ID_CROSS_RANK_2 = 75                 # 光系宠物-排行奖励
MAIL_ID_CROSS_NONE_2 = 76                 # 光系宠物-非排行奖励
MAIL_ID_CROSS_RANK_3 = 77                 # 草系宠物-排行奖励
MAIL_ID_CROSS_NONE_3 = 78                 # 草系宠物-非排行奖励
MAIL_ID_CROSS_RANK_4 = 79                 # 暗系宠物-排行奖励
MAIL_ID_CROSS_NONE_4 = 80                 # 暗系宠物-非排行奖励
MAIL_ID_CROSS_RANK_5 = 81                 # 火系宠物-排行奖励
MAIL_ID_CROSS_NONE_5 = 82                 # 火系宠物-非排行奖励
MAIL_ID_CROSS_RANK_6 = 83                 # 最强宠物-排行奖励
MAIL_ID_CROSS_NONE_6 = 84                 # 最强宠物-非排行奖励

MAIL_ID_CROSS_RANK_1_HEFU = 85                 # 水系宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_1_HEFU = 86                 # 水系宠物-非排行奖励 合服
MAIL_ID_CROSS_RANK_2_HEFU = 87                 # 光系宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_2_HEFU = 88                 # 光系宠物-非排行奖励 合服
MAIL_ID_CROSS_RANK_3_HEFU = 89                 # 草系宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_3_HEFU = 90                 # 草系宠物-非排行奖励 合服
MAIL_ID_CROSS_RANK_4_HEFU = 91                 # 暗系宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_4_HEFU = 92                 # 暗系宠物-非排行奖励 合服
MAIL_ID_CROSS_RANK_5_HEFU = 93                 # 火系宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_5_HEFU = 94                 # 火系宠物-非排行奖励 合服
MAIL_ID_CROSS_RANK_6_HEFU = 95                 # 最强宠物-排行奖励 合服
MAIL_ID_CROSS_NONE_6_HEFU = 96                 # 最强宠物-非排行奖励 合服

# 20191024新增今日充值活动
MAIL_ID_TODAY_CHARGE_ACT = 100

#段位赛奖励邮件
MAIL_ID_LEVEL_CONTEST_RANK_1 = 101 #段位赛排名奖励 青铜
MAIL_ID_LEVEL_CONTEST_RANK_2 = 102 #段位赛排名奖励 白银
MAIL_ID_LEVEL_CONTEST_RANK_3 = 103 #段位赛排名奖励 黄金
MAIL_ID_LEVEL_CONTEST_RANK_4 = 104 #段位赛排名奖励 钻石
MAIL_ID_LEVEL_CONTEST_RANK_5 = 105 #段位赛排名奖励 王者


MAIL_ID_LEVEL_CONTEST_NONE_1 = 111 #段位赛参与奖励 青铜
MAIL_ID_LEVEL_CONTEST_NONE_2 = 112 #段位赛参与奖励 白银
MAIL_ID_LEVEL_CONTEST_NONE_3 = 113 #段位赛参与奖励 黄金
MAIL_ID_LEVEL_CONTEST_NONE_4 = 114 #段位赛参与奖励 钻石
MAIL_ID_LEVEL_CONTEST_NONE_5 = 115 #段位赛参与奖励 王者


MAIL_ID_COST_RANK = 116            # 消费排行-排行奖励
MAIL_ID_COST_RANK_NONE = 117       # 消费排行-非排行奖励
MAIL_ID_CHARGE_RANK = 118          # 充值排行-排行奖励
MAIL_ID_CHARGE_RANK_NONE = 119     # 充值排行-非排行奖励
MAIL_ID_CHRISTMASREWARD = 120         # 圣诞节邮件大奖

MAIL_ID_NEW_YEAR_RANK_REWRAD = 121                # 元旦活动排行榜奖励
MAIL_ID_NEW_YEAR_CROSS_RANK_REWRAD = 122          # 元旦活动跨服排行榜奖励

MAIL_ID_LIMIT_JITIANFANLI_DAY_REWARD = 123     # 限时积天返利每日奖励
MAIL_ID_LIMIT_JITIANFANLI_SUPER_REWARD = 124   # 限时积天返利超级大奖

MAIL_ID_CHARGE_RANK_HEFU = 125          # 充值排行-排行奖励-合服
MAIL_ID_CHARGE_RANK_NONE_HEFU = 126     # 充值排行-非排行奖励-合服

MAIL_ID_LEICHONG_HEFU = 127                   # 累充回馈-合服

MAIL_ID_CATCHPET_RANK_HEFU = 128          # 抓宠大赛-合服

MAIL_ID_GROUP_PK_ELE_REWARD = 129 #对决赛-元素段位奖励
MAIL_ID_GROUP_PK_LD_REWARD = 130 #对决赛-光暗段位奖励

MAIL_ID_GROUP_PK_ELE_FINAL_REWARD = 131 #对决赛-元素决赛奖励
MAIL_ID_GROUP_PK_LD_FINAL_REWARD = 132 #对决赛-光暗决赛奖励

MAIL_ID_ZHUDAOXUNLI_NOR_REWARD = 133 #诸岛巡礼



MAIL_ID_BOSS_KILL_REWARD_LK = 1001        # 全民boss击杀奖励 立刻发

#技能类型
SKILL_TYPE_1 = 1 #宠物技能

#技能子类型
SKILL_SUB_TYPE_1 = 1
SKILL_SUB_TYPE_99 = 99
SKILL_SUB_TYPE_200 = 200
SKILL_SUB_TYPE_299 = 299

#出战队伍类型
BATTLE_ARRAY_TYPE_NONE = 0 #未出战
BATTLE_ARRAY_TYPE_NORMAL = 1 #常规战斗


#出战阵位
BATTLE_ARRAY_POS_1 = 1
BATTLE_ARRAY_POS_2 = 2
BATTLE_ARRAY_POS_3 = 3
BATTLE_ARRAY_POS_4 = 4
BATTLE_ARRAY_POS_5 = 5
BATTLE_ARRAY_POS_6 = 6
BATTLE_ARRAY_POS_7 = 7
BATTLE_ARRAY_POS_8 = 8
BATTLE_ARRAY_POS_9 = 9

ALL_BATTLE_POS = (BATTLE_ARRAY_POS_1, BATTLE_ARRAY_POS_2, BATTLE_ARRAY_POS_3,
                  BATTLE_ARRAY_POS_4, BATTLE_ARRAY_POS_5, BATTLE_ARRAY_POS_6,
                  BATTLE_ARRAY_POS_7, BATTLE_ARRAY_POS_8, BATTLE_ARRAY_POS_9)

FIGHT_TEAM_RED = 1 #红方
FIGHT_TEAM_BLUE = 2 #蓝方

#副本类型
FIGHT_TYPE_100 = 100 #挂机Boss



#战斗单位类型
FIGHTER_TYPE_PET = 1 #宠物
FIGHTER_TYPE_MST = 2 #怪物

#行动模型执行类型
FIGHT_DO_TYPE_ORDER = 1 #顺序
FIGHT_DO_TYPE_CONCURRENCE = 2 #并发

#动作类型
FIGHT_ACTION_TYPE_0 = 0 #空节点
FIGHT_ACTION_TYPE_1 = 1 #攻击
FIGHT_ACTION_TYPE_2 = 2 #受击

FIGHT_ACTION_TYPE_9 = 9 #恢复

#伤害类型
FIGHT_DAMAGE_TYPE_1 = 1 #普通
FIGHT_DAMAGE_TYPE_2 = 2 #暴击
FIGHT_DAMAGE_TYPE_3 = 3 #克制
FIGHT_DAMAGE_TYPE_4 = 4 #闪避
FIGHT_DAMAGE_TYPE_5 = 5 #间接
FIGHT_DAMAGE_TYPE_6 = 6 #吸收


#战斗行动时机点
FIGHT_ACT_POINT_1 = 6
FIGHT_ACT_POINT_2 = 2

#战斗效果类型
FIGHT_EFFECT_TYPE_100 = 100 # 直接伤害-物理-n%的物理伤害(万分比)
FIGHT_EFFECT_TYPE_101 = 101 # 直接伤害-物理(1特效多伤害)
FIGHT_EFFECT_TYPE_102 = 102 # 直接伤害-物理(多段特效多段伤害)

FIGHT_EFFECT_TYPE_200 = 200 # 直接伤害-法术-n%的法术伤害(万分比)
FIGHT_EFFECT_TYPE_201 = 201 # 直接伤害-法术(多段特效多段伤害)
FIGHT_EFFECT_TYPE_202 = 202 # 直接伤害-法术(多段特效多段伤害)


FIGHT_EFFECT_TYPE_500 = 500 # 回血-施法者攻击力n%点血量(万分比)

FIGHT_EFFECT_TYPE_1402 = 1402 # 净化--净化所有负面状态(不可驱散状态除外)

FIGHT_EFFECT_TYPE_2200 = 2200 # 本次攻击临时提升-xx属性_xx点










#活动ID

ACTIVITY_FUHUANIUDAN = 10100 #孵化扭蛋
ACTIVITY_XIANSHINIUDAN = 10200 #限时扭蛋
ACTIVITY_ZHENYINGNIUDAN = 10300 #阵营扭蛋



ACTIVITY_CHARGE_YUANBAO = 1 #充值元宝 - 开服多少天数额外赠送(ID勿动)
ACTIVITY_CHARGE_MONTH = 2 #充值月卡 - 开服多少天数额外赠送(ID勿动)
ACTIVITY_XINYUNGZHUANGPAN = 5 # 幸运转盘
ACTIVITY_CHARGE_WEEK = 6 #充值周卡 - 开服多少天数额外赠送(ID勿动)
ACTIVITY_CHENGZHANGJIJIN = 7 #成长基金
ACTIVITY_TOUZIJIHUA = 8 #投资计划
ACTIVITY_LEICHONG = 9 #累充
ACTIVITY_SHENCHONGLAIXI = 10 #神宠来袭
ACTIVITY_QMCJ = 13 #全民冲级
ACTIVITY_MUBIAOJIANGLI = 14 #目标奖励
ACTIVITY_YABIAO = 16 #押镖
ACTIVITY_TUANGOU = 20 #团购
ACTIVITY_QMJJ = 21 #全民进阶z
ACTIVITY_JIERIFANLI = 17 #节日返利
ACTIVITY_SHENMISHANGDIAN1 = 18 #神秘商店1
ACTIVITY_HUANLEZADAN = 19 #节日返利
ACTIVITY_SHENMISHANGDIAN2 = 22 #神秘商店2
ACTIVITY_SHENMISHANGDIAN3 = 23 #神秘商店3
ACTIVITY_DIAOYU = 24 #钓鱼
ACTIVITY_WAKUANG = 25 #挖矿
ACTIVITY_NIUDAN2 = 26 #限时扭蛋
ACTIVITY_JITIANFANLI = 27 # 积表返利
ACTIVITY_DAYLY_PVP = 30 #日常pvp抢夺
ACTIVITY_KFBOSS = 34 #跨服BOSS
ACTIVITY_LINGYUANGOU = 42 #0元购买
ACTIVITY_WUJIANGLIBAO = 43 #武将礼包
ACTIVITY_CHONGWULIBAO = 44 #宠物礼包
ACTIVITY_TXDY_BET_TIME = 45 #天下第一 押注时间
ACTIVITY_XINGYUNTH = 48 #幸运转盘特惠
ACTIVITY_CHARGE_TLREWAD = 49 #充值限时奖励
ACTIVITY_ZIZHILIBAO = 50 #资质礼包
ACTIVITY_SHOULINGLIBAO = 51 #兽灵礼包
ACTIVITY_LEICHONGGIFT = 52 #累充礼包
ACTIVITY_VIPDAYREWARD = 53 #vip每日奖励双倍
ACTIVITY_SHOULINGSHOP = 54 #vip兽灵商店优惠
ACTIVITY_APPOINTEDTIMEREWARD = 55 #小单车特别奖
ACTIVITY_QIANGGOU_GIFT_1 = 56 #抢购礼包1
ACTIVITY_QIANGGOU_GIFT_2 = 57 #抢购礼包2
ACTIVITY_SHAHULEYUAN_GIFT = 58 #沙狐乐园推送礼包
ACTIVITY_ZHOUMOLIBAO_GIFT = 59 #周末礼包
ACTIVITY_THANKSGIVING_DAY = 60 #感恩节活动
ACTIVITY_LEVEL_CONTEST = 61 #段位赛
ACTIVITY_LEVEL_CONTEST_TASK = 62 #段位赛任务
ACTIVITY_DAYLY_PERSON_CHARGE = 63 #单人累积充值天数活动（天天返利）
ACTIVITY_CHARGE_RANK = 64 #充值排行
ACTIVITY_COST_RANK = 65 #消费排行
ACTIVITY_CHRISTMAS_DROP = 66 #圣诞活动掉落用
ACTIVITY_SPEC_PET_OPEN = 67 #特典宠物功能开启
ACTIVITY_DAY_SINGLE_CHARGE = 68 #每日单笔
ACTIVITY_LIMIT_LEICHONG = 69 #限时累充
ACTIVITY_NEWYEAR_RANK_OPEN = 70 #元旦排行活动
ACTIVITY_LIMIT_JTFL = 71 #限时积天返利
ACTIVITY_SHAHULEYUAN_LUCKY = 72 #幸运乐园
ACTIVITY_SUPERREBATE = 73 #超级返利

ACTIVITY_CHINESENEWYEAR_XINGYUNQIAN = 74	#春节幸运签
ACTIVITY_CHINESENEWYEAR_TASK = 75	#春节任务
ACTIVITY_CHINESENEWYEAR_DAYBUY = 76	#春节每日秒杀
ACTIVITY_CHINESENEWYEAR_SKIN = 77	#春节换装
ACTIVITY_CHINESENEWYEAR_PK = 78	#春节pk赛
ACTIVITY_CHINESENEWYEAR_REDPACKET = 79	#春节红包

ACTIVITY_CLIENT_HEFU = 81	#合服进行提示
ACTIVITY_LOGINREWARD_HEFU = 82	#合服登陆
ACTIVITY_CHARGE_RANK_HEFU = 83	#充值排行 RANK_TYPE_CHARGE_HEFU
ACTIVITY_LEICHONG_HEFU = 84	#合服充值
ACTIVITY_BESTPET_HEFU = 85	#最强宠物--跨服
ACTIVITY_CATCHPET_RANK_HEFU = 86	#抓宠大赛
ACTIVITY_ARENA_HEFU = 87	#合服竞技
ACTIVITY_LEVELCONTEST_HEFU = 88	#段位争霸--跨服
ACTIVITY_CHARGE_X2_RESET_HEFU = 89	#重置双倍
ACTIVITY_DIAMOND_MINING = 90 #钻石挖矿
ACTIVITY_GROUP_PK = 91 #对决赛
ACTIVITY_CHARGE_STAR = 92 #星盘

ACTIVITY_CHINESENEWYEAR2_XINGYUNQIAN = 93	#愚人节幸运签
ACTIVITY_CHINESENEWYEAR2_TASK = 94	#愚人节任务
ACTIVITY_CHINESENEWYEAR2_DAYBUY = 95	#愚人节每日秒杀
ACTIVITY_CHINESENEWYEAR2_PK = 96	#愚人节pk赛
ACTIVITY_CHINESENEWYEAR2_ALL = 97	#愚人节 前端



KUAFU_YABIAO = 1 #跨服活动-押镖
KUAFU_DIAOYU = 2 #跨服活动-钓鱼
KUAFU_WAKUANG = 3 #跨服活动-挖矿
KUAFU_BOSS = 4 #跨服活动-BOSS


#功能开启ID，对应open配置表

#道馆
DAOGUAN_OPEN_ID = 4030



#帮会权限 1 = 帮主 2 = 副帮主 3 = 成员
GUILD_MEMBER_TYPE_1 = 1
GUILD_MEMBER_TYPE_2 = 2
GUILD_MEMBER_TYPE_3 = 3

#帮会日志 1=加入帮会 2=退出帮会 3=被踢 4=升职 5=降职 6=禅让
GUILD_LOG_TYPE_1 = 1
GUILD_LOG_TYPE_2 = 2
GUILD_LOG_TYPE_3 = 3
GUILD_LOG_TYPE_4 = 4
GUILD_LOG_TYPE_5 = 5
GUILD_LOG_TYPE_6 = 6

#帮会操作 1=禅让 2=升职 3=降职 4=踢出
GUILD_OPER_TYPE_1 = 1
GUILD_OPER_TYPE_2 = 2
GUILD_OPER_TYPE_3 = 3
GUILD_OPER_TYPE_4 = 4

#帮会任务类型 1=采集 2=打怪
GUILD_TASK_TYPE_1 = 1
GUILD_TASK_TYPE_2 = 2

#帮会技能类型
GUILD_SKILL_TYPE_1 = 1
GUILD_SKILL_TYPE_2 = 2
GUILD_SKILL_TYPE_3 = 3
GUILD_SKILL_TYPE_4 = 4
GUILD_SKILL_TYPE_5 = 5
GUILD_SKILL_TYPE_6 = 6
GUILD_SKILL_TYPE_7 = 7
GUILD_SKILL_TYPE_8 = 8

ALL_GUILD_SKILL = (GUILD_SKILL_TYPE_1, GUILD_SKILL_TYPE_2, GUILD_SKILL_TYPE_3, GUILD_SKILL_TYPE_4,
                   GUILD_SKILL_TYPE_5, GUILD_SKILL_TYPE_6, GUILD_SKILL_TYPE_7 ,GUILD_SKILL_TYPE_8)

