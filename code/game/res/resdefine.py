

# ssjBoss
class ResSsjBoss(object):
	RES_TABLE = "ssjBoss"
	__slots__ = ("id","grade","group","lv","fbId","mstId","firstReward","mailId",)

	def __init__(self):
		
		# id 生死劫boss表
		self.id = 0
		
		# grade 难度
		self.grade = 0
		
		# group 章数
		self.group = 0
		
		# lv 节数
		self.lv = 0
		
		# fbId 副本id
		self.fbId = 0
		
		# mstId 怪物id
		self.mstId = 0
		
		# firstReward 全服首通奖励
		self.firstReward = {}
		
		# mailId 全服首通邮件模板id
		self.mailId = 0
		

	def load_from_json(self, data):
		
		# id 生死劫boss表
		self.id = data.get("id",0)
		
		# grade 难度
		self.grade = data.get("grade",0)
		
		# group 章数
		self.group = data.get("group",0)
		
		# lv 节数
		self.lv = data.get("lv",0)
		
		# fbId 副本id
		self.fbId = data.get("fbId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# firstReward 全服首通奖励
		self.arrayint2tomap("firstReward", data.get("firstReward",[]))
		
		# mailId 全服首通邮件模板id
		self.mailId = data.get("mailId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# grBoss
class ResGrBoss(object):
	RES_TABLE = "grBoss"
	__slots__ = ("id","fbId","mstId",)

	def __init__(self):
		
		# id 个人boss表
		self.id = 0
		
		# fbId 副本id
		self.fbId = 0
		
		# mstId 怪物id
		self.mstId = 0
		

	def load_from_json(self, data):
		
		# id 个人boss表
		self.id = data.get("id",0)
		
		# fbId 副本id
		self.fbId = data.get("fbId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# kfbossrank
class ResKfbossrank(object):
	RES_TABLE = "kfbossrank"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id 跨服boss排行
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 跨服boss排行
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# ywBoss
class ResYwBoss(object):
	RES_TABLE = "ywBoss"
	__slots__ = ("id","actDesc","refreshDesc","fbId","mstId","stTime","endTime","interval","runaway","occupy","cost","refresh","refresh2","spec",)

	def __init__(self):
		
		# id 野外boss表
		self.id = 0
		
		# actDesc 活动说明
		self.actDesc = ""
		
		# refreshDesc 刷新说明
		self.refreshDesc = ""
		
		# fbId 副本id
		self.fbId = 0
		
		# mstId 怪物id
		self.mstId = 0
		
		# stTime boss开启时间
		self.stTime = ""
		
		# endTime boss结束时间
		self.endTime = ""
		
		# interval boss间隔时间(秒)
		self.interval = 0
		
		# runaway boss逃跑时间(秒)
		self.runaway = 0
		
		# occupy boss占领时间(秒)
		self.occupy = 0
		
		# cost 进入消耗
		self.cost = {}
		
		# refresh boss刷新时间
		self.refresh = []
		
		# refresh2 boss刷新时间（客户端用）
		self.refresh2 = []
		
		# spec 是否特殊
		self.spec = 0
		

	def load_from_json(self, data):
		
		# id 野外boss表
		self.id = data.get("id",0)
		
		# actDesc 活动说明
		self.actDesc = data.get("actDesc","")
		
		# refreshDesc 刷新说明
		self.refreshDesc = data.get("refreshDesc","")
		
		# fbId 副本id
		self.fbId = data.get("fbId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# stTime boss开启时间
		self.stTime = data.get("stTime","")
		
		# endTime boss结束时间
		self.endTime = data.get("endTime","")
		
		# interval boss间隔时间(秒)
		self.interval = data.get("interval",0)
		
		# runaway boss逃跑时间(秒)
		self.runaway = data.get("runaway",0)
		
		# occupy boss占领时间(秒)
		self.occupy = data.get("occupy",0)
		
		# cost 进入消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# refresh boss刷新时间
		self.refresh = data.get("refresh",[])
		
		# refresh2 boss刷新时间（客户端用）
		self.refresh2 = data.get("refresh2",[])
		
		# spec 是否特殊
		self.spec = data.get("spec",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# qmBoss
class ResQmBoss(object):
	RES_TABLE = "qmBoss"
	__slots__ = ("id","fbId","mstId","cdtime","relive","tzReward","killReward","rankfirstReward","rankReward","cost1","cost2","cost3","cost4","cost5","lkmailReward",)

	def __init__(self):
		
		# id 全民boss表
		self.id = 0
		
		# fbId 副本id
		self.fbId = 0
		
		# mstId 怪物id
		self.mstId = 0
		
		# cdtime 复活CD（秒）
		self.cdtime = 0
		
		# relive 是否可手动复活
		self.relive = 0
		
		# tzReward 挑战奖励
		self.tzReward = 0
		
		# killReward 击杀奖励
		self.killReward = 0
		
		# rankfirstReward 排名第一奖励
		self.rankfirstReward = 0
		
		# rankReward 其他排名奖励
		self.rankReward = 0
		
		# cost1 复活材料1
		self.cost1 = {}
		
		# cost2 复活材料2
		self.cost2 = {}
		
		# cost3 复活材料3
		self.cost3 = {}
		
		# cost4 复活材料4
		self.cost4 = {}
		
		# cost5 复活材料5
		self.cost5 = {}
		
		# lkmailReward 击杀邮件奖励
		self.lkmailReward = {}
		

	def load_from_json(self, data):
		
		# id 全民boss表
		self.id = data.get("id",0)
		
		# fbId 副本id
		self.fbId = data.get("fbId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# cdtime 复活CD（秒）
		self.cdtime = data.get("cdtime",0)
		
		# relive 是否可手动复活
		self.relive = data.get("relive",0)
		
		# tzReward 挑战奖励
		self.tzReward = data.get("tzReward",0)
		
		# killReward 击杀奖励
		self.killReward = data.get("killReward",0)
		
		# rankfirstReward 排名第一奖励
		self.rankfirstReward = data.get("rankfirstReward",0)
		
		# rankReward 其他排名奖励
		self.rankReward = data.get("rankReward",0)
		
		# cost1 复活材料1
		self.arrayint2tomap("cost1", data.get("cost1",[]))
		
		# cost2 复活材料2
		self.arrayint2tomap("cost2", data.get("cost2",[]))
		
		# cost3 复活材料3
		self.arrayint2tomap("cost3", data.get("cost3",[]))
		
		# cost4 复活材料4
		self.arrayint2tomap("cost4", data.get("cost4",[]))
		
		# cost5 复活材料5
		self.arrayint2tomap("cost5", data.get("cost5",[]))
		
		# lkmailReward 击杀邮件奖励
		self.arrayint2tomap("lkmailReward", data.get("lkmailReward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# kfBoss
class ResKfBoss(object):
	RES_TABLE = "kfBoss"
	__slots__ = ("id","fbId","mstId","name","localpet","remotepet","touchReward","shieldReward","killReward","min","max","baoxiangReward","cost","makeShield",)

	def __init__(self):
		
		# id 跨服boss表
		self.id = 0
		
		# fbId 副本id
		self.fbId = 0
		
		# mstId 怪物id
		self.mstId = 0
		
		# name 怪物名字
		self.name = ""
		
		# localpet 本服协助宠物池
		self.localpet = {}
		
		# remotepet 跨服协助宠物池
		self.remotepet = {}
		
		# touchReward 触碰奖励
		self.touchReward = 0
		
		# shieldReward 破盾奖励
		self.shieldReward = {}
		
		# killReward 击杀奖励
		self.killReward = {}
		
		# min 宝箱最小数量
		self.min = 0
		
		# max 宝箱最大数量
		self.max = 0
		
		# baoxiangReward 宝箱
		self.baoxiangReward = {}
		
		# cost 复活材料
		self.cost = {}
		
		# makeShield 生成盾百分比点
		self.makeShield = []
		

	def load_from_json(self, data):
		
		# id 跨服boss表
		self.id = data.get("id",0)
		
		# fbId 副本id
		self.fbId = data.get("fbId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# name 怪物名字
		self.name = data.get("name","")
		
		# localpet 本服协助宠物池
		self.arrayint2tomap("localpet", data.get("localpet",[]))
		
		# remotepet 跨服协助宠物池
		self.arrayint2tomap("remotepet", data.get("remotepet",[]))
		
		# touchReward 触碰奖励
		self.touchReward = data.get("touchReward",0)
		
		# shieldReward 破盾奖励
		self.arrayint2tomap("shieldReward", data.get("shieldReward",[]))
		
		# killReward 击杀奖励
		self.arrayint2tomap("killReward", data.get("killReward",[]))
		
		# min 宝箱最小数量
		self.min = data.get("min",0)
		
		# max 宝箱最大数量
		self.max = data.get("max",0)
		
		# baoxiangReward 宝箱
		self.arrayint2tomap("baoxiangReward", data.get("baoxiangReward",[]))
		
		# cost 复活材料
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# makeShield 生成盾百分比点
		self.makeShield = data.get("makeShield",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildSxBar
class ResGuildSxBar(object):
	RES_TABLE = "guildSxBar"
	__slots__ = ("id","num","reward",)

	def __init__(self):
		
		# id 帮会上香进度奖励
		self.id = 0
		
		# num 目标值
		self.num = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 帮会上香进度奖励
		self.id = data.get("id",0)
		
		# num 目标值
		self.num = data.get("num",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildlv
class ResGuildlv(object):
	RES_TABLE = "guildlv"
	__slots__ = ("lv","fund","deputybossnum","peoplenum","vip","cost","skillMax","guildSxNum","sxMaxNum","exchange","CityS","CityM","CityL",)

	def __init__(self):
		
		# lv 帮会表
		self.lv = 0
		
		# fund 资金
		self.fund = 0
		
		# deputybossnum 副帮人数
		self.deputybossnum = 0
		
		# peoplenum 人数
		self.peoplenum = 0
		
		# vip 创建vip等级条件
		self.vip = 0
		
		# cost 创建消耗
		self.cost = {}
		
		# skillMax 帮会技能等级上限
		self.skillMax = 0
		
		# guildSxNum 帮会上香最大次数
		self.guildSxNum = 0
		
		# sxMaxNum 帮会最大香火值
		self.sxMaxNum = 0
		
		# exchange 帮会兑换
		self.exchange = {}
		
		# CityS 能占领城市级别上限
		self.CityS = 0
		
		# CityM 能占领城市级别上限
		self.CityM = 0
		
		# CityL 能占领城市级别上限
		self.CityL = 0
		

	def load_from_json(self, data):
		
		# lv 帮会表
		self.lv = data.get("lv",0)
		
		# fund 资金
		self.fund = data.get("fund",0)
		
		# deputybossnum 副帮人数
		self.deputybossnum = data.get("deputybossnum",0)
		
		# peoplenum 人数
		self.peoplenum = data.get("peoplenum",0)
		
		# vip 创建vip等级条件
		self.vip = data.get("vip",0)
		
		# cost 创建消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# skillMax 帮会技能等级上限
		self.skillMax = data.get("skillMax",0)
		
		# guildSxNum 帮会上香最大次数
		self.guildSxNum = data.get("guildSxNum",0)
		
		# sxMaxNum 帮会最大香火值
		self.sxMaxNum = data.get("sxMaxNum",0)
		
		# exchange 帮会兑换
		self.arrayint2tomap("exchange", data.get("exchange",[]))
		
		# CityS 能占领城市级别上限
		self.CityS = data.get("CityS",0)
		
		# CityM 能占领城市级别上限
		self.CityM = data.get("CityM",0)
		
		# CityL 能占领城市级别上限
		self.CityL = data.get("CityL",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildSx
class ResGuildSx(object):
	RES_TABLE = "guildSx"
	__slots__ = ("id","addExp","addNum","cost","reward",)

	def __init__(self):
		
		# id 帮会上香
		self.id = 0
		
		# addExp 增加帮会资金
		self.addExp = 0
		
		# addNum 增加香火值
		self.addNum = 0
		
		# cost 消耗
		self.cost = {}
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 帮会上香
		self.id = data.get("id",0)
		
		# addExp 增加帮会资金
		self.addExp = data.get("addExp",0)
		
		# addNum 增加香火值
		self.addNum = data.get("addNum",0)
		
		# cost 消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildBarr
class ResGuildBarr(object):
	RES_TABLE = "guildBarr"
	__slots__ = ("id","lv","barrId","mstId",)

	def __init__(self):
		
		# id 帮会副本表
		self.id = 0
		
		# lv 帮会开放等级
		self.lv = 0
		
		# barrId 副本id
		self.barrId = 0
		
		# mstId 怪物id(形象展示）
		self.mstId = 0
		

	def load_from_json(self, data):
		
		# id 帮会副本表
		self.id = data.get("id",0)
		
		# lv 帮会开放等级
		self.lv = data.get("lv",0)
		
		# barrId 副本id
		self.barrId = data.get("barrId",0)
		
		# mstId 怪物id(形象展示）
		self.mstId = data.get("mstId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildTask
class ResGuildTask(object):
	RES_TABLE = "guildTask"
	__slots__ = ("id","type","condition","minLv","maxLv","resetCost","finishCost","rewardArrayint2","arg1","arg2",)

	def __init__(self):
		
		# id 帮会任务表
		self.id = 0
		
		# type 类型
		self.type = 0
		
		# condition 条件
		self.condition = 0
		
		# minLv 帮会最小等级
		self.minLv = 0
		
		# maxLv 帮会最大等级
		self.maxLv = 0
		
		# resetCost 任务重置消耗
		self.resetCost = {}
		
		# finishCost 一键完成消耗
		self.finishCost = {}
		
		# rewardArrayint2 奖励）
		self.rewardArrayint2 = {}
		
		# arg1 参数1
		self.arg1 = ""
		
		# arg2 参数2
		self.arg2 = ""
		

	def load_from_json(self, data):
		
		# id 帮会任务表
		self.id = data.get("id",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# condition 条件
		self.condition = data.get("condition",0)
		
		# minLv 帮会最小等级
		self.minLv = data.get("minLv",0)
		
		# maxLv 帮会最大等级
		self.maxLv = data.get("maxLv",0)
		
		# resetCost 任务重置消耗
		self.arrayint2tomap("resetCost", data.get("resetCost",[]))
		
		# finishCost 一键完成消耗
		self.arrayint2tomap("finishCost", data.get("finishCost",[]))
		
		# rewardArrayint2 奖励）
		self.arrayint2tomap("rewardArrayint2", data.get("rewardArrayint2",[]))
		
		# arg1 参数1
		self.arg1 = data.get("arg1","")
		
		# arg2 参数2
		self.arg2 = data.get("arg2","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildAct
class ResGuildAct(object):
	RES_TABLE = "guildAct"
	__slots__ = ("id","exp","attr","reward",)

	def __init__(self):
		
		# id 帮会活跃表
		self.id = 0
		
		# exp 升级经验
		self.exp = 0
		
		# attr 属性
		self.attr = {}
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 帮会活跃表
		self.id = data.get("id",0)
		
		# exp 升级经验
		self.exp = data.get("exp",0)
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# guildSkill
class ResGuildSkill(object):
	RES_TABLE = "guildSkill"
	__slots__ = ("id","skillId","lv","cost","attr",)

	def __init__(self):
		
		# id 帮会技能表
		self.id = 0
		
		# skillId 技能id
		self.skillId = 0
		
		# lv 技能等级
		self.lv = 0
		
		# cost 升级消耗道具
		self.cost = {}
		
		# attr 属性
		self.attr = {}
		

	def load_from_json(self, data):
		
		# id 帮会技能表
		self.id = data.get("id",0)
		
		# skillId 技能id
		self.skillId = data.get("skillId",0)
		
		# lv 技能等级
		self.lv = data.get("lv",0)
		
		# cost 升级消耗道具
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# chargeSent
class ResChargeSent(object):
	RES_TABLE = "chargeSent"
	__slots__ = ("id","reward","day","baodi",)

	def __init__(self):
		
		# id 充值快速战斗表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		
		# day 特权天数
		self.day = 0
		
		# baodi 特权保底第n次必出x星任务
		self.baodi = {}
		

	def load_from_json(self, data):
		
		# id 充值快速战斗表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# day 特权天数
		self.day = data.get("day",0)
		
		# baodi 特权保底第n次必出x星任务
		self.arrayint2tomap("baodi", data.get("baodi",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# charge
class ResCharge(object):
	RES_TABLE = "charge"
	__slots__ = ("id","type","typeid","platformId","os","rmb","exp","itemId",)

	def __init__(self):
		
		# id 充值表
		self.id = 0
		
		# type 类型
		self.type = ""
		
		# typeid 充值类型表id
		self.typeid = 0
		
		# platformId 平台
		self.platformId = 0
		
		# os 系统类型
		self.os = 0
		
		# rmb 人名币（单位：分）
		self.rmb = 0
		
		# exp 增加VIP经验
		self.exp = 0
		
		# itemId 平台道具id
		self.itemId = []
		

	def load_from_json(self, data):
		
		# id 充值表
		self.id = data.get("id",0)
		
		# type 类型
		self.type = data.get("type","")
		
		# typeid 充值类型表id
		self.typeid = data.get("typeid",0)
		
		# platformId 平台
		self.platformId = data.get("platformId",0)
		
		# os 系统类型
		self.os = data.get("os",0)
		
		# rmb 人名币（单位：分）
		self.rmb = data.get("rmb",0)
		
		# exp 增加VIP经验
		self.exp = data.get("exp",0)
		
		# itemId 平台道具id
		self.itemId = data.get("itemId",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# chargeQuick
class ResChargeQuick(object):
	RES_TABLE = "chargeQuick"
	__slots__ = ("id","reward","day",)

	def __init__(self):
		
		# id 充值快速战斗表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		
		# day 特权天数
		self.day = 0
		

	def load_from_json(self, data):
		
		# id 充值快速战斗表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# day 特权天数
		self.day = data.get("day",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# chargeDaily
class ResChargeDaily(object):
	RES_TABLE = "chargeDaily"
	__slots__ = ("id","reward","max",)

	def __init__(self):
		
		# id 充值快速战斗表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		
		# max 当前充值表数量
		self.max = 0
		

	def load_from_json(self, data):
		
		# id 充值快速战斗表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# max 当前充值表数量
		self.max = data.get("max",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# chargeMonth
class ResChargeMonth(object):
	RES_TABLE = "chargeMonth"
	__slots__ = ("id","reward","day",)

	def __init__(self):
		
		# id 充值快速战斗表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		
		# day 特权天数
		self.day = 0
		

	def load_from_json(self, data):
		
		# id 充值快速战斗表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# day 特权天数
		self.day = data.get("day",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petwashstar
class ResPetwashstar(object):
	RES_TABLE = "petwashstar"
	__slots__ = ("id","cnt",)

	def __init__(self):
		
		# id 宠物洗练星级表
		self.id = 0
		
		# cnt 升星需要次数
		self.cnt = 0
		

	def load_from_json(self, data):
		
		# id 宠物洗练星级表
		self.id = data.get("id",0)
		
		# cnt 升星需要次数
		self.cnt = data.get("cnt",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petwash
class ResPetwash(object):
	RES_TABLE = "petwash"
	__slots__ = ("id","petId","star","private","peculiarity",)

	def __init__(self):
		
		# id 宠物洗练表
		self.id = 0
		
		# petId 宠物id
		self.petId = 0
		
		# star 洗练星级
		self.star = 0
		
		# private 专属池子
		self.private = 0
		
		# peculiarity 普通特性池子
		self.peculiarity = 0
		

	def load_from_json(self, data):
		
		# id 宠物洗练表
		self.id = data.get("id",0)
		
		# petId 宠物id
		self.petId = data.get("petId",0)
		
		# star 洗练星级
		self.star = data.get("star",0)
		
		# private 专属池子
		self.private = data.get("private",0)
		
		# peculiarity 普通特性池子
		self.peculiarity = data.get("peculiarity",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# pet
class ResPet(object):
	RES_TABLE = "pet"
	__slots__ = ("id","name","mutexList","washSatr","normal","skills","peculiarity","cost","quality","attr","eleType","eleVal","job","jobName","relation",)

	def __init__(self):
		
		# id 宠物表
		self.id = 0
		
		# name 名称
		self.name = ""
		
		# mutexList 上阵互斥宠物列表
		self.mutexList = []
		
		# washSatr 默认洗练星级
		self.washSatr = 0
		
		# normal 普攻技能
		self.normal = 0
		
		# skills 初始技能列表
		self.skills = {}
		
		# peculiarity 初始特性列表
		self.peculiarity = []
		
		# cost 激活材料
		self.cost = {}
		
		# quality 品质
		self.quality = 0
		
		# attr 初始属性
		self.attr = {}
		
		# eleType 五行属性类型
		self.eleType = 0
		
		# eleVal 五行属性值
		self.eleVal = 0
		
		# job 职业
		self.job = 0
		
		# jobName 职业名称
		self.jobName = ""
		
		# relation 关系类型
		self.relation = []
		

	def load_from_json(self, data):
		
		# id 宠物表
		self.id = data.get("id",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# mutexList 上阵互斥宠物列表
		self.mutexList = data.get("mutexList",[])
		
		# washSatr 默认洗练星级
		self.washSatr = data.get("washSatr",0)
		
		# normal 普攻技能
		self.normal = data.get("normal",0)
		
		# skills 初始技能列表
		self.arrayint2tomap("skills", data.get("skills",[]))
		
		# peculiarity 初始特性列表
		self.peculiarity = data.get("peculiarity",[])
		
		# cost 激活材料
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# attr 初始属性
		self.attr = data.get("attr",{})
		
		# eleType 五行属性类型
		self.eleType = data.get("eleType",0)
		
		# eleVal 五行属性值
		self.eleVal = data.get("eleVal",0)
		
		# job 职业
		self.job = data.get("job",0)
		
		# jobName 职业名称
		self.jobName = data.get("jobName","")
		
		# relation 关系类型
		self.relation = data.get("relation",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petwashpool
class ResPetwashpool(object):
	RES_TABLE = "petwashpool"
	__slots__ = ("id","group","skill","rate",)

	def __init__(self):
		
		# id 宠物洗练池
		self.id = 0
		
		# group 池子组
		self.group = 0
		
		# skill 技能id
		self.skill = 0
		
		# rate 权重
		self.rate = 0
		

	def load_from_json(self, data):
		
		# id 宠物洗练池
		self.id = data.get("id",0)
		
		# group 池子组
		self.group = data.get("group",0)
		
		# skill 技能id
		self.skill = data.get("skill",0)
		
		# rate 权重
		self.rate = data.get("rate",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petrelationship1
class ResPetrelationship1(object):
	RES_TABLE = "petrelationship1"
	__slots__ = ("id","passID","limit","skill1","skill2","skill3","skill4","skill5",)

	def __init__(self):
		
		# id 连协技能
		self.id = 0
		
		# passID 跳过上阵限制条件
		self.passID = 0
		
		# limit 对应条件
		self.limit = []
		
		# skill1 连协技能id
		self.skill1 = 0
		
		# skill2 连协技能id
		self.skill2 = 0
		
		# skill3 连协技能id
		self.skill3 = 0
		
		# skill4 连协技能id
		self.skill4 = 0
		
		# skill5 连协技能id
		self.skill5 = 0
		

	def load_from_json(self, data):
		
		# id 连协技能
		self.id = data.get("id",0)
		
		# passID 跳过上阵限制条件
		self.passID = data.get("passID",0)
		
		# limit 对应条件
		self.limit = data.get("limit",[])
		
		# skill1 连协技能id
		self.skill1 = data.get("skill1",0)
		
		# skill2 连协技能id
		self.skill2 = data.get("skill2",0)
		
		# skill3 连协技能id
		self.skill3 = data.get("skill3",0)
		
		# skill4 连协技能id
		self.skill4 = data.get("skill4",0)
		
		# skill5 连协技能id
		self.skill5 = data.get("skill5",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petrelationship2
class ResPetrelationship2(object):
	RES_TABLE = "petrelationship2"
	__slots__ = ("id","group","lv","limit1","limit2","limit3","addall","addele","addjob","addrelation","addAttr",)

	def __init__(self):
		
		# id 队伍加成
		self.id = 0
		
		# group 分组
		self.group = 0
		
		# lv 等级
		self.lv = 0
		
		# limit1 对应条件
		self.limit1 = {}
		
		# limit2 对应条件
		self.limit2 = {}
		
		# limit3 对应条件
		self.limit3 = {}
		
		# addall 是否加全体
		self.addall = 0
		
		# addele 元素增益
		self.addele = []
		
		# addjob 职业增益
		self.addjob = []
		
		# addrelation 其他增益
		self.addrelation = []
		
		# addAttr 增加属性
		self.addAttr = {}
		

	def load_from_json(self, data):
		
		# id 队伍加成
		self.id = data.get("id",0)
		
		# group 分组
		self.group = data.get("group",0)
		
		# lv 等级
		self.lv = data.get("lv",0)
		
		# limit1 对应条件
		self.arrayint2tomap("limit1", data.get("limit1",[]))
		
		# limit2 对应条件
		self.arrayint2tomap("limit2", data.get("limit2",[]))
		
		# limit3 对应条件
		self.arrayint2tomap("limit3", data.get("limit3",[]))
		
		# addall 是否加全体
		self.addall = data.get("addall",0)
		
		# addele 元素增益
		self.addele = data.get("addele",[])
		
		# addjob 职业增益
		self.addjob = data.get("addjob",[])
		
		# addrelation 其他增益
		self.addrelation = data.get("addrelation",[])
		
		# addAttr 增加属性
		self.addAttr = data.get("addAttr",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petalbum
class ResPetalbum(object):
	RES_TABLE = "petalbum"
	__slots__ = ("id","eleType","need","attr","lv",)

	def __init__(self):
		
		# id 宠物图鉴表
		self.id = 0
		
		# eleType 五行属性类型
		self.eleType = 0
		
		# need 需求数量
		self.need = 0
		
		# attr 属性
		self.attr = {}
		
		# lv 说明
		self.lv = 0
		

	def load_from_json(self, data):
		
		# id 宠物图鉴表
		self.id = data.get("id",0)
		
		# eleType 五行属性类型
		self.eleType = data.get("eleType",0)
		
		# need 需求数量
		self.need = data.get("need",0)
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		# lv 说明
		self.lv = data.get("lv",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petrelationship3
class ResPetrelationship3(object):
	RES_TABLE = "petrelationship3"
	__slots__ = ("id","passID","need","limit","addAttr1","addAttr2","addAttr3","addAttr4","addAttr5",)

	def __init__(self):
		
		# id 羁绊
		self.id = 0
		
		# passID 跳过上阵限制条件
		self.passID = 0
		
		# need 是否需要上阵
		self.need = 0
		
		# limit 对应条件
		self.limit = []
		
		# addAttr1 增加属性
		self.addAttr1 = {}
		
		# addAttr2 增加属性
		self.addAttr2 = {}
		
		# addAttr3 增加属性
		self.addAttr3 = {}
		
		# addAttr4 增加属性
		self.addAttr4 = {}
		
		# addAttr5 增加属性
		self.addAttr5 = {}
		

	def load_from_json(self, data):
		
		# id 羁绊
		self.id = data.get("id",0)
		
		# passID 跳过上阵限制条件
		self.passID = data.get("passID",0)
		
		# need 是否需要上阵
		self.need = data.get("need",0)
		
		# limit 对应条件
		self.limit = data.get("limit",[])
		
		# addAttr1 增加属性
		self.addAttr1 = data.get("addAttr1",{})
		
		# addAttr2 增加属性
		self.addAttr2 = data.get("addAttr2",{})
		
		# addAttr3 增加属性
		self.addAttr3 = data.get("addAttr3",{})
		
		# addAttr4 增加属性
		self.addAttr4 = data.get("addAttr4",{})
		
		# addAttr5 增加属性
		self.addAttr5 = data.get("addAttr5",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petlv
class ResPetlv(object):
	RES_TABLE = "petlv"
	__slots__ = ("id","quality","lv","cost","back","isUp",)

	def __init__(self):
		
		# id 升级消耗
		self.id = 0
		
		# quality 品质
		self.quality = 0
		
		# lv 等级
		self.lv = 0
		
		# cost 升阶消耗
		self.cost = {}
		
		# back 返还
		self.back = {}
		
		# isUp 是否突破
		self.isUp = 0
		

	def load_from_json(self, data):
		
		# id 升级消耗
		self.id = data.get("id",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# lv 等级
		self.lv = data.get("lv",0)
		
		# cost 升阶消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# back 返还
		self.arrayint2tomap("back", data.get("back",[]))
		
		# isUp 是否突破
		self.isUp = data.get("isUp",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petevolve
class ResPetevolve(object):
	RES_TABLE = "petevolve"
	__slots__ = ("id","petId","showStar","evolveLv","changeID","attr","lvAttr","lvLimit","ui","needLv","cost","costPet1","costPet2","lxSkillLv","private","peculiarityAdd","maxSlots",)

	def __init__(self):
		
		# id 进化表
		self.id = 0
		
		# petId 宠物id
		self.petId = 0
		
		# showStar 显示星级
		self.showStar = 0
		
		# evolveLv 进化阶数
		self.evolveLv = 0
		
		# changeID 变更宠物id
		self.changeID = 0
		
		# attr 进化属性
		self.attr = {}
		
		# lvAttr 星级等级属性
		self.lvAttr = {}
		
		# lvLimit 可升级上限
		self.lvLimit = 0
		
		# ui UI类型
		self.ui = 0
		
		# needLv 进化需要等级
		self.needLv = 0
		
		# cost 进化消耗
		self.cost = {}
		
		# costPet1 消耗指定宠物
		self.costPet1 = []
		
		# costPet2 消耗宠物
		self.costPet2 = []
		
		# lxSkillLv 连协技能等级
		self.lxSkillLv = 0
		
		# private 开放专属特性
		self.private = 0
		
		# peculiarityAdd 进化新增特性列表
		self.peculiarityAdd = []
		
		# maxSlots 最大特性坑位
		self.maxSlots = 0
		

	def load_from_json(self, data):
		
		# id 进化表
		self.id = data.get("id",0)
		
		# petId 宠物id
		self.petId = data.get("petId",0)
		
		# showStar 显示星级
		self.showStar = data.get("showStar",0)
		
		# evolveLv 进化阶数
		self.evolveLv = data.get("evolveLv",0)
		
		# changeID 变更宠物id
		self.changeID = data.get("changeID",0)
		
		# attr 进化属性
		self.attr = data.get("attr",{})
		
		# lvAttr 星级等级属性
		self.lvAttr = data.get("lvAttr",{})
		
		# lvLimit 可升级上限
		self.lvLimit = data.get("lvLimit",0)
		
		# ui UI类型
		self.ui = data.get("ui",0)
		
		# needLv 进化需要等级
		self.needLv = data.get("needLv",0)
		
		# cost 进化消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# costPet1 消耗指定宠物
		self.costPet1 = data.get("costPet1",[])
		
		# costPet2 消耗宠物
		self.costPet2 = data.get("costPet2",[])
		
		# lxSkillLv 连协技能等级
		self.lxSkillLv = data.get("lxSkillLv",0)
		
		# private 开放专属特性
		self.private = data.get("private",0)
		
		# peculiarityAdd 进化新增特性列表
		self.peculiarityAdd = data.get("peculiarityAdd",[])
		
		# maxSlots 最大特性坑位
		self.maxSlots = data.get("maxSlots",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# title
class ResTitle(object):
	RES_TABLE = "title"
	__slots__ = ("id","type","typeName","bg","attr","cost",)

	def __init__(self):
		
		# id 称号表
		self.id = 0
		
		# type 类型
		self.type = 0
		
		# typeName 类型名
		self.typeName = ""
		
		# bg 底图
		self.bg = ""
		
		# attr 属性
		self.attr = {}
		
		# cost 消耗道具
		self.cost = {}
		

	def load_from_json(self, data):
		
		# id 称号表
		self.id = data.get("id",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# typeName 类型名
		self.typeName = data.get("typeName","")
		
		# bg 底图
		self.bg = data.get("bg","")
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		# cost 消耗道具
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# errorTip
class ResErrorTip(object):
	RES_TABLE = "errorTip"
	__slots__ = ("id","content",)

	def __init__(self):
		
		# id 错误代码
		self.id = 0
		
		# content 错误文本
		self.content = ""
		

	def load_from_json(self, data):
		
		# id 错误代码
		self.id = data.get("id",0)
		
		# content 错误文本
		self.content = data.get("content","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# mapObject
class ResMapObject(object):
	RES_TABLE = "mapObject"
	__slots__ = ("id","rewardid","reward","rescueSystemKey","rescueAuto",)

	def __init__(self):
		
		# id 地图物件
		self.id = 0
		
		# rewardid 奖励表id
		self.rewardid = 0
		
		# reward 奖励
		self.reward = {}
		
		# rescueSystemKey 救援id_位置
		self.rescueSystemKey = {}
		
		# rescueAuto 救援任意撒(几个
		self.rescueAuto = 0
		

	def load_from_json(self, data):
		
		# id 地图物件
		self.id = data.get("id",0)
		
		# rewardid 奖励表id
		self.rewardid = data.get("rewardid",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# rescueSystemKey 救援id_位置
		self.arrayint2tomap("rescueSystemKey", data.get("rescueSystemKey",[]))
		
		# rescueAuto 救援任意撒(几个
		self.rescueAuto = data.get("rescueAuto",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# mapWorld
class ResMapWorld(object):
	RES_TABLE = "mapWorld"
	__slots__ = ("id","name","lv","pos","miniIcon",)

	def __init__(self):
		
		# id 世界地图表
		self.id = 0
		
		# name 名称
		self.name = ""
		
		# lv 等级需求
		self.lv = 0
		
		# pos 位置X_Y
		self.pos = []
		
		# miniIcon 小地图图标
		self.miniIcon = ""
		

	def load_from_json(self, data):
		
		# id 世界地图表
		self.id = data.get("id",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# lv 等级需求
		self.lv = data.get("lv",0)
		
		# pos 位置X_Y
		self.pos = data.get("pos",[])
		
		# miniIcon 小地图图标
		self.miniIcon = data.get("miniIcon","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# encounter
class ResEncounter(object):
	RES_TABLE = "encounter"
	__slots__ = ("id","name","des","tips","passId","maxRound","rewardId","helpRewardId","monster1","monster2","monster3","notice","eleType","increase","decrease",)

	def __init__(self):
		
		# id 遭遇战
		self.id = 0
		
		# name 名称
		self.name = ""
		
		# des 描述
		self.des = ""
		
		# tips 提示
		self.tips = ""
		
		# passId 开放关卡ID
		self.passId = 0
		
		# maxRound 最大回合数
		self.maxRound = 0
		
		# rewardId 奖励id
		self.rewardId = 0
		
		# helpRewardId 协助奖励
		self.helpRewardId = 0
		
		# monster1 怪物1波
		self.monster1 = []
		
		# monster2 怪物2波
		self.monster2 = []
		
		# monster3 怪物3波
		self.monster3 = []
		
		# notice 产生公告的物品(物品id_公告模板)
		self.notice = []
		
		# eleType 五行属性类型
		self.eleType = 0
		
		# increase 属性增益
		self.increase = 0
		
		# decrease 属性减益
		self.decrease = 0
		

	def load_from_json(self, data):
		
		# id 遭遇战
		self.id = data.get("id",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# des 描述
		self.des = data.get("des","")
		
		# tips 提示
		self.tips = data.get("tips","")
		
		# passId 开放关卡ID
		self.passId = data.get("passId",0)
		
		# maxRound 最大回合数
		self.maxRound = data.get("maxRound",0)
		
		# rewardId 奖励id
		self.rewardId = data.get("rewardId",0)
		
		# helpRewardId 协助奖励
		self.helpRewardId = data.get("helpRewardId",0)
		
		# monster1 怪物1波
		self.monster1 = data.get("monster1",[])
		
		# monster2 怪物2波
		self.monster2 = data.get("monster2",[])
		
		# monster3 怪物3波
		self.monster3 = data.get("monster3",[])
		
		# notice 产生公告的物品(物品id_公告模板)
		self.notice = data.get("notice",[])
		
		# eleType 五行属性类型
		self.eleType = data.get("eleType",0)
		
		# increase 属性增益
		self.increase = data.get("increase",0)
		
		# decrease 属性减益
		self.decrease = data.get("decrease",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# mapSub
class ResMapSub(object):
	RES_TABLE = "mapSub"
	__slots__ = ("id","name","mapId","chapter","section","passDesc","passReward","fightLv","mstTime","mstList","mstId","bossBarrId","offexp","offcoin","offexplore","offpetexp","offreward","objReuse","objOnce","objPercent",)

	def __init__(self):
		
		# id 关卡表
		self.id = 0
		
		# name 对应地图名称
		self.name = ""
		
		# mapId 世界地图id
		self.mapId = 0
		
		# chapter 章
		self.chapter = 0
		
		# section 节
		self.section = 0
		
		# passDesc 通关奖励说明
		self.passDesc = ""
		
		# passReward 通关奖励
		self.passReward = {}
		
		# fightLv 挑战等级
		self.fightLv = 0
		
		# mstTime 小怪间隔出现时间
		self.mstTime = 0
		
		# mstList 小怪列表
		self.mstList = []
		
		# mstId boss怪物id
		self.mstId = 0
		
		# bossBarrId boss副本id
		self.bossBarrId = 0
		
		# offexp 挂机经验
		self.offexp = 0
		
		# offcoin 挂机金币
		self.offcoin = 0
		
		# offexplore 挂机探索点
		self.offexplore = 0
		
		# offpetexp 挂机宠物经验
		self.offpetexp = 0
		
		# offreward 挂机奖励表
		self.offreward = []
		
		# objReuse 撒地图重复
		self.objReuse = []
		
		# objOnce 撒地图关键
		self.objOnce = []
		
		# objPercent 撒地图关键万分率
		self.objPercent = 0
		

	def load_from_json(self, data):
		
		# id 关卡表
		self.id = data.get("id",0)
		
		# name 对应地图名称
		self.name = data.get("name","")
		
		# mapId 世界地图id
		self.mapId = data.get("mapId",0)
		
		# chapter 章
		self.chapter = data.get("chapter",0)
		
		# section 节
		self.section = data.get("section",0)
		
		# passDesc 通关奖励说明
		self.passDesc = data.get("passDesc","")
		
		# passReward 通关奖励
		self.arrayint2tomap("passReward", data.get("passReward",[]))
		
		# fightLv 挑战等级
		self.fightLv = data.get("fightLv",0)
		
		# mstTime 小怪间隔出现时间
		self.mstTime = data.get("mstTime",0)
		
		# mstList 小怪列表
		self.mstList = data.get("mstList",[])
		
		# mstId boss怪物id
		self.mstId = data.get("mstId",0)
		
		# bossBarrId boss副本id
		self.bossBarrId = data.get("bossBarrId",0)
		
		# offexp 挂机经验
		self.offexp = data.get("offexp",0)
		
		# offcoin 挂机金币
		self.offcoin = data.get("offcoin",0)
		
		# offexplore 挂机探索点
		self.offexplore = data.get("offexplore",0)
		
		# offpetexp 挂机宠物经验
		self.offpetexp = data.get("offpetexp",0)
		
		# offreward 挂机奖励表
		self.offreward = data.get("offreward",[])
		
		# objReuse 撒地图重复
		self.objReuse = data.get("objReuse",[])
		
		# objOnce 撒地图关键
		self.objOnce = data.get("objOnce",[])
		
		# objPercent 撒地图关键万分率
		self.objPercent = data.get("objPercent",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# examAnswerPoint
class ResExamAnswerPoint(object):
	RES_TABLE = "examAnswerPoint"
	__slots__ = ("id","correct","interval","point",)

	def __init__(self):
		
		# id 得分表
		self.id = 0
		
		# correct 正确
		self.correct = 0
		
		# interval 用时
		self.interval = 0
		
		# point 分数
		self.point = 0
		

	def load_from_json(self, data):
		
		# id 得分表
		self.id = data.get("id",0)
		
		# correct 正确
		self.correct = data.get("correct",0)
		
		# interval 用时
		self.interval = data.get("interval",0)
		
		# point 分数
		self.point = data.get("point",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# examQuestionPool
class ResExamQuestionPool(object):
	RES_TABLE = "examQuestionPool"
	__slots__ = ("id","correct",)

	def __init__(self):
		
		# id 题库表
		self.id = 0
		
		# correct 正确答案
		self.correct = 0
		

	def load_from_json(self, data):
		
		# id 题库表
		self.id = data.get("id",0)
		
		# correct 正确答案
		self.correct = data.get("correct",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# examRankReward
class ResExamRankReward(object):
	RES_TABLE = "examRankReward"
	__slots__ = ("id","rank","reward",)

	def __init__(self):
		
		# id 答题奖励表
		self.id = 0
		
		# rank 排名
		self.rank = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 答题奖励表
		self.id = data.get("id",0)
		
		# rank 排名
		self.rank = data.get("rank",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# item
class ResItem(object):
	RES_TABLE = "item"
	__slots__ = ("id","name","quality","sortValue","type","subType","page","use","useTip","useAuto","upleft","upright","iconId","compound","rewardId","donate","selectReward","checkPet","showCompoundNum","arg1","arg2","timeType","timeArg","leftTopStr","leftBotStr","costTips","chatId",)

	def __init__(self):
		
		# id 道具表
		self.id = 0
		
		# name 
		self.name = ""
		
		# quality 品质
		self.quality = 0
		
		# sortValue 排序
		self.sortValue = 0
		
		# type 类型
		self.type = 0
		
		# subType 子类型
		self.subType = 0
		
		# page 分页
		self.page = 0
		
		# use 能否使用
		self.use = 0
		
		# useTip 使用是否弹使用成功
		self.useTip = 0
		
		# useAuto 是否自动使用
		self.useAuto = 0
		
		# upleft 左上压标
		self.upleft = ""
		
		# upright 右上压标
		self.upright = ""
		
		# iconId 显示压标图片
		self.iconId = 0
		
		# compound 物品合成
		self.compound = []
		
		# rewardId 奖励id
		self.rewardId = 0
		
		# donate 能否帮会捐献
		self.donate = 0
		
		# selectReward 可选奖励
		self.selectReward = []
		
		# checkPet N选一判断宠物
		self.checkPet = 0
		
		# showCompoundNum 物品合成是否显示10/4
		self.showCompoundNum = 0
		
		# arg1 通用参数1
		self.arg1 = ""
		
		# arg2 通用参数2
		self.arg2 = ""
		
		# timeType 限时类型
		self.timeType = 0
		
		# timeArg 限时参数
		self.timeArg = ""
		
		# leftTopStr 道具图标左上角文字压标
		self.leftTopStr = ""
		
		# leftBotStr 道具图标左下角文字压标
		self.leftBotStr = ""
		
		# costTips 消耗材料不足提示文字
		self.costTips = ""
		
		# chatId 广播ID
		self.chatId = 0
		

	def load_from_json(self, data):
		
		# id 道具表
		self.id = data.get("id",0)
		
		# name 
		self.name = data.get("name","")
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# sortValue 排序
		self.sortValue = data.get("sortValue",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# subType 子类型
		self.subType = data.get("subType",0)
		
		# page 分页
		self.page = data.get("page",0)
		
		# use 能否使用
		self.use = data.get("use",0)
		
		# useTip 使用是否弹使用成功
		self.useTip = data.get("useTip",0)
		
		# useAuto 是否自动使用
		self.useAuto = data.get("useAuto",0)
		
		# upleft 左上压标
		self.upleft = data.get("upleft","")
		
		# upright 右上压标
		self.upright = data.get("upright","")
		
		# iconId 显示压标图片
		self.iconId = data.get("iconId",0)
		
		# compound 物品合成
		self.compound = data.get("compound",[])
		
		# rewardId 奖励id
		self.rewardId = data.get("rewardId",0)
		
		# donate 能否帮会捐献
		self.donate = data.get("donate",0)
		
		# selectReward 可选奖励
		self.selectReward = data.get("selectReward",[])
		
		# checkPet N选一判断宠物
		self.checkPet = data.get("checkPet",0)
		
		# showCompoundNum 物品合成是否显示10/4
		self.showCompoundNum = data.get("showCompoundNum",0)
		
		# arg1 通用参数1
		self.arg1 = data.get("arg1","")
		
		# arg2 通用参数2
		self.arg2 = data.get("arg2","")
		
		# timeType 限时类型
		self.timeType = data.get("timeType",0)
		
		# timeArg 限时参数
		self.timeArg = data.get("timeArg","")
		
		# leftTopStr 道具图标左上角文字压标
		self.leftTopStr = data.get("leftTopStr","")
		
		# leftBotStr 道具图标左下角文字压标
		self.leftBotStr = data.get("leftBotStr","")
		
		# costTips 消耗材料不足提示文字
		self.costTips = data.get("costTips","")
		
		# chatId 广播ID
		self.chatId = data.get("chatId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# jiujiyishou
class ResJiujiyishou(object):
	RES_TABLE = "jiujiyishou"
	__slots__ = ("id","name","unlock","firstRewardShow","addAttr","challengeList0","challengeList1","challengeList2","challengeList3","challengeList4","challengeList5","challengeList6","iconImg","lockTitle","beforeDesc","bossFaceId","unlockName","afterDesc","titleName","sceneId","sceneList","mapDesc1","mapDesc2","mapDesc3","leaderId","skillIds",)

	def __init__(self):
		
		# id 究极异兽表
		self.id = 0
		
		# name 道馆名称
		self.name = ""
		
		# unlock 解锁道馆id
		self.unlock = 0
		
		# firstRewardShow 客户端奖励展示(脖子说客户端这里是固定的)
		self.firstRewardShow = []
		
		# addAttr 增加属性
		self.addAttr = []
		
		# challengeList0 挑战副本列表星期天
		self.challengeList0 = []
		
		# challengeList1 挑战副本列表星期一
		self.challengeList1 = []
		
		# challengeList2 挑战副本列表星期二
		self.challengeList2 = []
		
		# challengeList3 挑战副本列表星期三
		self.challengeList3 = []
		
		# challengeList4 挑战副本列表星期四
		self.challengeList4 = []
		
		# challengeList5 挑战副本列表星期五
		self.challengeList5 = []
		
		# challengeList6 挑战副本列表星期六
		self.challengeList6 = []
		
		# iconImg 道馆图片
		self.iconImg = ""
		
		# lockTitle 解锁前台头
		self.lockTitle = ""
		
		# beforeDesc 解锁前说明
		self.beforeDesc = ""
		
		# bossFaceId 解锁形象怪物表
		self.bossFaceId = 0
		
		# unlockName 解锁人物名字
		self.unlockName = ""
		
		# afterDesc 解锁后说明
		self.afterDesc = ""
		
		# titleName 解锁道馆名字
		self.titleName = ""
		
		# sceneId 地图场景id
		self.sceneId = 0
		
		# sceneList 坐标
		self.sceneList = []
		
		# mapDesc1 地图小黑版
		self.mapDesc1 = ""
		
		# mapDesc2 地图小黑版
		self.mapDesc2 = ""
		
		# mapDesc3 地图小黑版
		self.mapDesc3 = ""
		
		# leaderId 馆主副本id
		self.leaderId = 0
		
		# skillIds 道馆boss技能ID
		self.skillIds = []
		

	def load_from_json(self, data):
		
		# id 究极异兽表
		self.id = data.get("id",0)
		
		# name 道馆名称
		self.name = data.get("name","")
		
		# unlock 解锁道馆id
		self.unlock = data.get("unlock",0)
		
		# firstRewardShow 客户端奖励展示(脖子说客户端这里是固定的)
		self.firstRewardShow = data.get("firstRewardShow",[])
		
		# addAttr 增加属性
		self.addAttr = data.get("addAttr",[])
		
		# challengeList0 挑战副本列表星期天
		self.challengeList0 = data.get("challengeList0",[])
		
		# challengeList1 挑战副本列表星期一
		self.challengeList1 = data.get("challengeList1",[])
		
		# challengeList2 挑战副本列表星期二
		self.challengeList2 = data.get("challengeList2",[])
		
		# challengeList3 挑战副本列表星期三
		self.challengeList3 = data.get("challengeList3",[])
		
		# challengeList4 挑战副本列表星期四
		self.challengeList4 = data.get("challengeList4",[])
		
		# challengeList5 挑战副本列表星期五
		self.challengeList5 = data.get("challengeList5",[])
		
		# challengeList6 挑战副本列表星期六
		self.challengeList6 = data.get("challengeList6",[])
		
		# iconImg 道馆图片
		self.iconImg = data.get("iconImg","")
		
		# lockTitle 解锁前台头
		self.lockTitle = data.get("lockTitle","")
		
		# beforeDesc 解锁前说明
		self.beforeDesc = data.get("beforeDesc","")
		
		# bossFaceId 解锁形象怪物表
		self.bossFaceId = data.get("bossFaceId",0)
		
		# unlockName 解锁人物名字
		self.unlockName = data.get("unlockName","")
		
		# afterDesc 解锁后说明
		self.afterDesc = data.get("afterDesc","")
		
		# titleName 解锁道馆名字
		self.titleName = data.get("titleName","")
		
		# sceneId 地图场景id
		self.sceneId = data.get("sceneId",0)
		
		# sceneList 坐标
		self.sceneList = data.get("sceneList",[])
		
		# mapDesc1 地图小黑版
		self.mapDesc1 = data.get("mapDesc1","")
		
		# mapDesc2 地图小黑版
		self.mapDesc2 = data.get("mapDesc2","")
		
		# mapDesc3 地图小黑版
		self.mapDesc3 = data.get("mapDesc3","")
		
		# leaderId 馆主副本id
		self.leaderId = data.get("leaderId",0)
		
		# skillIds 道馆boss技能ID
		self.skillIds = data.get("skillIds",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# pavilion
class ResPavilion(object):
	RES_TABLE = "pavilion"
	__slots__ = ("id","name","area","areaName","eleType","increase","decrease","unlockTask","attr","firstRewardId","firstRewardShow","rewardId","rewardShow","challengeList","iconImg","lockTitle","beforeDesc","bossFaceId","unlockName","afterDesc","titleName","eleTips","sceneId","sceneList","mapDesc1","mapDesc2","mapDesc3","leavewordWin","leavewordLose","leaderId","emebleId","emeblesort","actYskj","YsManifesto",)

	def __init__(self):
		
		# id 道馆表
		self.id = 0
		
		# name 道馆名称
		self.name = ""
		
		# area 所属地区
		self.area = 0
		
		# areaName 所属地区名称
		self.areaName = ""
		
		# eleType 元素类型
		self.eleType = 0
		
		# increase 属性增益
		self.increase = 0
		
		# decrease 属性减益
		self.decrease = 0
		
		# unlockTask 解锁任务列表
		self.unlockTask = []
		
		# attr 首通属性奖励
		self.attr = []
		
		# firstRewardId 首通奖励id
		self.firstRewardId = 0
		
		# firstRewardShow 首通客户端奖励展示
		self.firstRewardShow = []
		
		# rewardId 扫荡奖励id
		self.rewardId = 0
		
		# rewardShow 扫荡奖励展示
		self.rewardShow = []
		
		# challengeList 挑战副本列表
		self.challengeList = []
		
		# iconImg 道馆图片
		self.iconImg = ""
		
		# lockTitle 解锁前台头
		self.lockTitle = ""
		
		# beforeDesc 解锁前说明
		self.beforeDesc = ""
		
		# bossFaceId 解锁形象怪物表
		self.bossFaceId = 0
		
		# unlockName 解锁人物名字
		self.unlockName = ""
		
		# afterDesc 解锁后说明
		self.afterDesc = ""
		
		# titleName 解锁道馆名字
		self.titleName = ""
		
		# eleTips 属性提示
		self.eleTips = ""
		
		# sceneId 地图场景id
		self.sceneId = 0
		
		# sceneList 坐标
		self.sceneList = []
		
		# mapDesc1 地图小黑版
		self.mapDesc1 = ""
		
		# mapDesc2 地图小黑版
		self.mapDesc2 = ""
		
		# mapDesc3 地图小黑版
		self.mapDesc3 = ""
		
		# leavewordWin 遗言win
		self.leavewordWin = ""
		
		# leavewordLose 遗言lose
		self.leavewordLose = ""
		
		# leaderId 馆主副本id
		self.leaderId = 0
		
		# emebleId 勋章id
		self.emebleId = 0
		
		# emeblesort 勋章排行
		self.emeblesort = 0
		
		# actYskj 激活异兽空间第几层(0或者不填未不激活
		self.actYskj = 0
		
		# YsManifesto 开启异兽空间的垃圾话
		self.YsManifesto = ""
		

	def load_from_json(self, data):
		
		# id 道馆表
		self.id = data.get("id",0)
		
		# name 道馆名称
		self.name = data.get("name","")
		
		# area 所属地区
		self.area = data.get("area",0)
		
		# areaName 所属地区名称
		self.areaName = data.get("areaName","")
		
		# eleType 元素类型
		self.eleType = data.get("eleType",0)
		
		# increase 属性增益
		self.increase = data.get("increase",0)
		
		# decrease 属性减益
		self.decrease = data.get("decrease",0)
		
		# unlockTask 解锁任务列表
		self.unlockTask = data.get("unlockTask",[])
		
		# attr 首通属性奖励
		self.attr = data.get("attr",[])
		
		# firstRewardId 首通奖励id
		self.firstRewardId = data.get("firstRewardId",0)
		
		# firstRewardShow 首通客户端奖励展示
		self.firstRewardShow = data.get("firstRewardShow",[])
		
		# rewardId 扫荡奖励id
		self.rewardId = data.get("rewardId",0)
		
		# rewardShow 扫荡奖励展示
		self.rewardShow = data.get("rewardShow",[])
		
		# challengeList 挑战副本列表
		self.challengeList = data.get("challengeList",[])
		
		# iconImg 道馆图片
		self.iconImg = data.get("iconImg","")
		
		# lockTitle 解锁前台头
		self.lockTitle = data.get("lockTitle","")
		
		# beforeDesc 解锁前说明
		self.beforeDesc = data.get("beforeDesc","")
		
		# bossFaceId 解锁形象怪物表
		self.bossFaceId = data.get("bossFaceId",0)
		
		# unlockName 解锁人物名字
		self.unlockName = data.get("unlockName","")
		
		# afterDesc 解锁后说明
		self.afterDesc = data.get("afterDesc","")
		
		# titleName 解锁道馆名字
		self.titleName = data.get("titleName","")
		
		# eleTips 属性提示
		self.eleTips = data.get("eleTips","")
		
		# sceneId 地图场景id
		self.sceneId = data.get("sceneId",0)
		
		# sceneList 坐标
		self.sceneList = data.get("sceneList",[])
		
		# mapDesc1 地图小黑版
		self.mapDesc1 = data.get("mapDesc1","")
		
		# mapDesc2 地图小黑版
		self.mapDesc2 = data.get("mapDesc2","")
		
		# mapDesc3 地图小黑版
		self.mapDesc3 = data.get("mapDesc3","")
		
		# leavewordWin 遗言win
		self.leavewordWin = data.get("leavewordWin","")
		
		# leavewordLose 遗言lose
		self.leavewordLose = data.get("leavewordLose","")
		
		# leaderId 馆主副本id
		self.leaderId = data.get("leaderId",0)
		
		# emebleId 勋章id
		self.emebleId = data.get("emebleId",0)
		
		# emeblesort 勋章排行
		self.emeblesort = data.get("emeblesort",0)
		
		# actYskj 激活异兽空间第几层(0或者不填未不激活
		self.actYskj = data.get("actYskj",0)
		
		# YsManifesto 开启异兽空间的垃圾话
		self.YsManifesto = data.get("YsManifesto","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# jiujiyishouReward
class ResJiujiyishouReward(object):
	RES_TABLE = "jiujiyishouReward"
	__slots__ = ("id","rewardShow",)

	def __init__(self):
		
		# id 究极异兽奖励星期N
		self.id = 0
		
		# rewardShow 客户端(进口奖励)
		self.rewardShow = []
		

	def load_from_json(self, data):
		
		# id 究极异兽奖励星期N
		self.id = data.get("id",0)
		
		# rewardShow 客户端(进口奖励)
		self.rewardShow = data.get("rewardShow",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# diaoyureward
class ResDiaoyureward(object):
	RES_TABLE = "diaoyureward"
	__slots__ = ("quality","reward","reward2","score","weight","broadcast",)

	def __init__(self):
		
		# quality 钓鱼奖励表
		self.quality = 0
		
		# reward 奖励
		self.reward = {}
		
		# reward2 N天后奖励
		self.reward2 = {}
		
		# score 积分
		self.score = 0
		
		# weight 权重
		self.weight = 0
		
		# broadcast 广播id
		self.broadcast = 0
		

	def load_from_json(self, data):
		
		# quality 钓鱼奖励表
		self.quality = data.get("quality",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# reward2 N天后奖励
		self.arrayint2tomap("reward2", data.get("reward2",[]))
		
		# score 积分
		self.score = data.get("score",0)
		
		# weight 权重
		self.weight = data.get("weight",0)
		
		# broadcast 广播id
		self.broadcast = data.get("broadcast",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# diaoyurank
class ResDiaoyurank(object):
	RES_TABLE = "diaoyurank"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id 钓鱼奖排行励表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 钓鱼奖排行励表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# barrier
class ResBarrier(object):
	RES_TABLE = "barrier"
	__slots__ = ("id","lv","vip","num","maxRound","firstReward","rewardId","rewardIdLuck","helpRewardId","monster1","monster2","monster3","notice",)

	def __init__(self):
		
		# id 副本表
		self.id = 0
		
		# lv 进入等级
		self.lv = 0
		
		# vip vip等级限制
		self.vip = 0
		
		# num 每日进入次数
		self.num = 0
		
		# maxRound 最大回合数
		self.maxRound = 0
		
		# firstReward 首通奖励
		self.firstReward = {}
		
		# rewardId 奖励id
		self.rewardId = 0
		
		# rewardIdLuck 奖励id幸运状态
		self.rewardIdLuck = 0
		
		# helpRewardId 协助奖励
		self.helpRewardId = 0
		
		# monster1 怪物1波
		self.monster1 = 0
		
		# monster2 怪物2波
		self.monster2 = 0
		
		# monster3 怪物3波
		self.monster3 = 0
		
		# notice 产生公告的物品(物品id_公告模板)
		self.notice = []
		

	def load_from_json(self, data):
		
		# id 副本表
		self.id = data.get("id",0)
		
		# lv 进入等级
		self.lv = data.get("lv",0)
		
		# vip vip等级限制
		self.vip = data.get("vip",0)
		
		# num 每日进入次数
		self.num = data.get("num",0)
		
		# maxRound 最大回合数
		self.maxRound = data.get("maxRound",0)
		
		# firstReward 首通奖励
		self.arrayint2tomap("firstReward", data.get("firstReward",[]))
		
		# rewardId 奖励id
		self.rewardId = data.get("rewardId",0)
		
		# rewardIdLuck 奖励id幸运状态
		self.rewardIdLuck = data.get("rewardIdLuck",0)
		
		# helpRewardId 协助奖励
		self.helpRewardId = data.get("helpRewardId",0)
		
		# monster1 怪物1波
		self.monster1 = data.get("monster1",0)
		
		# monster2 怪物2波
		self.monster2 = data.get("monster2",0)
		
		# monster3 怪物3波
		self.monster3 = data.get("monster3",0)
		
		# notice 产生公告的物品(物品id_公告模板)
		self.notice = data.get("notice",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# barrierwaves
class ResBarrierwaves(object):
	RES_TABLE = "barrierwaves"
	__slots__ = ("id","pos1","pos2","pos3","pos4","pos5","pos6","pos7","pos8","pos9",)

	def __init__(self):
		
		# id 怪物布阵表
		self.id = 0
		
		# pos1 位置1
		self.pos1 = 0
		
		# pos2 位置2
		self.pos2 = 0
		
		# pos3 位置3
		self.pos3 = 0
		
		# pos4 位置4
		self.pos4 = 0
		
		# pos5 位置5
		self.pos5 = 0
		
		# pos6 位置6
		self.pos6 = 0
		
		# pos7 位置7
		self.pos7 = 0
		
		# pos8 位置8
		self.pos8 = 0
		
		# pos9 位置9
		self.pos9 = 0
		

	def load_from_json(self, data):
		
		# id 怪物布阵表
		self.id = data.get("id",0)
		
		# pos1 位置1
		self.pos1 = data.get("pos1",0)
		
		# pos2 位置2
		self.pos2 = data.get("pos2",0)
		
		# pos3 位置3
		self.pos3 = data.get("pos3",0)
		
		# pos4 位置4
		self.pos4 = data.get("pos4",0)
		
		# pos5 位置5
		self.pos5 = data.get("pos5",0)
		
		# pos6 位置6
		self.pos6 = data.get("pos6",0)
		
		# pos7 位置7
		self.pos7 = data.get("pos7",0)
		
		# pos8 位置8
		self.pos8 = data.get("pos8",0)
		
		# pos9 位置9
		self.pos9 = data.get("pos9",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# pvploot
class ResPvploot(object):
	RES_TABLE = "pvploot"
	__slots__ = ("id","name","reward","pos",)

	def __init__(self):
		
		# id 抢夺连胜表
		self.id = 0
		
		# name 名称
		self.name = ""
		
		# reward 奖励道具
		self.reward = {}
		
		# pos 获取奖励位置
		self.pos = 0
		

	def load_from_json(self, data):
		
		# id 抢夺连胜表
		self.id = data.get("id",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# reward 奖励道具
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# pos 获取奖励位置
		self.pos = data.get("pos",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# pvprank
class ResPvprank(object):
	RES_TABLE = "pvprank"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id pvp奖排行励表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id pvp奖排行励表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# pvpmatch
class ResPvpmatch(object):
	RES_TABLE = "pvpmatch"
	__slots__ = ("id","startVal","endVal","downVal","downNum","upVal","upNum","valLimit",)

	def __init__(self):
		
		# id pvp匹配表
		self.id = 0
		
		# startVal 战力段起始值
		self.startVal = 0
		
		# endVal 战力段起始值
		self.endVal = 0
		
		# downVal 下限浮动(万分比)
		self.downVal = 0
		
		# downNum 下限人数
		self.downNum = 0
		
		# upVal 上限浮动(万分比)
		self.upVal = 0
		
		# upNum 上限人数
		self.upNum = 0
		
		# valLimit 浮动最大限制(万分比)
		self.valLimit = 0
		

	def load_from_json(self, data):
		
		# id pvp匹配表
		self.id = data.get("id",0)
		
		# startVal 战力段起始值
		self.startVal = data.get("startVal",0)
		
		# endVal 战力段起始值
		self.endVal = data.get("endVal",0)
		
		# downVal 下限浮动(万分比)
		self.downVal = data.get("downVal",0)
		
		# downNum 下限人数
		self.downNum = data.get("downNum",0)
		
		# upVal 上限浮动(万分比)
		self.upVal = data.get("upVal",0)
		
		# upNum 上限人数
		self.upNum = data.get("upNum",0)
		
		# valLimit 浮动最大限制(万分比)
		self.valLimit = data.get("valLimit",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# open
class ResOpen(object):
	RES_TABLE = "open"
	__slots__ = ("id","fa","scale","offX","offY","level","guideId","type","vip","svip","openServiceDay","guildLv","mapLv","taskID","actId","openTaskId","name","tyIcon","tyBg","tyDesc","panel","PanelShow","tabIndex","showStyle","reward","needTipPanel","tipTitle","tipDesc","tipImg","tipIconImg","tipBtn",)

	def __init__(self):
		
		# id 功能开启表
		self.id = 0
		
		# fa 功能预告战力(不用了)
		self.fa = 0
		
		# scale 功能预告形象缩放
		self.scale = 0
		
		# offX 功能预告形象x
		self.offX = 0
		
		# offY 功能预告形象y
		self.offY = 0
		
		# level 开放等级
		self.level = 0
		
		# guideId 功能开启触发引导id
		self.guideId = 0
		
		# type 条件类型
		self.type = 0
		
		# vip vip开启
		self.vip = 0
		
		# svip 至尊卡要求
		self.svip = 0
		
		# openServiceDay 开服天数
		self.openServiceDay = 0
		
		# guildLv 帮会等级
		self.guildLv = 0
		
		# mapLv 关卡
		self.mapLv = 0
		
		# taskID 要过了任务的ID
		self.taskID = 0
		
		# actId 活动id
		self.actId = 0
		
		# openTaskId 开放功能体验任务id
		self.openTaskId = 0
		
		# name 名字
		self.name = ""
		
		# tyIcon 图标
		self.tyIcon = ""
		
		# tyBg 系统体验背景
		self.tyBg = ""
		
		# tyDesc 描述
		self.tyDesc = ""
		
		# panel 面板ID
		self.panel = ""
		
		# PanelShow PanelShow函数名
		self.PanelShow = ""
		
		# tabIndex tab索引
		self.tabIndex = 0
		
		# showStyle 主界面显示样式
		self.showStyle = 0
		
		# reward 奖励
		self.reward = []
		
		# needTipPanel 是否需要弹出开启界面
		self.needTipPanel = 0
		
		# tipTitle 开启界面标题
		self.tipTitle = ""
		
		# tipDesc 开启界面描述
		self.tipDesc = ""
		
		# tipImg 开启界面图片
		self.tipImg = ""
		
		# tipIconImg 飞的图标
		self.tipIconImg = ""
		
		# tipBtn 开启界面飞到的按钮
		self.tipBtn = ""
		

	def load_from_json(self, data):
		
		# id 功能开启表
		self.id = data.get("id",0)
		
		# fa 功能预告战力(不用了)
		self.fa = data.get("fa",0)
		
		# scale 功能预告形象缩放
		self.scale = data.get("scale",0)
		
		# offX 功能预告形象x
		self.offX = data.get("offX",0)
		
		# offY 功能预告形象y
		self.offY = data.get("offY",0)
		
		# level 开放等级
		self.level = data.get("level",0)
		
		# guideId 功能开启触发引导id
		self.guideId = data.get("guideId",0)
		
		# type 条件类型
		self.type = data.get("type",0)
		
		# vip vip开启
		self.vip = data.get("vip",0)
		
		# svip 至尊卡要求
		self.svip = data.get("svip",0)
		
		# openServiceDay 开服天数
		self.openServiceDay = data.get("openServiceDay",0)
		
		# guildLv 帮会等级
		self.guildLv = data.get("guildLv",0)
		
		# mapLv 关卡
		self.mapLv = data.get("mapLv",0)
		
		# taskID 要过了任务的ID
		self.taskID = data.get("taskID",0)
		
		# actId 活动id
		self.actId = data.get("actId",0)
		
		# openTaskId 开放功能体验任务id
		self.openTaskId = data.get("openTaskId",0)
		
		# name 名字
		self.name = data.get("name","")
		
		# tyIcon 图标
		self.tyIcon = data.get("tyIcon","")
		
		# tyBg 系统体验背景
		self.tyBg = data.get("tyBg","")
		
		# tyDesc 描述
		self.tyDesc = data.get("tyDesc","")
		
		# panel 面板ID
		self.panel = data.get("panel","")
		
		# PanelShow PanelShow函数名
		self.PanelShow = data.get("PanelShow","")
		
		# tabIndex tab索引
		self.tabIndex = data.get("tabIndex",0)
		
		# showStyle 主界面显示样式
		self.showStyle = data.get("showStyle",0)
		
		# reward 奖励
		self.reward = data.get("reward",[])
		
		# needTipPanel 是否需要弹出开启界面
		self.needTipPanel = data.get("needTipPanel",0)
		
		# tipTitle 开启界面标题
		self.tipTitle = data.get("tipTitle","")
		
		# tipDesc 开启界面描述
		self.tipDesc = data.get("tipDesc","")
		
		# tipImg 开启界面图片
		self.tipImg = data.get("tipImg","")
		
		# tipIconImg 飞的图标
		self.tipIconImg = data.get("tipIconImg","")
		
		# tipBtn 开启界面飞到的按钮
		self.tipBtn = data.get("tipBtn","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# openTask
class ResOpenTask(object):
	RES_TABLE = "openTask"
	__slots__ = ("id","taskList","reward","openReward",)

	def __init__(self):
		
		# id 功能开启任务表
		self.id = 0
		
		# taskList 体验任务列表
		self.taskList = []
		
		# reward 奖励
		self.reward = []
		
		# openReward 功能开启手动奖励
		self.openReward = []
		

	def load_from_json(self, data):
		
		# id 功能开启任务表
		self.id = data.get("id",0)
		
		# taskList 体验任务列表
		self.taskList = data.get("taskList",[])
		
		# reward 奖励
		self.reward = data.get("reward",[])
		
		# openReward 功能开启手动奖励
		self.openReward = data.get("openReward",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# monster
class ResMonster(object):
	RES_TABLE = "monster"
	__slots__ = ("id","name","type","quality","petID","level","evolveLv","normal","skills","peculiarity","dialog","dialogTime","scale","hp","atk","defe","speed","hit","miss","grassAddition","waterAddition","fireAddition","lightAddition","darkAddition","attr",)

	def __init__(self):
		
		# id 怪物表
		self.id = 0
		
		# name 名称
		self.name = ""
		
		# type 类型
		self.type = 0
		
		# quality 品质
		self.quality = 0
		
		# petID 宠物id
		self.petID = 0
		
		# level 等级
		self.level = 0
		
		# evolveLv 进化等级
		self.evolveLv = 0
		
		# normal 普攻技能
		self.normal = 0
		
		# skills 主动技能
		self.skills = []
		
		# peculiarity 被动技能
		self.peculiarity = []
		
		# dialog 战斗独白
		self.dialog = ""
		
		# dialogTime 战斗独白时间秒
		self.dialogTime = 0
		
		# scale 缩放
		self.scale = 0
		
		# hp 生命
		self.hp = 0
		
		# atk 攻击
		self.atk = 0
		
		# defe 防御
		self.defe = 0
		
		# speed 速度
		self.speed = 0
		
		# hit 命中
		self.hit = 0
		
		# miss 闪避
		self.miss = 0
		
		# grassAddition 草系增伤
		self.grassAddition = 0
		
		# waterAddition 水系增伤
		self.waterAddition = 0
		
		# fireAddition 火系增伤
		self.fireAddition = 0
		
		# lightAddition 光系增伤
		self.lightAddition = 0
		
		# darkAddition 暗系增伤
		self.darkAddition = 0
		
		# attr 通用属性
		self.attr = {}
		

	def load_from_json(self, data):
		
		# id 怪物表
		self.id = data.get("id",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# type 类型
		self.type = data.get("type",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# petID 宠物id
		self.petID = data.get("petID",0)
		
		# level 等级
		self.level = data.get("level",0)
		
		# evolveLv 进化等级
		self.evolveLv = data.get("evolveLv",0)
		
		# normal 普攻技能
		self.normal = data.get("normal",0)
		
		# skills 主动技能
		self.skills = data.get("skills",[])
		
		# peculiarity 被动技能
		self.peculiarity = data.get("peculiarity",[])
		
		# dialog 战斗独白
		self.dialog = data.get("dialog","")
		
		# dialogTime 战斗独白时间秒
		self.dialogTime = data.get("dialogTime",0)
		
		# scale 缩放
		self.scale = data.get("scale",0)
		
		# hp 生命
		self.hp = data.get("hp",0)
		
		# atk 攻击
		self.atk = data.get("atk",0)
		
		# defe 防御
		self.defe = data.get("defe",0)
		
		# speed 速度
		self.speed = data.get("speed",0)
		
		# hit 命中
		self.hit = data.get("hit",0)
		
		# miss 闪避
		self.miss = data.get("miss",0)
		
		# grassAddition 草系增伤
		self.grassAddition = data.get("grassAddition",0)
		
		# waterAddition 水系增伤
		self.waterAddition = data.get("waterAddition",0)
		
		# fireAddition 火系增伤
		self.fireAddition = data.get("fireAddition",0)
		
		# lightAddition 光系增伤
		self.lightAddition = data.get("lightAddition",0)
		
		# darkAddition 暗系增伤
		self.darkAddition = data.get("darkAddition",0)
		
		# attr 通用属性
		self.attr = data.get("attr",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengPersonrRank
class ResGongchengPersonrRank(object):
	RES_TABLE = "gongchengPersonrRank"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id 跨服boss排行
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 跨服boss排行
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongcheng
class ResGongcheng(object):
	RES_TABLE = "gongcheng"
	__slots__ = ("id","near","ATK_SUCC","DEF_FAIL","ATK_FAIL","DEF_SUCC","holdReward","defLevel","x","y","level","helpId","name","fbIds","npcAndms","occupyCD","atkCD","OpenLv","guildCitySocre","isDeclarewar","BuildImg","lines","showReward","info","gbinfo",)

	def __init__(self):
		
		# id 攻城城市id
		self.id = 0
		
		# near 相邻数组
		self.near = []
		
		# ATK_SUCC 杀1人奖励攻城成功
		self.ATK_SUCC = []
		
		# DEF_FAIL 杀1人奖励防守失败
		self.DEF_FAIL = []
		
		# ATK_FAIL 杀1人奖励攻城失败
		self.ATK_FAIL = []
		
		# DEF_SUCC 杀1人奖励防守成功
		self.DEF_SUCC = []
		
		# holdReward 22点占城奖励
		self.holdReward = []
		
		# defLevel 防御等级
		self.defLevel = 0
		
		# x 中心位置X
		self.x = 0
		
		# y 中心位置Y
		self.y = 0
		
		# level 城市界别
		self.level = 0
		
		# helpId 帮助说明id
		self.helpId = 0
		
		# name 名字
		self.name = ""
		
		# fbIds NPC副本id
		self.fbIds = []
		
		# npcAndms Npc形象
		self.npcAndms = []
		
		# occupyCD 占领保护时间cd(秒)
		self.occupyCD = 0
		
		# atkCD 公鸡保护时间cd(秒)
		self.atkCD = 0
		
		# OpenLv 开放等级(公会等级)
		self.OpenLv = 0
		
		# guildCitySocre 公会占城积分
		self.guildCitySocre = 0
		
		# isDeclarewar 是否要宣战
		self.isDeclarewar = 0
		
		# BuildImg 城市图片
		self.BuildImg = ""
		
		# lines 绿线
		self.lines = []
		
		# showReward 特产奖励
		self.showReward = {}
		
		# info 城市介绍
		self.info = ""
		
		# gbinfo 占城广播
		self.gbinfo = ""
		

	def load_from_json(self, data):
		
		# id 攻城城市id
		self.id = data.get("id",0)
		
		# near 相邻数组
		self.near = data.get("near",[])
		
		# ATK_SUCC 杀1人奖励攻城成功
		self.ATK_SUCC = data.get("ATK_SUCC",[])
		
		# DEF_FAIL 杀1人奖励防守失败
		self.DEF_FAIL = data.get("DEF_FAIL",[])
		
		# ATK_FAIL 杀1人奖励攻城失败
		self.ATK_FAIL = data.get("ATK_FAIL",[])
		
		# DEF_SUCC 杀1人奖励防守成功
		self.DEF_SUCC = data.get("DEF_SUCC",[])
		
		# holdReward 22点占城奖励
		self.holdReward = data.get("holdReward",[])
		
		# defLevel 防御等级
		self.defLevel = data.get("defLevel",0)
		
		# x 中心位置X
		self.x = data.get("x",0)
		
		# y 中心位置Y
		self.y = data.get("y",0)
		
		# level 城市界别
		self.level = data.get("level",0)
		
		# helpId 帮助说明id
		self.helpId = data.get("helpId",0)
		
		# name 名字
		self.name = data.get("name","")
		
		# fbIds NPC副本id
		self.fbIds = data.get("fbIds",[])
		
		# npcAndms Npc形象
		self.npcAndms = data.get("npcAndms",[])
		
		# occupyCD 占领保护时间cd(秒)
		self.occupyCD = data.get("occupyCD",0)
		
		# atkCD 公鸡保护时间cd(秒)
		self.atkCD = data.get("atkCD",0)
		
		# OpenLv 开放等级(公会等级)
		self.OpenLv = data.get("OpenLv",0)
		
		# guildCitySocre 公会占城积分
		self.guildCitySocre = data.get("guildCitySocre",0)
		
		# isDeclarewar 是否要宣战
		self.isDeclarewar = data.get("isDeclarewar",0)
		
		# BuildImg 城市图片
		self.BuildImg = data.get("BuildImg","")
		
		# lines 绿线
		self.lines = data.get("lines",[])
		
		# showReward 特产奖励
		self.arrayint2tomap("showReward", data.get("showReward",[]))
		
		# info 城市介绍
		self.info = data.get("info","")
		
		# gbinfo 占城广播
		self.gbinfo = data.get("gbinfo","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengGangRank
class ResGongchengGangRank(object):
	RES_TABLE = "gongchengGangRank"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id 跨服boss排行
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 跨服boss排行
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengActive
class ResGongchengActive(object):
	RES_TABLE = "gongchengActive"
	__slots__ = ("id","openDay","lastDay","lastDayRank","reward1","reward2",)

	def __init__(self):
		
		# id 攻城期号表
		self.id = 0
		
		# openDay 开服第X天开启
		self.openDay = 0
		
		# lastDay 持续天数
		self.lastDay = 0
		
		# lastDayRank 持续天数（排行榜）
		self.lastDayRank = 0
		
		# reward1 第一名奖励
		self.reward1 = {}
		
		# reward2 其他名奖励
		self.reward2 = {}
		

	def load_from_json(self, data):
		
		# id 攻城期号表
		self.id = data.get("id",0)
		
		# openDay 开服第X天开启
		self.openDay = data.get("openDay",0)
		
		# lastDay 持续天数
		self.lastDay = data.get("lastDay",0)
		
		# lastDayRank 持续天数（排行榜）
		self.lastDayRank = data.get("lastDayRank",0)
		
		# reward1 第一名奖励
		self.arrayint2tomap("reward1", data.get("reward1",[]))
		
		# reward2 其他名奖励
		self.arrayint2tomap("reward2", data.get("reward2",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengLimitReward
class ResGongchengLimitReward(object):
	RES_TABLE = "gongchengLimitReward"
	__slots__ = ("id","cycle","titleIcon","giftIcon","reward","limit","costOld","cost","chargeOld","chargeId",)

	def __init__(self):
		
		# id 攻城限購禮包
		self.id = 0
		
		# cycle 周期
		self.cycle = 0
		
		# titleIcon 名稱圖標
		self.titleIcon = ""
		
		# giftIcon 禮包圖標
		self.giftIcon = ""
		
		# reward 獎勵
		self.reward = {}
		
		# limit 限購次數
		self.limit = 0
		
		# costOld 原價1
		self.costOld = 0
		
		# cost 花費
		self.cost = {}
		
		# chargeOld 原價2
		self.chargeOld = 0
		
		# chargeId 直購關聯充值id
		self.chargeId = []
		

	def load_from_json(self, data):
		
		# id 攻城限購禮包
		self.id = data.get("id",0)
		
		# cycle 周期
		self.cycle = data.get("cycle",0)
		
		# titleIcon 名稱圖標
		self.titleIcon = data.get("titleIcon","")
		
		# giftIcon 禮包圖標
		self.giftIcon = data.get("giftIcon","")
		
		# reward 獎勵
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# limit 限購次數
		self.limit = data.get("limit",0)
		
		# costOld 原價1
		self.costOld = data.get("costOld",0)
		
		# cost 花費
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# chargeOld 原價2
		self.chargeOld = data.get("chargeOld",0)
		
		# chargeId 直購關聯充值id
		self.chargeId = data.get("chargeId",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengTask
class ResGongchengTask(object):
	RES_TABLE = "gongchengTask"
	__slots__ = ("id","cycle","pageOpen","taskOpen","taskEnd","taskList",)

	def __init__(self):
		
		# id 攻城任务页签
		self.id = 0
		
		# cycle 周期
		self.cycle = 0
		
		# pageOpen 页签开启时间(开服第x天)
		self.pageOpen = 0
		
		# taskOpen 任务开始时间(开服第x天)
		self.taskOpen = 0
		
		# taskEnd 任务结束时间(开服第x天)
		self.taskEnd = 0
		
		# taskList 任务列表
		self.taskList = []
		

	def load_from_json(self, data):
		
		# id 攻城任务页签
		self.id = data.get("id",0)
		
		# cycle 周期
		self.cycle = data.get("cycle",0)
		
		# pageOpen 页签开启时间(开服第x天)
		self.pageOpen = data.get("pageOpen",0)
		
		# taskOpen 任务开始时间(开服第x天)
		self.taskOpen = data.get("taskOpen",0)
		
		# taskEnd 任务结束时间(开服第x天)
		self.taskEnd = data.get("taskEnd",0)
		
		# taskList 任务列表
		self.taskList = data.get("taskList",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengShop
class ResGongchengShop(object):
	RES_TABLE = "gongchengShop"
	__slots__ = ("id","limit","cost","reward","cycle",)

	def __init__(self):
		
		# id 攻城商店
		self.id = 0
		
		# limit 限购次数
		self.limit = 0
		
		# cost 花费
		self.cost = {}
		
		# reward 奖励
		self.reward = {}
		
		# cycle 周期
		self.cycle = 0
		

	def load_from_json(self, data):
		
		# id 攻城商店
		self.id = data.get("id",0)
		
		# limit 限购次数
		self.limit = data.get("limit",0)
		
		# cost 花费
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# cycle 周期
		self.cycle = data.get("cycle",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# gongchengLoginReward
class ResGongchengLoginReward(object):
	RES_TABLE = "gongchengLoginReward"
	__slots__ = ("id","cycle","day","reward",)

	def __init__(self):
		
		# id key
		self.id = 0
		
		# cycle 周期
		self.cycle = 0
		
		# day 攻城登陆天数
		self.day = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id key
		self.id = data.get("id",0)
		
		# cycle 周期
		self.cycle = data.get("cycle",0)
		
		# day 攻城登陆天数
		self.day = data.get("day",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# hetiEvo
class ResHetiEvo(object):
	RES_TABLE = "hetiEvo"
	__slots__ = ("id","petIds",)

	def __init__(self):
		
		# id 合体宠物id
		self.id = 0
		
		# petIds 进化等级形象
		self.petIds = []
		

	def load_from_json(self, data):
		
		# id 合体宠物id
		self.id = data.get("id",0)
		
		# petIds 进化等级形象
		self.petIds = data.get("petIds",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# hetiReward
class ResHetiReward(object):
	RES_TABLE = "hetiReward"
	__slots__ = ("id","reward",)

	def __init__(self):
		
		# id 合体奖励表
		self.id = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 合体奖励表
		self.id = data.get("id",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# hetiMake
class ResHetiMake(object):
	RES_TABLE = "hetiMake"
	__slots__ = ("id","level","ver","match",)

	def __init__(self):
		
		# id 合体宠物规则
		self.id = 0
		
		# level 难度
		self.level = 0
		
		# ver 版本
		self.ver = 0
		
		# match 匹配规则
		self.match = []
		

	def load_from_json(self, data):
		
		# id 合体宠物规则
		self.id = data.get("id",0)
		
		# level 难度
		self.level = data.get("level",0)
		
		# ver 版本
		self.ver = data.get("ver",0)
		
		# match 匹配规则
		self.match = data.get("match",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# totemBj
class ResTotemBj(object):
	RES_TABLE = "totemBj"
	__slots__ = ("id","num","multi",)

	def __init__(self):
		
		# id 图腾暴击表
		self.id = 0
		
		# num 暴击需要次数
		self.num = 0
		
		# multi 暴击倍数
		self.multi = 0
		

	def load_from_json(self, data):
		
		# id 图腾暴击表
		self.id = data.get("id",0)
		
		# num 暴击需要次数
		self.num = data.get("num",0)
		
		# multi 暴击倍数
		self.multi = data.get("multi",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# totemRan
class ResTotemRan(object):
	RES_TABLE = "totemRan"
	__slots__ = ("id","num","multi",)

	def __init__(self):
		
		# id 图腾随机暴击表
		self.id = 0
		
		# num 暴击权重
		self.num = 0
		
		# multi 暴击倍数
		self.multi = 0
		

	def load_from_json(self, data):
		
		# id 图腾随机暴击表
		self.id = data.get("id",0)
		
		# num 暴击权重
		self.num = data.get("num",0)
		
		# multi 暴击倍数
		self.multi = data.get("multi",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# totems
class ResTotems(object):
	RES_TABLE = "totems"
	__slots__ = ("id","pos","level","exp","breakLv","ele","cost","tpCost","costPet1","costPet2","specLv","attr1","attr2",)

	def __init__(self):
		
		# id 图腾表
		self.id = 0
		
		# pos 部位
		self.pos = 0
		
		# level 等级
		self.level = 0
		
		# exp 经验
		self.exp = 0
		
		# breakLv 阶数
		self.breakLv = 0
		
		# ele 元素
		self.ele = 0
		
		# cost 每次点击升级消耗
		self.cost = {}
		
		# tpCost 突破消耗
		self.tpCost = {}
		
		# costPet1 消耗指定宠物
		self.costPet1 = []
		
		# costPet2 消耗宠物
		self.costPet2 = []
		
		# specLv 特殊效果等级
		self.specLv = 0
		
		# attr1 激活突破用属性
		self.attr1 = {}
		
		# attr2 小弹窗属性
		self.attr2 = {}
		

	def load_from_json(self, data):
		
		# id 图腾表
		self.id = data.get("id",0)
		
		# pos 部位
		self.pos = data.get("pos",0)
		
		# level 等级
		self.level = data.get("level",0)
		
		# exp 经验
		self.exp = data.get("exp",0)
		
		# breakLv 阶数
		self.breakLv = data.get("breakLv",0)
		
		# ele 元素
		self.ele = data.get("ele",0)
		
		# cost 每次点击升级消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# tpCost 突破消耗
		self.arrayint2tomap("tpCost", data.get("tpCost",[]))
		
		# costPet1 消耗指定宠物
		self.costPet1 = data.get("costPet1",[])
		
		# costPet2 消耗宠物
		self.costPet2 = data.get("costPet2",[])
		
		# specLv 特殊效果等级
		self.specLv = data.get("specLv",0)
		
		# attr1 激活突破用属性
		self.attr1 = data.get("attr1",{})
		
		# attr2 小弹窗属性
		self.attr2 = data.get("attr2",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# activity
class ResActivity(object):
	RES_TABLE = "activity"
	__slots__ = ("id","name","type","group","sort","openDayRange","mergeDayRange","everyday","everyweek","dateRange","level","icon","icon2","prepare","aheadTime","timeInfoStr","CycleNo","param",)

	def __init__(self):
		
		# id 活动表
		self.id = 0
		
		# name 活动名称
		self.name = ""
		
		# type 类型
		self.type = 0
		
		# group 分组
		self.group = 0
		
		# sort 排序
		self.sort = 0
		
		# openDayRange 开服天数时间段（大优先级）
		self.openDayRange = []
		
		# mergeDayRange 合服天数时间段（大优先级）
		self.mergeDayRange = []
		
		# everyday 每日活动（小优先级）
		self.everyday = []
		
		# everyweek 每周活动（小优先级）
		self.everyweek = []
		
		# dateRange 固定日期（小优先级）
		self.dateRange = []
		
		# level 等级需求
		self.level = 0
		
		# icon 按钮图标
		self.icon = ""
		
		# icon2 按钮图标2
		self.icon2 = ""
		
		# prepare 活动准备时间
		self.prepare = 0
		
		# aheadTime 提前x秒事件
		self.aheadTime = 0
		
		# timeInfoStr 时间说明文本
		self.timeInfoStr = ""
		
		# CycleNo 活动期号
		self.CycleNo = 0
		
		# param 传参
		self.param = ""
		

	def load_from_json(self, data):
		
		# id 活动表
		self.id = data.get("id",0)
		
		# name 活动名称
		self.name = data.get("name","")
		
		# type 类型
		self.type = data.get("type",0)
		
		# group 分组
		self.group = data.get("group",0)
		
		# sort 排序
		self.sort = data.get("sort",0)
		
		# openDayRange 开服天数时间段（大优先级）
		self.openDayRange = data.get("openDayRange",[])
		
		# mergeDayRange 合服天数时间段（大优先级）
		self.mergeDayRange = data.get("mergeDayRange",[])
		
		# everyday 每日活动（小优先级）
		self.everyday = data.get("everyday",[])
		
		# everyweek 每周活动（小优先级）
		self.everyweek = data.get("everyweek",[])
		
		# dateRange 固定日期（小优先级）
		self.dateRange = data.get("dateRange",[])
		
		# level 等级需求
		self.level = data.get("level",0)
		
		# icon 按钮图标
		self.icon = data.get("icon","")
		
		# icon2 按钮图标2
		self.icon2 = data.get("icon2","")
		
		# prepare 活动准备时间
		self.prepare = data.get("prepare",0)
		
		# aheadTime 提前x秒事件
		self.aheadTime = data.get("aheadTime",0)
		
		# timeInfoStr 时间说明文本
		self.timeInfoStr = data.get("timeInfoStr","")
		
		# CycleNo 活动期号
		self.CycleNo = data.get("CycleNo",0)
		
		# param 传参
		self.param = data.get("param","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# cycle
class ResCycle(object):
	RES_TABLE = "cycle"
	__slots__ = ("id","activityID","openDayRange","mergeDayRange","day","cycleFuncID",)

	def __init__(self):
		
		# id 周期表
		self.id = 0
		
		# activityID 关联活动id
		self.activityID = 0
		
		# openDayRange [开服天数时间段]
		self.openDayRange = []
		
		# mergeDayRange [合服天数时间段]
		self.mergeDayRange = []
		
		# day [日期]
		self.day = []
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = 0
		

	def load_from_json(self, data):
		
		# id 周期表
		self.id = data.get("id",0)
		
		# activityID 关联活动id
		self.activityID = data.get("activityID",0)
		
		# openDayRange [开服天数时间段]
		self.openDayRange = data.get("openDayRange",[])
		
		# mergeDayRange [合服天数时间段]
		self.mergeDayRange = data.get("mergeDayRange",[])
		
		# day [日期]
		self.day = data.get("day",[])
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = data.get("cycleFuncID",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# activityMain
class ResActivityMain(object):
	RES_TABLE = "activityMain"
	__slots__ = ("key","time","timeInfo","timeInfo2",)

	def __init__(self):
		
		# key 活动大厅表
		self.key = ""
		
		# time 时间
		self.time = []
		
		# timeInfo 界面时间说明1
		self.timeInfo = ""
		
		# timeInfo2 界面时间说明2
		self.timeInfo2 = ""
		

	def load_from_json(self, data):
		
		# key 活动大厅表
		self.key = data.get("key","")
		
		# time 时间
		self.time = data.get("time",[])
		
		# timeInfo 界面时间说明1
		self.timeInfo = data.get("timeInfo","")
		
		# timeInfo2 界面时间说明2
		self.timeInfo2 = data.get("timeInfo2","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# reward
class ResReward(object):
	RES_TABLE = "reward"
	__slots__ = ("id","cond1","type1","pool1","cond2","type2","pool2","cond3","type3","pool3",)

	def __init__(self):
		
		# id 奖励表
		self.id = 0
		
		# cond1 条件
		self.cond1 = 0
		
		# type1 奖池类型
		self.type1 = 0
		
		# pool1 奖池组ID
		self.pool1 = []
		
		# cond2 条件
		self.cond2 = 0
		
		# type2 奖池类型
		self.type2 = 0
		
		# pool2 奖池组ID
		self.pool2 = []
		
		# cond3 条件
		self.cond3 = 0
		
		# type3 奖池类型
		self.type3 = 0
		
		# pool3 奖池组ID
		self.pool3 = []
		

	def load_from_json(self, data):
		
		# id 奖励表
		self.id = data.get("id",0)
		
		# cond1 条件
		self.cond1 = data.get("cond1",0)
		
		# type1 奖池类型
		self.type1 = data.get("type1",0)
		
		# pool1 奖池组ID
		self.pool1 = data.get("pool1",[])
		
		# cond2 条件
		self.cond2 = data.get("cond2",0)
		
		# type2 奖池类型
		self.type2 = data.get("type2",0)
		
		# pool2 奖池组ID
		self.pool2 = data.get("pool2",[])
		
		# cond3 条件
		self.cond3 = data.get("cond3",0)
		
		# type3 奖池类型
		self.type3 = data.get("type3",0)
		
		# pool3 奖池组ID
		self.pool3 = data.get("pool3",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# rewardpool
class ResRewardpool(object):
	RES_TABLE = "rewardpool"
	__slots__ = ("id","group","itemNo","num","rate",)

	def __init__(self):
		
		# id 奖池表
		self.id = 0
		
		# group 奖池组
		self.group = 0
		
		# itemNo 道具ID
		self.itemNo = 0
		
		# num 數量
		self.num = 0
		
		# rate 權重
		self.rate = 0
		

	def load_from_json(self, data):
		
		# id 奖池表
		self.id = data.get("id",0)
		
		# group 奖池组
		self.group = data.get("group",0)
		
		# itemNo 道具ID
		self.itemNo = data.get("itemNo",0)
		
		# num 數量
		self.num = data.get("num",0)
		
		# rate 權重
		self.rate = data.get("rate",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# effect
class ResEffect(object):
	RES_TABLE = "effect"
	__slots__ = ("id","group","order","actPoint","target","cond","condArgs","goOn","effType","effArgs",)

	def __init__(self):
		
		# id 技能效果表
		self.id = 0
		
		# group 分组id
		self.group = 0
		
		# order 执行顺序
		self.order = 0
		
		# actPoint 触发时机
		self.actPoint = 0
		
		# target 目标选择
		self.target = ""
		
		# cond 条件
		self.cond = 0
		
		# condArgs 条件参数
		self.condArgs = ""
		
		# goOn 是否向下执行
		self.goOn = 0
		
		# effType 效果类型
		self.effType = 0
		
		# effArgs 参数
		self.effArgs = ""
		

	def load_from_json(self, data):
		
		# id 技能效果表
		self.id = data.get("id",0)
		
		# group 分组id
		self.group = data.get("group",0)
		
		# order 执行顺序
		self.order = data.get("order",0)
		
		# actPoint 触发时机
		self.actPoint = data.get("actPoint",0)
		
		# target 目标选择
		self.target = data.get("target","")
		
		# cond 条件
		self.cond = data.get("cond",0)
		
		# condArgs 条件参数
		self.condArgs = data.get("condArgs","")
		
		# goOn 是否向下执行
		self.goOn = data.get("goOn",0)
		
		# effType 效果类型
		self.effType = data.get("effType",0)
		
		# effArgs 参数
		self.effArgs = data.get("effArgs","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# buff
class ResBuff(object):
	RES_TABLE = "buff"
	__slots__ = ("id","ficon","fname","fdesc","delay","effect",)

	def __init__(self):
		
		# id BUFF表
		self.id = 0
		
		# ficon 战斗-buff图标
		self.ficon = ""
		
		# fname 战斗-tips名字
		self.fname = ""
		
		# fdesc 战斗-tips描述
		self.fdesc = ""
		
		# delay 延时消除
		self.delay = 0
		
		# effect 技能效果组
		self.effect = 0
		

	def load_from_json(self, data):
		
		# id BUFF表
		self.id = data.get("id",0)
		
		# ficon 战斗-buff图标
		self.ficon = data.get("ficon","")
		
		# fname 战斗-tips名字
		self.fname = data.get("fname","")
		
		# fdesc 战斗-tips描述
		self.fdesc = data.get("fdesc","")
		
		# delay 延时消除
		self.delay = data.get("delay",0)
		
		# effect 技能效果组
		self.effect = data.get("effect",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# skill
class ResSkill(object):
	RES_TABLE = "skill"
	__slots__ = ("id","skillId","level","name","type","subType","needLv","quality","attr","upCost","active","cd","effect",)

	def __init__(self):
		
		# id 技能表
		self.id = 0
		
		# skillId 技能Id
		self.skillId = 0
		
		# level 等级
		self.level = 0
		
		# name 名称
		self.name = ""
		
		# type 类型
		self.type = 0
		
		# subType 子类型(目前仅洗炼特性用)
		self.subType = 0
		
		# needLv 等级需求
		self.needLv = 0
		
		# quality 品质
		self.quality = 0
		
		# attr 增加属性
		self.attr = {}
		
		# upCost 升级消耗
		self.upCost = {}
		
		# active 是否主动技能
		self.active = 0
		
		# cd 冷却cd
		self.cd = 0
		
		# effect 技能效果组
		self.effect = 0
		

	def load_from_json(self, data):
		
		# id 技能表
		self.id = data.get("id",0)
		
		# skillId 技能Id
		self.skillId = data.get("skillId",0)
		
		# level 等级
		self.level = data.get("level",0)
		
		# name 名称
		self.name = data.get("name","")
		
		# type 类型
		self.type = data.get("type",0)
		
		# subType 子类型(目前仅洗炼特性用)
		self.subType = data.get("subType",0)
		
		# needLv 等级需求
		self.needLv = data.get("needLv",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# attr 增加属性
		self.attr = data.get("attr",{})
		
		# upCost 升级消耗
		self.arrayint2tomap("upCost", data.get("upCost",[]))
		
		# active 是否主动技能
		self.active = data.get("active",0)
		
		# cd 冷却cd
		self.cd = data.get("cd",0)
		
		# effect 技能效果组
		self.effect = data.get("effect",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# rescueReward
class ResRescueReward(object):
	RES_TABLE = "rescueReward"
	__slots__ = ("id","score","reward",)

	def __init__(self):
		
		# id 救援领奖
		self.id = 0
		
		# score 需求
		self.score = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 救援领奖
		self.id = data.get("id",0)
		
		# score 需求
		self.score = data.get("score",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# rescueSystem
class ResRescueSystem(object):
	RES_TABLE = "rescueSystem"
	__slots__ = ("id","worldId","petId","heightStr","weightStr","desc","mapsubid","num1","num2","num3","num4","num5","icon1","icon2","icon3","icon4","icon5","tipid1","tipid2","tipid3","tipid4","tipid5",)

	def __init__(self):
		
		# id 救援表
		self.id = 0
		
		# worldId 世界地圖表id
		self.worldId = 0
		
		# petId 寵物表id
		self.petId = 0
		
		# heightStr 身高
		self.heightStr = ""
		
		# weightStr 體重
		self.weightStr = ""
		
		# desc 說明
		self.desc = ""
		
		# mapsubid 需求關卡id
		self.mapsubid = 0
		
		# num1 需求數量1
		self.num1 = 0
		
		# num2 需求數量2
		self.num2 = 0
		
		# num3 需求數量3
		self.num3 = 0
		
		# num4 需求數量4
		self.num4 = 0
		
		# num5 需求數量5
		self.num5 = 0
		
		# icon1 icon1
		self.icon1 = ""
		
		# icon2 icon2
		self.icon2 = ""
		
		# icon3 icon3
		self.icon3 = ""
		
		# icon4 icon4
		self.icon4 = ""
		
		# icon5 icon5
		self.icon5 = ""
		
		# tipid1 tip1
		self.tipid1 = ""
		
		# tipid2 tip2
		self.tipid2 = ""
		
		# tipid3 tip3
		self.tipid3 = ""
		
		# tipid4 tip4
		self.tipid4 = ""
		
		# tipid5 tip5
		self.tipid5 = ""
		

	def load_from_json(self, data):
		
		# id 救援表
		self.id = data.get("id",0)
		
		# worldId 世界地圖表id
		self.worldId = data.get("worldId",0)
		
		# petId 寵物表id
		self.petId = data.get("petId",0)
		
		# heightStr 身高
		self.heightStr = data.get("heightStr","")
		
		# weightStr 體重
		self.weightStr = data.get("weightStr","")
		
		# desc 說明
		self.desc = data.get("desc","")
		
		# mapsubid 需求關卡id
		self.mapsubid = data.get("mapsubid",0)
		
		# num1 需求數量1
		self.num1 = data.get("num1",0)
		
		# num2 需求數量2
		self.num2 = data.get("num2",0)
		
		# num3 需求數量3
		self.num3 = data.get("num3",0)
		
		# num4 需求數量4
		self.num4 = data.get("num4",0)
		
		# num5 需求數量5
		self.num5 = data.get("num5",0)
		
		# icon1 icon1
		self.icon1 = data.get("icon1","")
		
		# icon2 icon2
		self.icon2 = data.get("icon2","")
		
		# icon3 icon3
		self.icon3 = data.get("icon3","")
		
		# icon4 icon4
		self.icon4 = data.get("icon4","")
		
		# icon5 icon5
		self.icon5 = data.get("icon5","")
		
		# tipid1 tip1
		self.tipid1 = data.get("tipid1","")
		
		# tipid2 tip2
		self.tipid2 = data.get("tipid2","")
		
		# tipid3 tip3
		self.tipid3 = data.get("tipid3","")
		
		# tipid4 tip4
		self.tipid4 = data.get("tipid4","")
		
		# tipid5 tip5
		self.tipid5 = data.get("tipid5","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# marryGift
class ResMarryGift(object):
	RES_TABLE = "marryGift"
	__slots__ = ("id","cost","reward",)

	def __init__(self):
		
		# id 礼金表
		self.id = 0
		
		# cost 消耗
		self.cost = {}
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 礼金表
		self.id = data.get("id",0)
		
		# cost 消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# marryPower
class ResMarryPower(object):
	RES_TABLE = "marryPower"
	__slots__ = ("id","cost","type","add","cd","enlimit","uselimit","trueLove",)

	def __init__(self):
		
		# id 亲密度
		self.id = 0
		
		# cost 消耗
		self.cost = {}
		
		# type 类型
		self.type = 0
		
		# add 增加亲密度
		self.add = 0
		
		# cd 能量恢复时间0不恢复
		self.cd = 0
		
		# enlimit 能量上限0没有能量需求
		self.enlimit = 0
		
		# uselimit 每天使用限制0不限制
		self.uselimit = 0
		
		# trueLove 放入真爱邮箱
		self.trueLove = 0
		

	def load_from_json(self, data):
		
		# id 亲密度
		self.id = data.get("id",0)
		
		# cost 消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# type 类型
		self.type = data.get("type",0)
		
		# add 增加亲密度
		self.add = data.get("add",0)
		
		# cd 能量恢复时间0不恢复
		self.cd = data.get("cd",0)
		
		# enlimit 能量上限0没有能量需求
		self.enlimit = data.get("enlimit",0)
		
		# uselimit 每天使用限制0不限制
		self.uselimit = data.get("uselimit",0)
		
		# trueLove 放入真爱邮箱
		self.trueLove = data.get("trueLove",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# rescueTask
class ResRescueTask(object):
	RES_TABLE = "rescueTask"
	__slots__ = ("id","name","star","w","petid","eleType","showStar","explore","hour","cost","reward","rescueSystemKey","rescueAuto",)

	def __init__(self):
		
		# id 派遣任务id
		self.id = 0
		
		# name 任务名字
		self.name = ""
		
		# star 任务品质（星星
		self.star = 0
		
		# w 权重
		self.w = 0
		
		# petid 需要宠物id
		self.petid = []
		
		# eleType 需求宠物属性
		self.eleType = []
		
		# showStar 需要宠物星
		self.showStar = []
		
		# explore 消耗探索值
		self.explore = {}
		
		# hour 任务时间（小时
		self.hour = 0
		
		# cost 加速花费(1小时
		self.cost = {}
		
		# reward 奖励
		self.reward = {}
		
		# rescueSystemKey 救援id_位置
		self.rescueSystemKey = {}
		
		# rescueAuto 救援任意撒(几个
		self.rescueAuto = 0
		

	def load_from_json(self, data):
		
		# id 派遣任务id
		self.id = data.get("id",0)
		
		# name 任务名字
		self.name = data.get("name","")
		
		# star 任务品质（星星
		self.star = data.get("star",0)
		
		# w 权重
		self.w = data.get("w",0)
		
		# petid 需要宠物id
		self.petid = data.get("petid",[])
		
		# eleType 需求宠物属性
		self.eleType = data.get("eleType",[])
		
		# showStar 需要宠物星
		self.showStar = data.get("showStar",[])
		
		# explore 消耗探索值
		self.arrayint2tomap("explore", data.get("explore",[]))
		
		# hour 任务时间（小时
		self.hour = data.get("hour",0)
		
		# cost 加速花费(1小时
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# rescueSystemKey 救援id_位置
		self.arrayint2tomap("rescueSystemKey", data.get("rescueSystemKey",[]))
		
		# rescueAuto 救援任意撒(几个
		self.rescueAuto = data.get("rescueAuto",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# house
class ResHouse(object):
	RES_TABLE = "house"
	__slots__ = ("id","exp","cost","addExp","common","high","luxury",)

	def __init__(self):
		
		# id 房子表
		self.id = 0
		
		# exp 升阶经验
		self.exp = 0
		
		# cost 每次点击升级消耗
		self.cost = {}
		
		# addExp 每次点击升级获得经验
		self.addExp = 0
		
		# common 普通
		self.common = {}
		
		# high 高级
		self.high = {}
		
		# luxury 豪华
		self.luxury = {}
		

	def load_from_json(self, data):
		
		# id 房子表
		self.id = data.get("id",0)
		
		# exp 升阶经验
		self.exp = data.get("exp",0)
		
		# cost 每次点击升级消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# addExp 每次点击升级获得经验
		self.addExp = data.get("addExp",0)
		
		# common 普通
		self.common = data.get("common",{})
		
		# high 高级
		self.high = data.get("high",{})
		
		# luxury 豪华
		self.luxury = data.get("luxury",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# marry
class ResMarry(object):
	RES_TABLE = "marry"
	__slots__ = ("id","cost","firstReward","reward",)

	def __init__(self):
		
		# id 结婚档次表
		self.id = 0
		
		# cost 消耗
		self.cost = {}
		
		# firstReward 首次奖励
		self.firstReward = {}
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 结婚档次表
		self.id = data.get("id",0)
		
		# cost 消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# firstReward 首次奖励
		self.arrayint2tomap("firstReward", data.get("firstReward",[]))
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# marryLv
class ResMarryLv(object):
	RES_TABLE = "marryLv"
	__slots__ = ("id","power","needExp","reward",)

	def __init__(self):
		
		# id 等级
		self.id = 0
		
		# power 等级需求
		self.power = 0
		
		# needExp 下级需求
		self.needExp = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 等级
		self.id = data.get("id",0)
		
		# power 等级需求
		self.power = data.get("power",0)
		
		# needExp 下级需求
		self.needExp = data.get("needExp",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# level
class ResLevel(object):
	RES_TABLE = "level"
	__slots__ = ("level","exp",)

	def __init__(self):
		
		# level 角色等级表
		self.level = 0
		
		# exp 经验
		self.exp = 0
		

	def load_from_json(self, data):
		
		# level 角色等级表
		self.level = data.get("level",0)
		
		# exp 经验
		self.exp = data.get("exp",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# roleinit
class ResRoleinit(object):
	RES_TABLE = "roleinit"
	__slots__ = ("key","i","arrayint2",)

	def __init__(self):
		
		# key 角色初始化表
		self.key = ""
		
		# i 正整数
		self.i = 0
		
		# arrayint2 二维数组（整形）
		self.arrayint2 = {}
		

	def load_from_json(self, data):
		
		# key 角色初始化表
		self.key = data.get("key","")
		
		# i 正整数
		self.i = data.get("i",0)
		
		# arrayint2 二维数组（整形）
		self.arrayint2tomap("arrayint2", data.get("arrayint2",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# kuafuMap
class ResKuafuMap(object):
	RES_TABLE = "kuafuMap"
	__slots__ = ("id","serverNo","serverNoClient",)

	def __init__(self):
		
		# id 映射数字编号
		self.id = 0
		
		# serverNo 真实服务器编号
		self.serverNo = ""
		
		# serverNoClient 服id前端用
		self.serverNoClient = ""
		

	def load_from_json(self, data):
		
		# id 映射数字编号
		self.id = data.get("id",0)
		
		# serverNo 真实服务器编号
		self.serverNo = data.get("serverNo","")
		
		# serverNoClient 服id前端用
		self.serverNoClient = data.get("serverNoClient","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# kuafuGroup
class ResKuafuGroup(object):
	RES_TABLE = "kuafuGroup"
	__slots__ = ("id","sid","type","num",)

	def __init__(self):
		
		# id id
		self.id = 0
		
		# sid 映射数字编号
		self.sid = []
		
		# type 模块id
		self.type = 0
		
		# num 内分组数量
		self.num = 0
		

	def load_from_json(self, data):
		
		# id id
		self.id = data.get("id",0)
		
		# sid 映射数字编号
		self.sid = data.get("sid",[])
		
		# type 模块id
		self.type = data.get("type",0)
		
		# num 内分组数量
		self.num = data.get("num",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# serverMergeMap
class ResServerMergeMap(object):
	RES_TABLE = "serverMergeMap"
	__slots__ = ("serverNo","curMain",)

	def __init__(self):
		
		# serverNo 真实服务器编号
		self.serverNo = ""
		
		# curMain 当前从属主服
		self.curMain = ""
		

	def load_from_json(self, data):
		
		# serverNo 真实服务器编号
		self.serverNo = data.get("serverNo","")
		
		# curMain 当前从属主服
		self.curMain = data.get("curMain","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# kuafuServerNo
class ResKuafuServerNo(object):
	RES_TABLE = "kuafuServerNo"
	__slots__ = ("serverNo","serverNoClient","type",)

	def __init__(self):
		
		# serverNo 真实服务器编号
		self.serverNo = ""
		
		# serverNoClient 服id前端用
		self.serverNoClient = ""
		
		# type 渠道分组
		self.type = 0
		

	def load_from_json(self, data):
		
		# serverNo 真实服务器编号
		self.serverNo = data.get("serverNo","")
		
		# serverNoClient 服id前端用
		self.serverNoClient = data.get("serverNoClient","")
		
		# type 渠道分组
		self.type = data.get("type",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# MagicLamp
class ResMagicLamp(object):
	RES_TABLE = "MagicLamp"
	__slots__ = ("id","content","num","particle",)

	def __init__(self):
		
		# id 聊天模板表
		self.id = 0
		
		# content 内容
		self.content = ""
		
		# num 次数
		self.num = 0
		
		# particle 栗子
		self.particle = ""
		

	def load_from_json(self, data):
		
		# id 聊天模板表
		self.id = data.get("id",0)
		
		# content 内容
		self.content = data.get("content","")
		
		# num 次数
		self.num = data.get("num",0)
		
		# particle 栗子
		self.particle = data.get("particle","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# chat
class ResChat(object):
	RES_TABLE = "chat"
	__slots__ = ("id","type","content","MagicLampId",)

	def __init__(self):
		
		# id 聊天模板表
		self.id = 0
		
		# type 类型
		self.type = 0
		
		# content 内容内容不填聊天框则没有消息内容不填聊天框则没有消息内容不填聊天框则没有消息内容不填聊天框则没有消息
		self.content = ""
		
		# MagicLampId 走马灯ID
		self.MagicLampId = 0
		

	def load_from_json(self, data):
		
		# id 聊天模板表
		self.id = data.get("id",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# content 内容内容不填聊天框则没有消息内容不填聊天框则没有消息内容不填聊天框则没有消息内容不填聊天框则没有消息
		self.content = data.get("content","")
		
		# MagicLampId 走马灯ID
		self.MagicLampId = data.get("MagicLampId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# niudanFuhua
class ResNiudanFuhua(object):
	RES_TABLE = "niudanFuhua"
	__slots__ = ("cycleFuncID","needs","reward","baodiNum",)

	def __init__(self):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = 0
		
		# needs 抽奖次数要求
		self.needs = []
		
		# reward 奖励
		self.reward = []
		
		# baodiNum 前端宠物形象
		self.baodiNum = []
		

	def load_from_json(self, data):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = data.get("cycleFuncID",0)
		
		# needs 抽奖次数要求
		self.needs = data.get("needs",[])
		
		# reward 奖励
		self.reward = data.get("reward",[])
		
		# baodiNum 前端宠物形象
		self.baodiNum = data.get("baodiNum",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# niudanSystem
class ResNiudanSystem(object):
	RES_TABLE = "niudanSystem"
	__slots__ = ("id","costFree","cd","cost","costRep","costTen","costTenRep","Ten","reward","mod","sysActID","modidx","RollOneResID","ptActID","jyActID",)

	def __init__(self):
		
		# id 扭蛋分类勿动
		self.id = 0
		
		# costFree 是否每天免费N次
		self.costFree = 0
		
		# cd 免费CD秒数
		self.cd = 0
		
		# cost 抽奖1次消费
		self.cost = {}
		
		# costRep 抽奖1次消费代替
		self.costRep = {}
		
		# costTen 抽奖N次消费
		self.costTen = {}
		
		# costTenRep 抽奖N次消费代替
		self.costTenRep = {}
		
		# Ten 抽奖N次消费次数
		self.Ten = 0
		
		# reward 抽奖1次奖励
		self.reward = {}
		
		# mod 模块(RES)
		self.mod = ""
		
		# sysActID 关联系统活动id
		self.sysActID = 0
		
		# modidx 模块index
		self.modidx = 0
		
		# RollOneResID 计数器id
		self.RollOneResID = []
		
		# ptActID 普通池关联活动id
		self.ptActID = 0
		
		# jyActID 精英池关联活动id
		self.jyActID = 0
		

	def load_from_json(self, data):
		
		# id 扭蛋分类勿动
		self.id = data.get("id",0)
		
		# costFree 是否每天免费N次
		self.costFree = data.get("costFree",0)
		
		# cd 免费CD秒数
		self.cd = data.get("cd",0)
		
		# cost 抽奖1次消费
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# costRep 抽奖1次消费代替
		self.arrayint2tomap("costRep", data.get("costRep",[]))
		
		# costTen 抽奖N次消费
		self.arrayint2tomap("costTen", data.get("costTen",[]))
		
		# costTenRep 抽奖N次消费代替
		self.arrayint2tomap("costTenRep", data.get("costTenRep",[]))
		
		# Ten 抽奖N次消费次数
		self.Ten = data.get("Ten",0)
		
		# reward 抽奖1次奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# mod 模块(RES)
		self.mod = data.get("mod","")
		
		# sysActID 关联系统活动id
		self.sysActID = data.get("sysActID",0)
		
		# modidx 模块index
		self.modidx = data.get("modidx",0)
		
		# RollOneResID 计数器id
		self.RollOneResID = data.get("RollOneResID",[])
		
		# ptActID 普通池关联活动id
		self.ptActID = data.get("ptActID",0)
		
		# jyActID 精英池关联活动id
		self.jyActID = data.get("jyActID",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# niudanXianshi
class ResNiudanXianshi(object):
	RES_TABLE = "niudanXianshi"
	__slots__ = ("cycleFuncID","needs","rewardNeeds","pets","baodiNum","reward",)

	def __init__(self):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = 0
		
		# needs 抽奖次数要求
		self.needs = []
		
		# rewardNeeds 奖励
		self.rewardNeeds = []
		
		# pets 前端宠物形象
		self.pets = []
		
		# baodiNum 抽多少次必出次数
		self.baodiNum = []
		
		# reward 抽多少次必出奖励（替换）
		self.reward = []
		

	def load_from_json(self, data):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = data.get("cycleFuncID",0)
		
		# needs 抽奖次数要求
		self.needs = data.get("needs",[])
		
		# rewardNeeds 奖励
		self.rewardNeeds = data.get("rewardNeeds",[])
		
		# pets 前端宠物形象
		self.pets = data.get("pets",[])
		
		# baodiNum 抽多少次必出次数
		self.baodiNum = data.get("baodiNum",[])
		
		# reward 抽多少次必出奖励（替换）
		self.reward = data.get("reward",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# niudanZhenying
class ResNiudanZhenying(object):
	RES_TABLE = "niudanZhenying"
	__slots__ = ("cycleFuncID","needs","reward","baodiNum",)

	def __init__(self):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = 0
		
		# needs 抽奖次数要求
		self.needs = []
		
		# reward 奖励
		self.reward = []
		
		# baodiNum 抽多少次必出次数
		self.baodiNum = []
		

	def load_from_json(self, data):
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = data.get("cycleFuncID",0)
		
		# needs 抽奖次数要求
		self.needs = data.get("needs",[])
		
		# reward 奖励
		self.reward = data.get("reward",[])
		
		# baodiNum 抽多少次必出次数
		self.baodiNum = data.get("baodiNum",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# niudanPool
class ResNiudanPool(object):
	RES_TABLE = "niudanPool"
	__slots__ = ("id","cycleFuncID","scope","Weight","reward",)

	def __init__(self):
		
		# id 扭蛋池
		self.id = 0
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = 0
		
		# scope 抽奖次数区段[]
		self.scope = []
		
		# Weight 权重
		self.Weight = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 扭蛋池
		self.id = data.get("id",0)
		
		# cycleFuncID 周期业务id
		self.cycleFuncID = data.get("cycleFuncID",0)
		
		# scope 抽奖次数区段[]
		self.scope = data.get("scope",[])
		
		# Weight 权重
		self.Weight = data.get("Weight",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# lwbzStarReward
class ResLwbzStarReward(object):
	RES_TABLE = "lwbzStarReward"
	__slots__ = ("id","six","twelve","eighteen",)

	def __init__(self):
		
		# id 龙王宝藏星数奖励表
		self.id = 0
		
		# six 6星奖励
		self.six = {}
		
		# twelve 12星奖励
		self.twelve = {}
		
		# eighteen 18星奖励
		self.eighteen = {}
		

	def load_from_json(self, data):
		
		# id 龙王宝藏星数奖励表
		self.id = data.get("id",0)
		
		# six 6星奖励
		self.arrayint2tomap("six", data.get("six",[]))
		
		# twelve 12星奖励
		self.arrayint2tomap("twelve", data.get("twelve",[]))
		
		# eighteen 18星奖励
		self.arrayint2tomap("eighteen", data.get("eighteen",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# clfb
class ResClfb(object):
	RES_TABLE = "clfb"
	__slots__ = ("id","barrierId","openLv","sweepLv","sweepCost","freeCount","baseSweepCount","name",)

	def __init__(self):
		
		# id 材料副本表
		self.id = 0
		
		# barrierId 副本id
		self.barrierId = []
		
		# openLv 开启等级
		self.openLv = 0
		
		# sweepLv 扫荡等级
		self.sweepLv = 0
		
		# sweepCost 扫荡消耗
		self.sweepCost = {}
		
		# freeCount 免费次数
		self.freeCount = 0
		
		# baseSweepCount 基础扫荡次数
		self.baseSweepCount = 0
		
		# name 副本名字
		self.name = ""
		

	def load_from_json(self, data):
		
		# id 材料副本表
		self.id = data.get("id",0)
		
		# barrierId 副本id
		self.barrierId = data.get("barrierId",[])
		
		# openLv 开启等级
		self.openLv = data.get("openLv",0)
		
		# sweepLv 扫荡等级
		self.sweepLv = data.get("sweepLv",0)
		
		# sweepCost 扫荡消耗
		self.arrayint2tomap("sweepCost", data.get("sweepCost",[]))
		
		# freeCount 免费次数
		self.freeCount = data.get("freeCount",0)
		
		# baseSweepCount 基础扫荡次数
		self.baseSweepCount = data.get("baseSweepCount",0)
		
		# name 副本名字
		self.name = data.get("name","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# xlysBuff
class ResXlysBuff(object):
	RES_TABLE = "xlysBuff"
	__slots__ = ("key","per","cost",)

	def __init__(self):
		
		# key 小雷音寺Buff表勿动
		self.key = ""
		
		# per 增加万分比
		self.per = 0
		
		# cost 第n次购买消耗(最要配置每日能购买多少个cost就要有多少个)
		self.cost = {}
		

	def load_from_json(self, data):
		
		# key 小雷音寺Buff表勿动
		self.key = data.get("key","")
		
		# per 增加万分比
		self.per = data.get("per",0)
		
		# cost 第n次购买消耗(最要配置每日能购买多少个cost就要有多少个)
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# ttsl
class ResTtsl(object):
	RES_TABLE = "ttsl"
	__slots__ = ("id","type","lvClient","firstReward","mstId","barrierId","tipItemId",)

	def __init__(self):
		
		# id 天庭试炼表
		self.id = 0
		
		# type 难度
		self.type = 0
		
		# lvClient 前端关卡
		self.lvClient = 0
		
		# firstReward 首通奖励
		self.firstReward = {}
		
		# mstId 怪物id
		self.mstId = 0
		
		# barrierId 副本id
		self.barrierId = 0
		
		# tipItemId 提示道具id
		self.tipItemId = 0
		

	def load_from_json(self, data):
		
		# id 天庭试炼表
		self.id = data.get("id",0)
		
		# type 难度
		self.type = data.get("type",0)
		
		# lvClient 前端关卡
		self.lvClient = data.get("lvClient",0)
		
		# firstReward 首通奖励
		self.arrayint2tomap("firstReward", data.get("firstReward",[]))
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# barrierId 副本id
		self.barrierId = data.get("barrierId",0)
		
		# tipItemId 提示道具id
		self.tipItemId = data.get("tipItemId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# lwbz
class ResLwbz(object):
	RES_TABLE = "lwbz"
	__slots__ = ("id","type","needTip","baotuNo","baotuId","baotuIdClient","barrierId","star",)

	def __init__(self):
		
		# id 龙王宝藏表
		self.id = 0
		
		# type 难度
		self.type = 0
		
		# needTip 是否需要下一个难度提醒
		self.needTip = 0
		
		# baotuNo 藏宝图序号
		self.baotuNo = 0
		
		# baotuId 藏宝图id
		self.baotuId = 0
		
		# baotuIdClient 藏宝图前端id
		self.baotuIdClient = 0
		
		# barrierId 副本id
		self.barrierId = 0
		
		# star 星数
		self.star = 0
		

	def load_from_json(self, data):
		
		# id 龙王宝藏表
		self.id = data.get("id",0)
		
		# type 难度
		self.type = data.get("type",0)
		
		# needTip 是否需要下一个难度提醒
		self.needTip = data.get("needTip",0)
		
		# baotuNo 藏宝图序号
		self.baotuNo = data.get("baotuNo",0)
		
		# baotuId 藏宝图id
		self.baotuId = data.get("baotuId",0)
		
		# baotuIdClient 藏宝图前端id
		self.baotuIdClient = data.get("baotuIdClient",0)
		
		# barrierId 副本id
		self.barrierId = data.get("barrierId",0)
		
		# star 星数
		self.star = data.get("star",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# xlys
class ResXlys(object):
	RES_TABLE = "xlys"
	__slots__ = ("id","type","level","levelClient","barrierId","mstId","wuxing",)

	def __init__(self):
		
		# id 小雷音寺表
		self.id = 0
		
		# type 难度
		self.type = 0
		
		# level 关卡
		self.level = 0
		
		# levelClient 关卡
		self.levelClient = 0
		
		# barrierId 副本id
		self.barrierId = 0
		
		# mstId 怪物id
		self.mstId = 0
		
		# wuxing 五行
		self.wuxing = []
		

	def load_from_json(self, data):
		
		# id 小雷音寺表
		self.id = data.get("id",0)
		
		# type 难度
		self.type = data.get("type",0)
		
		# level 关卡
		self.level = data.get("level",0)
		
		# levelClient 关卡
		self.levelClient = data.get("levelClient",0)
		
		# barrierId 副本id
		self.barrierId = data.get("barrierId",0)
		
		# mstId 怪物id
		self.mstId = data.get("mstId",0)
		
		# wuxing 五行
		self.wuxing = data.get("wuxing",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# common
class ResCommon(object):
	RES_TABLE = "common"
	__slots__ = ("key","i","s","arraystring2","arrayint1","arrayint2",)

	def __init__(self):
		
		# key 全局数据表
		self.key = ""
		
		# i 正整数
		self.i = 0
		
		# s 字符串
		self.s = ""
		
		# arraystring2 二维数组（字符串）
		self.arraystring2 = {}
		
		# arrayint1 一维数组（整形）
		self.arrayint1 = []
		
		# arrayint2 二维数组（整形）
		self.arrayint2 = []
		

	def load_from_json(self, data):
		
		# key 全局数据表
		self.key = data.get("key","")
		
		# i 正整数
		self.i = data.get("i",0)
		
		# s 字符串
		self.s = data.get("s","")
		
		# arraystring2 二维数组（字符串）
		self.arraystring2tomap("arraystring2", data.get("arraystring2",[]))
		
		# arrayint1 一维数组（整形）
		self.arrayint1 = data.get("arrayint1",[])
		
		# arrayint2 二维数组（整形）
		self.arrayint2 = data.get("arrayint2",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# maincityTopBtn
class ResMaincityTopBtn(object):
	RES_TABLE = "maincityTopBtn"
	__slots__ = ("id","sort","name",)

	def __init__(self):
		
		# id 需要顺下去排不可插、乱
		self.id = 0
		
		# sort 排序数值大的走前面
		self.sort = 0
		
		# name 按钮名字(策划勿动
		self.name = ""
		

	def load_from_json(self, data):
		
		# id 需要顺下去排不可插、乱
		self.id = data.get("id",0)
		
		# sort 排序数值大的走前面
		self.sort = data.get("sort",0)
		
		# name 按钮名字(策划勿动
		self.name = data.get("name","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# task
class ResTask(object):
	RES_TABLE = "task"
	__slots__ = ("id","group","conditon","nextId","type","guideId","num","arg1","arg2","rewardInt","finishReward","bussid",)

	def __init__(self):
		
		# id 任务表
		self.id = 0
		
		# group 任务组id
		self.group = 0
		
		# conditon 领取条件
		self.conditon = []
		
		# nextId 下一个任务id
		self.nextId = 0
		
		# type 类型
		self.type = 0
		
		# guideId 引导id
		self.guideId = 0
		
		# num 任务进度
		self.num = 0
		
		# arg1 参数1
		self.arg1 = ""
		
		# arg2 参数2
		self.arg2 = ""
		
		# rewardInt 进度奖励(正整数）
		self.rewardInt = 0
		
		# finishReward 整体完成奖励
		self.finishReward = {}
		
		# bussid 业务参数
		self.bussid = 0
		

	def load_from_json(self, data):
		
		# id 任务表
		self.id = data.get("id",0)
		
		# group 任务组id
		self.group = data.get("group",0)
		
		# conditon 领取条件
		self.conditon = data.get("conditon",[])
		
		# nextId 下一个任务id
		self.nextId = data.get("nextId",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# guideId 引导id
		self.guideId = data.get("guideId",0)
		
		# num 任务进度
		self.num = data.get("num",0)
		
		# arg1 参数1
		self.arg1 = data.get("arg1","")
		
		# arg2 参数2
		self.arg2 = data.get("arg2","")
		
		# rewardInt 进度奖励(正整数）
		self.rewardInt = data.get("rewardInt",0)
		
		# finishReward 整体完成奖励
		self.arrayint2tomap("finishReward", data.get("finishReward",[]))
		
		# bussid 业务参数
		self.bussid = data.get("bussid",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# shopConst
class ResShopConst(object):
	RES_TABLE = "shopConst"
	__slots__ = ("id","title","costRes","npcIcon","desc","manualgroup","mRefersh","dayRefersh","freeRefersh","freeRecover","costRefersh","costLadder","panelRefersh","btn","type","buyDesc","lockTips","jumpBtn","openid","link","xpos","pageType","pageName",)

	def __init__(self):
		
		# id 商店系统表
		self.id = 0
		
		# title 标题
		self.title = ""
		
		# costRes 资源条显示
		self.costRes = []
		
		# npcIcon npc形象
		self.npcIcon = ""
		
		# desc 左上角描述
		self.desc = ""
		
		# manualgroup 商品组
		self.manualgroup = []
		
		# mRefersh 是否被手动刷新
		self.mRefersh = []
		
		# dayRefersh 是否被系统刷新
		self.dayRefersh = []
		
		# freeRefersh 免费刷次数
		self.freeRefersh = 0
		
		# freeRecover 免费刷恢复秒
		self.freeRecover = 0
		
		# costRefersh 收费刷次数
		self.costRefersh = 0
		
		# costLadder 刷新阶段消耗
		self.costLadder = []
		
		# panelRefersh 面板显示什么时候刷新商店(前端)
		self.panelRefersh = 0
		
		# btn 按钮
		self.btn = ""
		
		# type 显示数量类型
		self.type = []
		
		# buyDesc 购买条件
		self.buyDesc = []
		
		# lockTips 未解锁提示
		self.lockTips = ""
		
		# jumpBtn 跳转按钮文字
		self.jumpBtn = ""
		
		# openid 按钮跳转功能开启表
		self.openid = 0
		
		# link 跳转
		self.link = 0
		
		# xpos 货币的x坐标
		self.xpos = 0
		
		# pageType 分页类型
		self.pageType = []
		
		# pageName 分页名称
		self.pageName = []
		

	def load_from_json(self, data):
		
		# id 商店系统表
		self.id = data.get("id",0)
		
		# title 标题
		self.title = data.get("title","")
		
		# costRes 资源条显示
		self.costRes = data.get("costRes",[])
		
		# npcIcon npc形象
		self.npcIcon = data.get("npcIcon","")
		
		# desc 左上角描述
		self.desc = data.get("desc","")
		
		# manualgroup 商品组
		self.manualgroup = data.get("manualgroup",[])
		
		# mRefersh 是否被手动刷新
		self.mRefersh = data.get("mRefersh",[])
		
		# dayRefersh 是否被系统刷新
		self.dayRefersh = data.get("dayRefersh",[])
		
		# freeRefersh 免费刷次数
		self.freeRefersh = data.get("freeRefersh",0)
		
		# freeRecover 免费刷恢复秒
		self.freeRecover = data.get("freeRecover",0)
		
		# costRefersh 收费刷次数
		self.costRefersh = data.get("costRefersh",0)
		
		# costLadder 刷新阶段消耗
		self.costLadder = data.get("costLadder",[])
		
		# panelRefersh 面板显示什么时候刷新商店(前端)
		self.panelRefersh = data.get("panelRefersh",0)
		
		# btn 按钮
		self.btn = data.get("btn","")
		
		# type 显示数量类型
		self.type = data.get("type",[])
		
		# buyDesc 购买条件
		self.buyDesc = data.get("buyDesc",[])
		
		# lockTips 未解锁提示
		self.lockTips = data.get("lockTips","")
		
		# jumpBtn 跳转按钮文字
		self.jumpBtn = data.get("jumpBtn","")
		
		# openid 按钮跳转功能开启表
		self.openid = data.get("openid",0)
		
		# link 跳转
		self.link = data.get("link",0)
		
		# xpos 货币的x坐标
		self.xpos = data.get("xpos",0)
		
		# pageType 分页类型
		self.pageType = data.get("pageType",[])
		
		# pageName 分页名称
		self.pageName = data.get("pageName",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# shopGroup
class ResShopGroup(object):
	RES_TABLE = "shopGroup"
	__slots__ = ("id","group","w","limitNum","refCycle","cost1","cost2","reward","eff",)

	def __init__(self):
		
		# id 商店表
		self.id = 0
		
		# group 组z
		self.group = 0
		
		# w 权重
		self.w = 0
		
		# limitNum 限购数量
		self.limitNum = 0
		
		# refCycle 刷新周期
		self.refCycle = 0
		
		# cost1 消耗优先代替
		self.cost1 = {}
		
		# cost2 消耗
		self.cost2 = {}
		
		# reward 获得
		self.reward = {}
		
		# eff 商品特效
		self.eff = ""
		

	def load_from_json(self, data):
		
		# id 商店表
		self.id = data.get("id",0)
		
		# group 组z
		self.group = data.get("group",0)
		
		# w 权重
		self.w = data.get("w",0)
		
		# limitNum 限购数量
		self.limitNum = data.get("limitNum",0)
		
		# refCycle 刷新周期
		self.refCycle = data.get("refCycle",0)
		
		# cost1 消耗优先代替
		self.arrayint2tomap("cost1", data.get("cost1",[]))
		
		# cost2 消耗
		self.arrayint2tomap("cost2", data.get("cost2",[]))
		
		# reward 获得
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# eff 商品特效
		self.eff = data.get("eff","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# shopQuick
class ResShopQuick(object):
	RES_TABLE = "shopQuick"
	__slots__ = ("id","shopId","link",)

	def __init__(self):
		
		# id 快速购买表
		self.id = 0
		
		# shopId 关联的商店表Id
		self.shopId = 0
		
		# link 途径id列表
		self.link = []
		

	def load_from_json(self, data):
		
		# id 快速购买表
		self.id = data.get("id",0)
		
		# shopId 关联的商店表Id
		self.shopId = data.get("shopId",0)
		
		# link 途径id列表
		self.link = data.get("link",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# attrbute
class ResAttrbute(object):
	RES_TABLE = "attrbute"
	__slots__ = ("key","name","sortValue","ratio","isPercent","dpoint","icon",)

	def __init__(self):
		
		# key 属性定义key
		self.key = ""
		
		# name 属性名字
		self.name = ""
		
		# sortValue 属性排列
		self.sortValue = 0
		
		# ratio 战斗力系数
		self.ratio = 0
		
		# isPercent 是否万分比显示
		self.isPercent = 0
		
		# dpoint 前端显示保留小数点位数
		self.dpoint = 0
		
		# icon 属性图标
		self.icon = ""
		

	def load_from_json(self, data):
		
		# key 属性定义key
		self.key = data.get("key","")
		
		# name 属性名字
		self.name = data.get("name","")
		
		# sortValue 属性排列
		self.sortValue = data.get("sortValue",0)
		
		# ratio 战斗力系数
		self.ratio = data.get("ratio",0)
		
		# isPercent 是否万分比显示
		self.isPercent = data.get("isPercent",0)
		
		# dpoint 前端显示保留小数点位数
		self.dpoint = data.get("dpoint",0)
		
		# icon 属性图标
		self.icon = data.get("icon","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# myhead
class ResMyhead(object):
	RES_TABLE = "myhead"
	__slots__ = ("id","sort","type","typeName","bg","cost","attr",)

	def __init__(self):
		
		# id 时装表
		self.id = 0
		
		# sort 类型
		self.sort = 0
		
		# type 类型
		self.type = 0
		
		# typeName 类型名
		self.typeName = ""
		
		# bg 底图
		self.bg = ""
		
		# cost 消耗道具
		self.cost = {}
		
		# attr 属性
		self.attr = {}
		

	def load_from_json(self, data):
		
		# id 时装表
		self.id = data.get("id",0)
		
		# sort 类型
		self.sort = data.get("sort",0)
		
		# type 类型
		self.type = data.get("type",0)
		
		# typeName 类型名
		self.typeName = data.get("typeName","")
		
		# bg 底图
		self.bg = data.get("bg","")
		
		# cost 消耗道具
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# condition
class ResCondition(object):
	RES_TABLE = "condition"
	__slots__ = ("id","condition",)

	def __init__(self):
		
		# id 属性定义key
		self.id = 0
		
		# condition 条件
		self.condition = ""
		

	def load_from_json(self, data):
		
		# id 属性定义key
		self.id = data.get("id",0)
		
		# condition 条件
		self.condition = data.get("condition","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# link
class ResLink(object):
	RES_TABLE = "link"
	__slots__ = ("id","name","openId","toBagId","icon","wordinfo",)

	def __init__(self):
		
		# id 途径ID
		self.id = 0
		
		# name 名字
		self.name = ""
		
		# openId 打开界面,对应功能开启表
		self.openId = 0
		
		# toBagId 打开背包跳到道具id
		self.toBagId = []
		
		# icon 途径图片图标(图标全部都在美术路径主界面)
		self.icon = ""
		
		# wordinfo 文字提示说明
		self.wordinfo = ""
		

	def load_from_json(self, data):
		
		# id 途径ID
		self.id = data.get("id",0)
		
		# name 名字
		self.name = data.get("name","")
		
		# openId 打开界面,对应功能开启表
		self.openId = data.get("openId",0)
		
		# toBagId 打开背包跳到道具id
		self.toBagId = data.get("toBagId",[])
		
		# icon 途径图片图标(图标全部都在美术路径主界面)
		self.icon = data.get("icon","")
		
		# wordinfo 文字提示说明
		self.wordinfo = data.get("wordinfo","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# vip
class ResVip(object):
	RES_TABLE = "vip"
	__slots__ = ("id","exp","lineSpacing","dayReward","offper","offtimes","goldExchange","bindExchange","grBossOneKey","qmBossTz","qmBossFh","equipResolveAuto","equipResolve50","ttslOneKey","lwbzOneKey","arenaBuyTimes","clbzSweepCount","clfbSweepAll","guildTaskResetNum","fightSpeed","shopDiscount","ysAuto","addbag","mr300TaskCost","zkfmTaskCost","TaskDesc","daoguanBuyNum","daoguanSweep","pvpbuynum","pvpBuyCost","battleJumpNum","costview","cost","rewardTime","reward","hetiBuyNum",)

	def __init__(self):
		
		# id vip表
		self.id = 0
		
		# exp vip经验
		self.exp = 0
		
		# lineSpacing 描述行间距
		self.lineSpacing = 0
		
		# dayReward vip每日奖励
		self.dayReward = []
		
		# offper 挂机额外万分比
		self.offper = 0
		
		# offtimes 挂机额外次数
		self.offtimes = 0
		
		# goldExchange 金币兑换次数
		self.goldExchange = 0
		
		# bindExchange 绑钻兑换次数
		self.bindExchange = 0
		
		# grBossOneKey 个人boss一键扫荡
		self.grBossOneKey = 0
		
		# qmBossTz 全民boss可购买挑战次数
		self.qmBossTz = 0
		
		# qmBossFh 全民boss是否可复活
		self.qmBossFh = 0
		
		# equipResolveAuto 是否可自动熔炼
		self.equipResolveAuto = 0
		
		# equipResolve50 熔炼50个
		self.equipResolve50 = 0
		
		# ttslOneKey 天庭试炼一键扫荡
		self.ttslOneKey = 0
		
		# lwbzOneKey 龙王宝藏一键挖宝
		self.lwbzOneKey = 0
		
		# arenaBuyTimes 竞技场挑战购买次数
		self.arenaBuyTimes = 0
		
		# clbzSweepCount 材料副本附加扫荡次数
		self.clbzSweepCount = 0
		
		# clfbSweepAll 材料副本一键扫荡
		self.clfbSweepAll = 0
		
		# guildTaskResetNum 帮会任务重置次数
		self.guildTaskResetNum = 0
		
		# fightSpeed 战斗倍数
		self.fightSpeed = 0
		
		# shopDiscount 商店折扣
		self.shopDiscount = 0
		
		# ysAuto 开启异兽空间自动挑战
		self.ysAuto = 0
		
		# addbag 额外增加背包格
		self.addbag = 0
		
		# mr300TaskCost 每日任务每点进度消耗
		self.mr300TaskCost = 0
		
		# zkfmTaskCost 日常对战每点进度消耗
		self.zkfmTaskCost = 0
		
		# TaskDesc 任务一键完成打折
		self.TaskDesc = 0
		
		# daoguanBuyNum 道馆购买挑战次数
		self.daoguanBuyNum = 0
		
		# daoguanSweep 道馆一键扫荡功能
		self.daoguanSweep = 0
		
		# pvpbuynum PVP购买次数
		self.pvpbuynum = 0
		
		# pvpBuyCost PVP购买次数消耗
		self.pvpBuyCost = 0
		
		# battleJumpNum 战斗跳过次数(0没有>0有-1无限)
		self.battleJumpNum = 0
		
		# costview 前端显示礼包价
		self.costview = []
		
		# cost 后端实际礼包价
		self.cost = []
		
		# rewardTime 在线时长领取(秒)
		self.rewardTime = 0
		
		# reward 奖励
		self.reward = []
		
		# hetiBuyNum 合体能购买的次数
		self.hetiBuyNum = 0
		

	def load_from_json(self, data):
		
		# id vip表
		self.id = data.get("id",0)
		
		# exp vip经验
		self.exp = data.get("exp",0)
		
		# lineSpacing 描述行间距
		self.lineSpacing = data.get("lineSpacing",0)
		
		# dayReward vip每日奖励
		self.dayReward = data.get("dayReward",[])
		
		# offper 挂机额外万分比
		self.offper = data.get("offper",0)
		
		# offtimes 挂机额外次数
		self.offtimes = data.get("offtimes",0)
		
		# goldExchange 金币兑换次数
		self.goldExchange = data.get("goldExchange",0)
		
		# bindExchange 绑钻兑换次数
		self.bindExchange = data.get("bindExchange",0)
		
		# grBossOneKey 个人boss一键扫荡
		self.grBossOneKey = data.get("grBossOneKey",0)
		
		# qmBossTz 全民boss可购买挑战次数
		self.qmBossTz = data.get("qmBossTz",0)
		
		# qmBossFh 全民boss是否可复活
		self.qmBossFh = data.get("qmBossFh",0)
		
		# equipResolveAuto 是否可自动熔炼
		self.equipResolveAuto = data.get("equipResolveAuto",0)
		
		# equipResolve50 熔炼50个
		self.equipResolve50 = data.get("equipResolve50",0)
		
		# ttslOneKey 天庭试炼一键扫荡
		self.ttslOneKey = data.get("ttslOneKey",0)
		
		# lwbzOneKey 龙王宝藏一键挖宝
		self.lwbzOneKey = data.get("lwbzOneKey",0)
		
		# arenaBuyTimes 竞技场挑战购买次数
		self.arenaBuyTimes = data.get("arenaBuyTimes",0)
		
		# clbzSweepCount 材料副本附加扫荡次数
		self.clbzSweepCount = data.get("clbzSweepCount",0)
		
		# clfbSweepAll 材料副本一键扫荡
		self.clfbSweepAll = data.get("clfbSweepAll",0)
		
		# guildTaskResetNum 帮会任务重置次数
		self.guildTaskResetNum = data.get("guildTaskResetNum",0)
		
		# fightSpeed 战斗倍数
		self.fightSpeed = data.get("fightSpeed",0)
		
		# shopDiscount 商店折扣
		self.shopDiscount = data.get("shopDiscount",0)
		
		# ysAuto 开启异兽空间自动挑战
		self.ysAuto = data.get("ysAuto",0)
		
		# addbag 额外增加背包格
		self.addbag = data.get("addbag",0)
		
		# mr300TaskCost 每日任务每点进度消耗
		self.mr300TaskCost = data.get("mr300TaskCost",0)
		
		# zkfmTaskCost 日常对战每点进度消耗
		self.zkfmTaskCost = data.get("zkfmTaskCost",0)
		
		# TaskDesc 任务一键完成打折
		self.TaskDesc = data.get("TaskDesc",0)
		
		# daoguanBuyNum 道馆购买挑战次数
		self.daoguanBuyNum = data.get("daoguanBuyNum",0)
		
		# daoguanSweep 道馆一键扫荡功能
		self.daoguanSweep = data.get("daoguanSweep",0)
		
		# pvpbuynum PVP购买次数
		self.pvpbuynum = data.get("pvpbuynum",0)
		
		# pvpBuyCost PVP购买次数消耗
		self.pvpBuyCost = data.get("pvpBuyCost",0)
		
		# battleJumpNum 战斗跳过次数(0没有>0有-1无限)
		self.battleJumpNum = data.get("battleJumpNum",0)
		
		# costview 前端显示礼包价
		self.costview = data.get("costview",[])
		
		# cost 后端实际礼包价
		self.cost = data.get("cost",[])
		
		# rewardTime 在线时长领取(秒)
		self.rewardTime = data.get("rewardTime",0)
		
		# reward 奖励
		self.reward = data.get("reward",[])
		
		# hetiBuyNum 合体能购买的次数
		self.hetiBuyNum = data.get("hetiBuyNum",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# xunlu
class ResXunlu(object):
	RES_TABLE = "xunlu"
	__slots__ = ("id","mapPos1","mapPos2","mapPos3","mapPos4",)

	def __init__(self):
		
		# id 地图id
		self.id = 0
		
		# mapPos1 走路坐标
		self.mapPos1 = []
		
		# mapPos2 
		self.mapPos2 = []
		
		# mapPos3 
		self.mapPos3 = []
		
		# mapPos4 
		self.mapPos4 = []
		

	def load_from_json(self, data):
		
		# id 地图id
		self.id = data.get("id",0)
		
		# mapPos1 走路坐标
		self.mapPos1 = data.get("mapPos1",[])
		
		# mapPos2 
		self.mapPos2 = data.get("mapPos2",[])
		
		# mapPos3 
		self.mapPos3 = data.get("mapPos3",[])
		
		# mapPos4 
		self.mapPos4 = data.get("mapPos4",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# yabiaoreward
class ResYabiaoreward(object):
	RES_TABLE = "yabiaoreward"
	__slots__ = ("quality","reward","rob","weight","broadcast","fuchoubroadcast",)

	def __init__(self):
		
		# quality 押镖奖励表
		self.quality = 0
		
		# reward 奖励
		self.reward = {}
		
		# rob 掠夺/复仇(道具必须一致奖励id有多少这里有多少)
		self.rob = {}
		
		# weight 权重
		self.weight = 0
		
		# broadcast 广播id
		self.broadcast = 0
		
		# fuchoubroadcast 复仇广播id
		self.fuchoubroadcast = 0
		

	def load_from_json(self, data):
		
		# quality 押镖奖励表
		self.quality = data.get("quality",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# rob 掠夺/复仇(道具必须一致奖励id有多少这里有多少)
		self.arrayint2tomap("rob", data.get("rob",[]))
		
		# weight 权重
		self.weight = data.get("weight",0)
		
		# broadcast 广播id
		self.broadcast = data.get("broadcast",0)
		
		# fuchoubroadcast 复仇广播id
		self.fuchoubroadcast = data.get("fuchoubroadcast",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# mail
class ResMail(object):
	RES_TABLE = "mail"
	__slots__ = ("id","title","content",)

	def __init__(self):
		
		# id 邮件模板表
		self.id = 0
		
		# title 邮件标题
		self.title = ""
		
		# content 邮件内容
		self.content = ""
		

	def load_from_json(self, data):
		
		# id 邮件模板表
		self.id = data.get("id",0)
		
		# title 邮件标题
		self.title = data.get("title","")
		
		# content 邮件内容
		self.content = data.get("content","")
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# fightDesc
class ResFightDesc(object):
	RES_TABLE = "fightDesc"
	__slots__ = ("type","fightName","fightBg","title","costJumpLv","costJumpVip","costJump","isCostFree","jumpLv","jumpVip","jump","isFree","directJumpLv","directJumpVip","directJump","isDirectFree","desc","isShowDesc","winOpenId","winBtn1","winBtn2","winBtn3","loseOpenId","loseBtn1","loseBtn2","loseBtn3","loseUpBtn1","loseUpBtn2","loseUpBtn3","loseUpBtn4","cdTime","isRole",)

	def __init__(self):
		
		# type 战斗类型
		self.type = 0
		
		# fightName 战斗结算当前战斗xxxx
		self.fightName = ""
		
		# fightBg 战斗背景
		self.fightBg = ""
		
		# title 标题
		self.title = ""
		
		# costJumpLv 等级可跳过
		self.costJumpLv = 0
		
		# costJumpVip vip几特权可跳过
		self.costJumpVip = 0
		
		# costJump 第几回合显示跳过按钮
		self.costJump = 0
		
		# isCostFree 是否免费
		self.isCostFree = 0
		
		# jumpLv 等级可跳过
		self.jumpLv = 0
		
		# jumpVip vip几特权可跳过
		self.jumpVip = 0
		
		# jump 第几回合显示跳过按钮
		self.jump = 0
		
		# isFree 是否免费
		self.isFree = 0
		
		# directJumpLv 等级可跳过
		self.directJumpLv = 0
		
		# directJumpVip vip几特权可跳过
		self.directJumpVip = 0
		
		# directJump 第几回合显示跳过按钮
		self.directJump = 0
		
		# isDirectFree 是否免费
		self.isDirectFree = 0
		
		# desc 描述
		self.desc = ""
		
		# isShowDesc 是否有右上角描述
		self.isShowDesc = 0
		
		# winOpenId 战斗胜利弹窗
		self.winOpenId = 0
		
		# winBtn1 胜利弹窗按钮
		self.winBtn1 = ""
		
		# winBtn2 胜利弹窗按钮
		self.winBtn2 = ""
		
		# winBtn3 胜利弹窗按钮
		self.winBtn3 = ""
		
		# loseOpenId 失败弹窗
		self.loseOpenId = 0
		
		# loseBtn1 失败弹窗按钮
		self.loseBtn1 = ""
		
		# loseBtn2 失败弹窗按钮
		self.loseBtn2 = ""
		
		# loseBtn3 失败弹窗按钮
		self.loseBtn3 = ""
		
		# loseUpBtn1 失败弹窗提升按钮
		self.loseUpBtn1 = ""
		
		# loseUpBtn2 失败弹窗提升按钮
		self.loseUpBtn2 = ""
		
		# loseUpBtn3 失败弹窗提升按钮
		self.loseUpBtn3 = ""
		
		# loseUpBtn4 失败弹窗提升按钮
		self.loseUpBtn4 = ""
		
		# cdTime 倒计时0或不填则不进行倒计时
		self.cdTime = 0
		
		# isRole 是否有头像信息经验啥d
		self.isRole = 0
		

	def load_from_json(self, data):
		
		# type 战斗类型
		self.type = data.get("type",0)
		
		# fightName 战斗结算当前战斗xxxx
		self.fightName = data.get("fightName","")
		
		# fightBg 战斗背景
		self.fightBg = data.get("fightBg","")
		
		# title 标题
		self.title = data.get("title","")
		
		# costJumpLv 等级可跳过
		self.costJumpLv = data.get("costJumpLv",0)
		
		# costJumpVip vip几特权可跳过
		self.costJumpVip = data.get("costJumpVip",0)
		
		# costJump 第几回合显示跳过按钮
		self.costJump = data.get("costJump",0)
		
		# isCostFree 是否免费
		self.isCostFree = data.get("isCostFree",0)
		
		# jumpLv 等级可跳过
		self.jumpLv = data.get("jumpLv",0)
		
		# jumpVip vip几特权可跳过
		self.jumpVip = data.get("jumpVip",0)
		
		# jump 第几回合显示跳过按钮
		self.jump = data.get("jump",0)
		
		# isFree 是否免费
		self.isFree = data.get("isFree",0)
		
		# directJumpLv 等级可跳过
		self.directJumpLv = data.get("directJumpLv",0)
		
		# directJumpVip vip几特权可跳过
		self.directJumpVip = data.get("directJumpVip",0)
		
		# directJump 第几回合显示跳过按钮
		self.directJump = data.get("directJump",0)
		
		# isDirectFree 是否免费
		self.isDirectFree = data.get("isDirectFree",0)
		
		# desc 描述
		self.desc = data.get("desc","")
		
		# isShowDesc 是否有右上角描述
		self.isShowDesc = data.get("isShowDesc",0)
		
		# winOpenId 战斗胜利弹窗
		self.winOpenId = data.get("winOpenId",0)
		
		# winBtn1 胜利弹窗按钮
		self.winBtn1 = data.get("winBtn1","")
		
		# winBtn2 胜利弹窗按钮
		self.winBtn2 = data.get("winBtn2","")
		
		# winBtn3 胜利弹窗按钮
		self.winBtn3 = data.get("winBtn3","")
		
		# loseOpenId 失败弹窗
		self.loseOpenId = data.get("loseOpenId",0)
		
		# loseBtn1 失败弹窗按钮
		self.loseBtn1 = data.get("loseBtn1","")
		
		# loseBtn2 失败弹窗按钮
		self.loseBtn2 = data.get("loseBtn2","")
		
		# loseBtn3 失败弹窗按钮
		self.loseBtn3 = data.get("loseBtn3","")
		
		# loseUpBtn1 失败弹窗提升按钮
		self.loseUpBtn1 = data.get("loseUpBtn1","")
		
		# loseUpBtn2 失败弹窗提升按钮
		self.loseUpBtn2 = data.get("loseUpBtn2","")
		
		# loseUpBtn3 失败弹窗提升按钮
		self.loseUpBtn3 = data.get("loseUpBtn3","")
		
		# loseUpBtn4 失败弹窗提升按钮
		self.loseUpBtn4 = data.get("loseUpBtn4","")
		
		# cdTime 倒计时0或不填则不进行倒计时
		self.cdTime = data.get("cdTime",0)
		
		# isRole 是否有头像信息经验啥d
		self.isRole = data.get("isRole",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petEquipAttr
class ResPetEquipAttr(object):
	RES_TABLE = "petEquipAttr"
	__slots__ = ("id","attrType","baseVal","addVal","vice","q",)

	def __init__(self):
		
		# id 宠物装备属性
		self.id = 0
		
		# attrType 属性类型
		self.attrType = ""
		
		# baseVal 初始生成值
		self.baseVal = 0
		
		# addVal 每强化1级增加值
		self.addVal = 0
		
		# vice 是否副属性
		self.vice = 0
		
		# q 对应品质
		self.q = 0
		

	def load_from_json(self, data):
		
		# id 宠物装备属性
		self.id = data.get("id",0)
		
		# attrType 属性类型
		self.attrType = data.get("attrType","")
		
		# baseVal 初始生成值
		self.baseVal = data.get("baseVal",0)
		
		# addVal 每强化1级增加值
		self.addVal = data.get("addVal",0)
		
		# vice 是否副属性
		self.vice = data.get("vice",0)
		
		# q 对应品质
		self.q = data.get("q",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# equip
class ResEquip(object):
	RES_TABLE = "equip"
	__slots__ = ("id","name","type","pos","level","star","quality","skills","page","attr","godAttr","godNextId","godUpgradeCost","recycl1","recycl2","recycl3","chatId",)

	def __init__(self):
		
		# id 装备表
		self.id = 0
		
		# name 物品名称
		self.name = ""
		
		# type 类型
		self.type = 0
		
		# pos 部位
		self.pos = 0
		
		# level 等级
		self.level = 0
		
		# star 星级
		self.star = 0
		
		# quality 品质
		self.quality = 0
		
		# skills 技能列表
		self.skills = []
		
		# page 分页
		self.page = 0
		
		# attr 属性
		self.attr = {}
		
		# godAttr 神装极品属性
		self.godAttr = {}
		
		# godNextId 神装下级装备id
		self.godNextId = 0
		
		# godUpgradeCost 神装升级消耗
		self.godUpgradeCost = {}
		
		# recycl1 装备熔炼
		self.recycl1 = {}
		
		# recycl2 法宝分解
		self.recycl2 = {}
		
		# recycl3 神装分解
		self.recycl3 = {}
		
		# chatId 广播ID
		self.chatId = 0
		

	def load_from_json(self, data):
		
		# id 装备表
		self.id = data.get("id",0)
		
		# name 物品名称
		self.name = data.get("name","")
		
		# type 类型
		self.type = data.get("type",0)
		
		# pos 部位
		self.pos = data.get("pos",0)
		
		# level 等级
		self.level = data.get("level",0)
		
		# star 星级
		self.star = data.get("star",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# skills 技能列表
		self.skills = data.get("skills",[])
		
		# page 分页
		self.page = data.get("page",0)
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		# godAttr 神装极品属性
		self.godAttr = data.get("godAttr",{})
		
		# godNextId 神装下级装备id
		self.godNextId = data.get("godNextId",0)
		
		# godUpgradeCost 神装升级消耗
		self.arrayint2tomap("godUpgradeCost", data.get("godUpgradeCost",[]))
		
		# recycl1 装备熔炼
		self.arrayint2tomap("recycl1", data.get("recycl1",[]))
		
		# recycl2 法宝分解
		self.arrayint2tomap("recycl2", data.get("recycl2",[]))
		
		# recycl3 神装分解
		self.arrayint2tomap("recycl3", data.get("recycl3",[]))
		
		# chatId 广播ID
		self.chatId = data.get("chatId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petEquipUpgrade
class ResPetEquipUpgrade(object):
	RES_TABLE = "petEquipUpgrade"
	__slots__ = ("id","quality","lv","viceAdd","cost","recycl",)

	def __init__(self):
		
		# id 宠物装备强化
		self.id = 0
		
		# quality 品质
		self.quality = 0
		
		# lv 强化等级
		self.lv = 0
		
		# viceAdd 增加副属性条数
		self.viceAdd = 0
		
		# cost 消耗
		self.cost = {}
		
		# recycl 分解返还
		self.recycl = {}
		

	def load_from_json(self, data):
		
		# id 宠物装备强化
		self.id = data.get("id",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# lv 强化等级
		self.lv = data.get("lv",0)
		
		# viceAdd 增加副属性条数
		self.viceAdd = data.get("viceAdd",0)
		
		# cost 消耗
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# recycl 分解返还
		self.arrayint2tomap("recycl", data.get("recycl",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petEquipSuit
class ResPetEquipSuit(object):
	RES_TABLE = "petEquipSuit"
	__slots__ = ("id","suitType","need","attr","skillId",)

	def __init__(self):
		
		# id 宠物装备套装
		self.id = 0
		
		# suitType 套装类型
		self.suitType = 0
		
		# need 需求件数
		self.need = 0
		
		# attr 属性
		self.attr = {}
		
		# skillId 技能id
		self.skillId = 0
		

	def load_from_json(self, data):
		
		# id 宠物装备套装
		self.id = data.get("id",0)
		
		# suitType 套装类型
		self.suitType = data.get("suitType",0)
		
		# need 需求件数
		self.need = data.get("need",0)
		
		# attr 属性
		self.attr = data.get("attr",{})
		
		# skillId 技能id
		self.skillId = data.get("skillId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# equipaddlv
class ResEquipaddlv(object):
	RES_TABLE = "equipaddlv"
	__slots__ = ("id","equipLv","quality","rate",)

	def __init__(self):
		
		# id 装备附加等级表
		self.id = 0
		
		# equipLv 装备阶数
		self.equipLv = 0
		
		# quality 装备品质
		self.quality = 0
		
		# rate 权重
		self.rate = []
		

	def load_from_json(self, data):
		
		# id 装备附加等级表
		self.id = data.get("id",0)
		
		# equipLv 装备阶数
		self.equipLv = data.get("equipLv",0)
		
		# quality 装备品质
		self.quality = data.get("quality",0)
		
		# rate 权重
		self.rate = data.get("rate",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# petEquip
class ResPetEquip(object):
	RES_TABLE = "petEquip"
	__slots__ = ("id","name","needLv","pos","quality","suitType","mainPool","vicePool","viceNum","type","page","chatId",)

	def __init__(self):
		
		# id 宠物装备表
		self.id = 0
		
		# name 物品名称
		self.name = ""
		
		# needLv 穿戴等级
		self.needLv = 0
		
		# pos 部位
		self.pos = 0
		
		# quality 品质
		self.quality = 0
		
		# suitType 套装类型
		self.suitType = 0
		
		# mainPool 主属性池子
		self.mainPool = []
		
		# vicePool 副属性池子
		self.vicePool = []
		
		# viceNum 初始副属性条数
		self.viceNum = []
		
		# type 类型
		self.type = 0
		
		# page 分页
		self.page = 0
		
		# chatId 广播ID
		self.chatId = 0
		

	def load_from_json(self, data):
		
		# id 宠物装备表
		self.id = data.get("id",0)
		
		# name 物品名称
		self.name = data.get("name","")
		
		# needLv 穿戴等级
		self.needLv = data.get("needLv",0)
		
		# pos 部位
		self.pos = data.get("pos",0)
		
		# quality 品质
		self.quality = data.get("quality",0)
		
		# suitType 套装类型
		self.suitType = data.get("suitType",0)
		
		# mainPool 主属性池子
		self.mainPool = data.get("mainPool",[])
		
		# vicePool 副属性池子
		self.vicePool = data.get("vicePool",[])
		
		# viceNum 初始副属性条数
		self.viceNum = data.get("viceNum",[])
		
		# type 类型
		self.type = data.get("type",0)
		
		# page 分页
		self.page = data.get("page",0)
		
		# chatId 广播ID
		self.chatId = data.get("chatId",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# zhudaoxunliReward
class ResZhudaoxunliReward(object):
	RES_TABLE = "zhudaoxunliReward"
	__slots__ = ("id","qihao","need","reward","rewardVip",)

	def __init__(self):
		
		# id id
		self.id = 0
		
		# qihao 期号
		self.qihao = 0
		
		# need 需求
		self.need = 0
		
		# reward 固定奖励
		self.reward = {}
		
		# rewardVip 特权奖励
		self.rewardVip = {}
		

	def load_from_json(self, data):
		
		# id id
		self.id = data.get("id",0)
		
		# qihao 期号
		self.qihao = data.get("qihao",0)
		
		# need 需求
		self.need = data.get("need",0)
		
		# reward 固定奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		# rewardVip 特权奖励
		self.arrayint2tomap("rewardVip", data.get("rewardVip",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# zhudaoxunliDay
class ResZhudaoxunliDay(object):
	RES_TABLE = "zhudaoxunliDay"
	__slots__ = ("id","start","buyDay","end","charge",)

	def __init__(self):
		
		# id 期号
		self.id = 0
		
		# start 开始天数包含
		self.start = 0
		
		# buyDay 开始n天后可购买等级
		self.buyDay = 0
		
		# end 结束天数包含
		self.end = 0
		
		# charge 充值表id
		self.charge = []
		

	def load_from_json(self, data):
		
		# id 期号
		self.id = data.get("id",0)
		
		# start 开始天数包含
		self.start = data.get("start",0)
		
		# buyDay 开始n天后可购买等级
		self.buyDay = data.get("buyDay",0)
		
		# end 结束天数包含
		self.end = data.get("end",0)
		
		# charge 充值表id
		self.charge = data.get("charge",[])
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# zhuanpanPool
class ResZhuanpanPool(object):
	RES_TABLE = "zhuanpanPool"
	__slots__ = ("id","sys","idx","Weight","reward",)

	def __init__(self):
		
		# id 转盘池
		self.id = 0
		
		# sys 归属系统
		self.sys = 0
		
		# idx 归属格子
		self.idx = 0
		
		# Weight 权重
		self.Weight = 0
		
		# reward 奖励
		self.reward = {}
		

	def load_from_json(self, data):
		
		# id 转盘池
		self.id = data.get("id",0)
		
		# sys 归属系统
		self.sys = data.get("sys",0)
		
		# idx 归属格子
		self.idx = data.get("idx",0)
		
		# Weight 权重
		self.Weight = data.get("Weight",0)
		
		# reward 奖励
		self.arrayint2tomap("reward", data.get("reward",[]))
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)

# zhuanpanSystem
class ResZhuanpanSystem(object):
	RES_TABLE = "zhuanpanSystem"
	__slots__ = ("id","needs","rewardNeeds","cost","costTen","Ten","idxCanDisable","idxWeight","costReset","free","score",)

	def __init__(self):
		
		# id 转盘分类勿动
		self.id = 0
		
		# needs 抽奖次数要求
		self.needs = []
		
		# rewardNeeds 奖励
		self.rewardNeeds = []
		
		# cost 抽奖1次消费
		self.cost = {}
		
		# costTen 抽奖N次消费
		self.costTen = {}
		
		# Ten 抽奖N次消费次数
		self.Ten = 0
		
		# idxCanDisable 格子是否为不能重复抽取不可省略
		self.idxCanDisable = {}
		
		# idxWeight 格子是权重
		self.idxWeight = []
		
		# costReset 刷新消费
		self.costReset = {}
		
		# free 免费刷新倒计时（秒
		self.free = 0
		
		# score 转1次加几分
		self.score = 0
		

	def load_from_json(self, data):
		
		# id 转盘分类勿动
		self.id = data.get("id",0)
		
		# needs 抽奖次数要求
		self.needs = data.get("needs",[])
		
		# rewardNeeds 奖励
		self.rewardNeeds = data.get("rewardNeeds",[])
		
		# cost 抽奖1次消费
		self.arrayint2tomap("cost", data.get("cost",[]))
		
		# costTen 抽奖N次消费
		self.arrayint2tomap("costTen", data.get("costTen",[]))
		
		# Ten 抽奖N次消费次数
		self.Ten = data.get("Ten",0)
		
		# idxCanDisable 格子是否为不能重复抽取不可省略
		self.arrayint2tomap("idxCanDisable", data.get("idxCanDisable",[]))
		
		# idxWeight 格子是权重
		self.idxWeight = data.get("idxWeight",[])
		
		# costReset 刷新消费
		self.arrayint2tomap("costReset", data.get("costReset",[]))
		
		# free 免费刷新倒计时（秒
		self.free = data.get("free",0)
		
		# score 转1次加几分
		self.score = data.get("score",0)
		
		
	def arrayint2tomap(self, key, arrayint2):
		data = getattr(self, key, {})
		for k, v in arrayint2:
			data[k] = data.get(k,0)+v
		setattr(self, key, data)
	
	def arraystring2tomap(self, key, arraystring2):
		data = getattr(self, key, {})
		for k, v in arraystring2:
			data[k] = v
		setattr(self, key, data)