#!/usr/bin/env python
# -*- coding:utf-8 -*-

from game.common import utility
from game.define import constant, msg_define
from game import Game
import random
import copy
import time

from game.core.cycleData import CycleDay


class PlayerHeti(utility.DirtyFlag):
    def __init__(self, owner):
        utility.DirtyFlag.__init__(self)
        self.owner = owner  # 拥有者
        self.score = 0 #分数
        self.gold = 0 #金币
        self.startTime = 0 #点击开始的时间
        self.HetiNum = 0 #循环合体次数
        self.st = 0 #开始时间
        self.obj = [] #物体
        self.cycleDay = CycleDay(self)

        self.level = 0 #难度
        self.ver = 0 #难度版本
        self.count = 0 #累计开始次数

        self.card=[] #未实例化宠物牌堆
        self.typeApet=[] #剩余A宠实例
        self.typeBpet=[] #剩余B宠实例
        self.typeCpet=[] #剩余C宠实例
        self.nowgroupidx=0 #当前循环组idx
        self.t2v={} #模板对应宠物实例id
        self.returnv=[] #被删宠物 元素：[倒计数,宠物id_阶段]
        self.bigRewardCount=0 #大宝箱计数
        self.smallRewardCount=0 #大宝箱计数
        
        self.histscore = 0 #历史分数
        self.histgold = 0 #历史金币
        self.item={} #本局获得道具
        self.lastrank=0

        self.save_cache = {} #存储缓存
        # self.owner.sub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        if self.owner:
            self.owner.markDirty()

    #存库数据
    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["cycleDay"] = self.cycleDay.to_save_bytes()
            self.save_cache["score"] = self.score
            self.save_cache["gold"] = self.gold
            self.save_cache["histscore"] = self.histscore
            self.save_cache["histgold"] = self.histgold
            self.save_cache["HetiNum"] = self.HetiNum
            self.save_cache["startTime"] = self.startTime
            self.save_cache["st"] = self.st
            self.save_cache["obj"] = self.obj

            self.save_cache["level"] = self.level
            self.save_cache["ver"] = self.ver
            self.save_cache["count"] = self.count
            self.save_cache["card"] = self.card
            self.save_cache["typeApet"] = self.typeApet
            self.save_cache["typeBpet"] = self.typeBpet
            self.save_cache["typeCpet"] = self.typeCpet
            self.save_cache["nowgroupidx"] = self.nowgroupidx
            self.save_cache["t2v"] = self.t2v
            self.save_cache["returnv"] = self.returnv
            self.save_cache["bigRewardCount"] = self.bigRewardCount
            self.save_cache["smallRewardCount"] = self.smallRewardCount
            self.save_cache["item"] = self.item
            self.save_cache["lastrank"] = self.lastrank
        return self.save_cache

    #读库数据初始化
    def load_from_dict(self, data):
        self.cycleDay.load_from_dict(data.get("cycleDay", ""))
        self.score = data.get("score", 0) 
        self.gold = data.get("gold", 0) 
        self.histscore = data.get("histscore", 0) 
        self.histgold = data.get("histgold", 0) 
        self.HetiNum = data.get("HetiNum", 0) 
        self.startTime = data.get("startTime", 0) 
        self.st = data.get("st", 0) 
        self.obj = data.get("obj", [])

        self.level = data.get("level", 0) 
        self.ver = data.get("ver", 0) 
        self.count = data.get("count", 0) 
        self.card = data.get("card", []) 
        self.typeApet = data.get("typeApet", []) 
        self.typeBpet = data.get("typeBpet", []) 
        self.typeCpet = data.get("typeCpet", []) 
        self.nowgroupidx = data.get("nowgroupidx", 0) 
        self.t2v = data.get("t2v", {}) 
        self.returnv = data.get("returnv", []) 
        self.bigRewardCount = data.get("bigRewardCount", 0) 
        self.smallRewardCount = data.get("smallRewardCount", 0) 
        self.item = data.get("item", {}) 
        self.lastrank = data.get("lastrank", 0) 

    #登录初始化下发数据
    def to_init_data(self):
        init_data = {}
        init_data["score"] = self.score
        init_data["gold"] = self.gold
        init_data["st"] = self.st
        init_data["obj"] = self.obj

        nowtime=time.time()

        heticishu = Game.res_mgr.res_common.get("heticishu")
        hetiNumCD = Game.res_mgr.res_common.get("hetiNumCD")

 
        while self.HetiNum and self.startTime and self.startTime+hetiNumCD.i<=nowtime:
            self.HetiNum-=1
            self.startTime+=hetiNumCD.i    

        if self.HetiNum==0:
            self.startTime=0


        init_data["startTime"] = self.startTime
        init_data["num"] = self.HetiNum

        self.markDirty()

        name=""
        # rankobj = Game.sub_rank_mgr.getRankobj(constant.RANK_HETI)
        rankobj=None
        if rankobj:
            rankList = rankobj.GetSnapshot()
            if len(rankList)>=1:
                name = rankList[0]["info"]["name"]


        init_data["name"] = name
        init_data["hetiBuyNum"] = self.GethetiBuyNum()
        
        # init_data["top"] = []

        return init_data

    def buyNum(self):

        self.HetiNum-=1
        self.AddhetiBuyNum()
        self.markDirty()

    def AddHetiNum(self):
        
        x=self.HetiNum

        if x==0:
            self.startTime=time.time()

        self.HetiNum+=1

        self.markDirty()
    
    def GethetiBuyNum(self):
        return self.cycleDay.Query("hetiBuyNum", 0)

    def AddhetiBuyNum(self):
        self.cycleDay.Set("hetiBuyNum", self.GethetiBuyNum()+1)

    def GetHetiTodayScore(self):
        return self.cycleDay.Query("HetiTodayScore", 0)

    def SetHetiTodayScore(self,v):
        self.cycleDay.Set("HetiTodayScore", v)

    def GetHetiTodayGold(self):
        return self.cycleDay.Query("HetiTodayGold", 0)

    def SetHetiTodayGold(self,v):
        self.cycleDay.Set("HetiTodayGold", v)

    def uninit(self):
        pass
        # self.owner.unsub(msg_define.MSG_ROLE_XLV_UPGRADE, self.event_lv_uprade)

    def getPetid(self,t):
        x=getattr(self, "type%spet" % t, None)
        v=x.pop(0)
        self.markDirty()
        return v
    
    def findT(self,t):
        petid = self.t2v.get(t[0]+'_'+t[1],None)
        if not petid:
            petid=self.getPetid(t[0])
            self.t2v[t[0]+'_'+t[1]]=petid
        
        return str(petid)+'-'+t[2]



    def getReturnv(self):
        
        delidx=-1
        returnv_l=len(self.returnv)

        for idx in range(returnv_l):
            self.returnv[idx][0]-=1
            if self.returnv[idx][0]<=0:
                delidx=idx
        
        if delidx!=-1:
            v=self.returnv[delidx][1]
            del self.returnv[delidx]
            return v
        
        return None
        
    def findNext(self,v):
        petid_n=v.split("-")
        petid=int(petid_n[0])
        n=int(petid_n[1])
        
        maxn=0
        if petid in Game.res_mgr.res_typeApet:
            maxn=1
        elif petid in Game.res_mgr.res_typeBpet:
            maxn=2
        elif petid in Game.res_mgr.res_typeCpet:
            maxn=3
        
        if n>=maxn:
            return ''
        
        return str(petid)+'-'+str(n+1)

    def addReward(self,w):
        self.gold+=w.get(constant.CURRENCY_COIN,0)
        for k,v in w.items():
            self.item[str(k)]=self.item.get(str(k),0)+v
        self.markDirty()

    def start(self):
        
        hetiInitCao = Game.res_mgr.res_common.get("hetiInitCao")
        hetiLevel2Count = Game.res_mgr.res_common.get("hetiLevel2Count")
        hetiLevel3Count = Game.res_mgr.res_common.get("hetiLevel3Count")


        if self.count>=hetiLevel3Count.i:
            self.level=3
        elif self.count>=hetiLevel2Count.i:
            self.level=2
        else:
            self.level=1

        vernum=len(Game.res_mgr.res_hetiMakeDict[self.level])
        self.ver=random.randint(1,vernum)
        self.nowgroupidx=len(Game.res_mgr.res_hetiMakeDict[self.level][self.ver])-1 #最后一个

        self.st = time.time() #开始时间
        self.obj=["*-*"]*hetiInitCao.i

        self.typeApet=copy.deepcopy(Game.res_mgr.res_typeApet)
        self.typeBpet=copy.deepcopy(Game.res_mgr.res_typeBpet)
        self.typeCpet=copy.deepcopy(Game.res_mgr.res_typeCpet)
        random.shuffle(self.typeApet)
        random.shuffle(self.typeBpet)
        random.shuffle(self.typeCpet)

        self.score = 0 #分数
        self.gold = 0 #金币
        self.t2v={} #模板对应宠物实例id
        self.card=[] #空
        self.returnv=[] #被删宠物
        self.item={}

    
        self.count+=1
        self.AddHetiNum()

        
   
        self.markDirty()

    # 返回宝箱id,加分
    def caoPre(self):
        hetiPet = Game.res_mgr.res_common.get("hetiPet")
        hetibigchest = Game.res_mgr.res_common.get("hetibigchest")
        hetismallchest = Game.res_mgr.res_common.get("hetismallchest")

        r=[]
        r.append([0,hetiPet.i])

        if self.bigRewardCount<hetibigchest.arrayint1[0]:
            r.append([1,hetibigchest.arrayint1[1]])
        
        if self.smallRewardCount<hetismallchest.arrayint1[0]:
            r.append([2,hetismallchest.arrayint1[1]])
        

        
        boxtype=utility.Choice(r)

        if boxtype==0:
            return 0,0,boxtype

        rid=0
        s=0
        
        if boxtype==1:
            self.bigRewardCount+=1
            rid,s = hetibigchest.arrayint1[2],hetibigchest.arrayint1[3]
        elif boxtype==2:
            self.smallRewardCount+=1           
            rid,s = hetismallchest.arrayint1[2],hetismallchest.arrayint1[3]

        self.score+=s
        self.markDirty()
        return rid,s,boxtype
        


    # 返回 ""
    def cao(self):


        self.obj.remove("*-*")

        v=self.getReturnv()

        if not v:
            if len(self.card)==0:
                self.nowgroupidx+=1
                if self.nowgroupidx>=len(Game.res_mgr.res_hetiMakeDict[self.level][self.ver]):
                    self.nowgroupidx=0
                
                self.card=copy.deepcopy(Game.res_mgr.res_hetiMakeDict[self.level][self.ver][self.nowgroupidx])
                random.shuffle(self.card)

            t=self.card.pop(0)
            
            v=self.findT(t)
        
        self.obj.append(v)
        
        # print(self.obj)

        self.markDirty()

        return v




    # 返回 [],加分
    def hebing(self,v):
        
        self.obj.remove(v)
        self.obj.remove(v)

        hetihebingScore = Game.res_mgr.res_common.get("hetihebingScore")
        

        petid_n=v.split("-")
        n=int(petid_n[1])
        
        addscore=hetihebingScore.arrayint1[n-1]
        self.score+=addscore

        newv = self.findNext(v)

        retval=[]
        if newv:
            self.obj.append(newv)
            retval.append(newv)

        hetiFillCao = Game.res_mgr.res_common.get("hetiFillCao")

        if self.obj.count("*-*")<hetiFillCao.i:
            if newv:
                self.obj.append("*-*")
                retval.append("*-*")
            else:
                self.obj.append("*-*")
                self.obj.append("*-*")
                retval.append("*-*")
                retval.append("*-*")
        else:
            if newv:
                r=random.randint(0,1)
                if r:
                    self.obj.append("*-*")
                    retval.append("*-*")
            else:
                r=random.randint(1,2)
                if r==1:
                    self.obj.append("*-*")
                    retval.append("*-*")
                else:
                    self.obj.append("*-*")
                    self.obj.append("*-*")
                    retval.append("*-*")
                    retval.append("*-*")
        
        # print(self.obj)

        return retval,addscore

    def delv(self,v):

        self.obj.remove(v)
        self.obj.append("*-*")

        hetidel = Game.res_mgr.res_common.get("hetidel")
        hetiReturn = Game.res_mgr.res_common.get("hetiReturn")
        step=random.randint(hetiReturn.arrayint1[0],hetiReturn.arrayint1[1])

        self.returnv.append([step,v])
        
        hetideli=hetidel.i
        if self.score<hetideli:
            hetideli=self.score
        
        self.score-=hetideli


        self.markDirty()
        return hetideli

    def donetest(self):
        # rankobj = Game.sub_rank_mgr.getRankobj(constant.RANK_HETI)
        rankobj=None
        if rankobj:
            rankList = rankobj.GetSnapshot()
            if len(rankList)>=1:
                print(rankList[0])

    def done(self):
        self.st=0




        if self.histscore<self.score:
            self.histscore=self.score

        if self.histgold<self.gold:
            self.histgold=self.gold


        needupd=0
        if self.GetHetiTodayScore()<self.score:
            self.SetHetiTodayScore(self.score)
            needupd=1


        if self.GetHetiTodayGold()<self.gold:
            self.SetHetiTodayGold(self.gold)
            needupd=1
            

        if needupd:
            self.owner.rank.uploadRank(constant.RANK_HETI)

        orank=self.lastrank

        # rankobj = Game.sub_rank_mgr.getRankobj(constant.RANK_HETI)
        rankobj=None
        if rankobj:
            # rankList = rankobj.getRankList()
            myRank = rankobj.getMyRank(self.owner.id)
            if myRank:
                self.lastrank=myRank

        
        nrank=self.lastrank
        if orank==0:
            orank=nrank

        self.markDirty()

        self.owner.safe_pub(msg_define.MSG_MINI_GAME_UP_TO_STD, self.score)

        return orank,nrank