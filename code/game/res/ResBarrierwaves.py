import random
import copy

from game import Game
from game.common import utility
from game.define import constant
from game.res.resdefine import ResBarrierwaves as ResBarrierwavesBase

class ResBarrierwaves(ResBarrierwavesBase):

    def getRelation(self):
        cache = getattr(self, "cache", {})
        if cache:
            return cache

        #数据统计
        allPetID = {}
        allEle = {}
        allJob = {}
        allRelation = {}
        for pos in constant.ALL_BATTLE_POS:
            monster_id = getattr(self, "pos%s"%pos, 0)
            if not monster_id:
                continue
            mstRes = Game.res_mgr.res_monster.get(monster_id)
            if not mstRes:
                continue
            petRes = Game.res_mgr.res_pet.get(mstRes.petID)
            if not petRes:
                continue
            # 元素
            allEle[petRes.eleType] = allEle.get(petRes.eleType, 0) + 1
            # 职业
            allJob[petRes.job] = allJob.get(petRes.job, 0) + 1
            # 其他
            for t in petRes.relation:
                allRelation[t] = allRelation.get(t, 0) + 1

            allPetID[mstRes.petID] = allPetID.get(mstRes.petID, 0) + 1

        #连协
        relationship1 = {}
        for obj in Game.res_mgr.res_petrelationship1.values():
            isAdd = 1
            for petID in obj.limit:
                if not allPetID.get(petID):
                    isAdd = 0
                    break
            if isAdd:
                for petID in obj.limit:
                    data = set(relationship1.setdefault(petID, []))
                    data.add(obj.id)
                    relationship1[petID] = list(data)

        #队伍加成
        relationship2 = {}
        _tmp = {}
        for obj in Game.res_mgr.res_petrelationship2.values():
            isAdd = 1
            for k, v in obj.limit1.items():
                if allEle.get(k, 0) < v:
                    isAdd = 0
                    break
            for k, v in obj.limit2.items():
                if allJob.get(k, 0) < v:
                    isAdd = 0
                    break
            for k, v in obj.limit3.items():
                if allRelation.get(k, 0) < v:
                    isAdd = 0
                    break
            if isAdd:
                curRes = _tmp.setdefault(obj.group)
                if curRes:
                    #同组只取最高的
                    if obj.lv > curRes.lv:
                        _tmp[obj.group] = obj
                else:
                    _tmp[obj.group] = obj
        # 差异比较 删除旧的，增加新的
        for petID in allPetID.keys():
            data = set(relationship2.setdefault(petID, []))
            res = Game.res_mgr.res_pet.get(petID)
            for obj in _tmp.values():
                if obj.addall:
                    data.add(obj.id)
                else:
                    if res.eleType in obj.addele:
                        data.add(obj.id)
                    if res.job in obj.addjob:
                        data.add(obj.id)
                    for oneType in res.relation:
                        if oneType in obj.addrelation:
                            data.add(obj.id)
            relationship2[petID] = list(data)

        #羁绊 组合存在多个情况
        relationship3 = {}
        for obj in Game.res_mgr.res_petrelationship3.values():
            isAdd = 1
            for petID in obj.limit:
                if not allPetID.get(petID):
                    isAdd = 0
                    break
            if isAdd:
                for petID in obj.limit:
                    data = set(relationship3.setdefault(petID, []))
                    data.add(obj.id)
                    relationship3[petID] = list(data)

        cache["r1"] = relationship1
        cache["r2"] = relationship2
        cache["r3"] = relationship3
        self.cache = cache
        return self.cache