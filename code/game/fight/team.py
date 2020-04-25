#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import uuid

from corelib.frame import Game
from game.define import constant

from game.core.attributeContainer import AttributeContainerBase
from game.fight.fighter import PetFighter, MonsterFighter

class TeamAttribute(AttributeContainerBase):
    pass

class FightPlayerWave(object):
    def __init__(self, fightIns, teamIns, waveData):
        self.uid = fightIns.iterFightInsUid("wave")
        self.fightIns = fightIns
        self.teamIns = teamIns

        self.fa = 0
        self.init(waveData)

    def init(self, waveData):
        # 宠物
        self.position = {}
        for pos, pet_data in waveData.items():
            petobj = PetFighter(self.fightIns, self.teamIns, self, int(pos), pet_data)
            self.position[int(pos)] = petobj
            self.fa += petobj.attr.fa

    def isAllDead(self):
        isAllDead = 1
        for obj in self.position.values():
            if not obj.status.is_dead:
                isAllDead = 0
                break
        return isAllDead

    def to_client(self):
        objs = []
        for pos, obj in self.position.items():
            one = {}
            one["fid"] = obj.uid
            one["pos"] = pos
            one["tp"] = obj.FIGHTER_TYPE
            one["attr"] = obj.attr.to_client()

            one["d"] = {}
            one["d"]["petID"] = obj.resID
            one["d"]["lv"] = obj.lv
            one["d"]["evLv"] = obj.evLv
            one["d"]["r1"] = obj.relationship1
            one["d"]["r2"] = obj.relationship2
            one["d"]["r3"] = obj.relationship3
            one["d"]["r4"] = obj.relationship4

            objs.append(one)
        return objs

    def getAll(self):
        return list(self.position.values())

class FightPlayerTeam(object):
    def __init__(self, fightIns, flag, fightdata):
        self.uid = fightIns.iterFightInsUid("team")
        self.fightIns = fightIns

        self.flag = flag # 1=红方 2=蓝方
        self.init(fightdata)


    def init(self, fightdata):
        self.pid = fightdata.get("pid", 0)
        self.fa = fightdata.get("fa", 0)
        self.name = fightdata.get("name", "")
        self.sex = fightdata.get("sex", 0)
        self.vipLv = fightdata.get("vipLv", 0)
        self.lv = fightdata.get("lv", 0)
        self.portrait = fightdata.get("portrait", 0)
        self.headframe = fightdata.get("headframe", 0)
        self.title = fightdata.get("title", 0)
        #各类容器池子
        # self.attr = {}
        # attr = fightdata.get("attr", {})
        # for containerType, packageList in attr.items():
        #     oneAttr = {}
        #     for index, name in enumerate(constant.ALL_ATTR):
        #         oneAttr[name] = packageList[index]
        #     self.attr[containerType] = TeamAttribute(self, oneAttr)

        # 多队宠物
        self.waves = {}
        waves = fightdata.get("pet", [])
        for index, waveData in enumerate(waves):
            wave = FightPlayerWave(self.fightIns, self, waveData)
            self.waves[index+1] = wave


    def to_client(self):
        resp = {}
        resp["pid"] = self.pid
        resp["campID"] = self.flag
        resp["info"] = self.pack_info()

        resp["waves"] = []
        for index, wave in self.waves.items():
            one = {}
            objs = wave.to_client()
            one["index"] = index
            one["tid"] = wave.uid
            one["fa"] = wave.fa
            one["objs"] = objs
            resp["waves"].append(one)
        return resp

    def pack_info(self):
        info = {}
        info["tp"] = 1
        info["d"] = {}
        info["d"]["name"] = self.name
        info["d"]["fa"] = self.fa
        info["d"]["lv"] = self.lv
        info["d"]["title"] = self.title
        info["d"]["sex"] = self.sex
        info["d"]["portrait"] = self.portrait
        info["d"]["headframe"] = self.headframe
        info["d"]["vipLv"] = self.vipLv
        return info


class FightMonsterWave(object):
    def __init__(self, fightIns, teamIns, waveData):
        self.uid = fightIns.iterFightInsUid("wave")
        self.fightIns = fightIns
        self.teamIns = teamIns
        self.fa = 0

        self.init(waveData)

    def init(self, waveData):
        self.position = {}

        position = waveData.get("position", {})
        relation = waveData.get("relation", {})

        # 计算 连协 队伍加成 羁绊
        for pos, monster_id in position.items():
            mstRes = Game.res_mgr.res_monster.get(monster_id)
            mstobj = MonsterFighter(self.fightIns, self.teamIns, self, int(pos), mstRes, relation)
            self.position[int(pos)] = mstobj
            self.fa += mstobj.attr.fa


    def isAllDead(self):
        isAllDead = 1
        for obj in self.position.values():
            if not obj.status.is_dead:
                isAllDead = 0
                break
        return isAllDead

    def to_client(self):
        objs = []
        for pos, obj in self.position.items():
            one = {}
            one["fid"] = obj.uid
            one["pos"] = pos
            one["tp"] = obj.FIGHTER_TYPE
            one["attr"] = obj.attr.to_client()

            one["d"] = {}
            one["d"]["mstID"] = obj.resID
            one["d"]["r1"] = obj.relationship1
            one["d"]["r2"] = obj.relationship2
            one["d"]["r3"] = obj.relationship3

            objs.append(one)
        return objs

    def getAll(self):
        return list(self.position.values())

class FightMonsterTeam(object):
    def __init__(self, fightIns, flag, fightdata):
        self.fightIns = fightIns

        self.flag = flag # 1=红方 2=蓝方
        self.init(fightdata)


    def init(self, fightdata):
        self.pid = 0 #系统默认 0
        # 多队
        self.waves = {}
        for index, waveData in fightdata.items():
            wave = FightMonsterWave(self.fightIns, self, waveData)
            self.waves[index] = wave

    def to_client(self):
        resp = {}
        resp["pid"] = self.pid
        resp["campID"] = self.flag
        resp["info"] = self.pack_info()

        resp["waves"] = []
        for index, wave in self.waves.items():
            one = {}
            objs = wave.to_client()
            one["index"] = index
            one["tid"] = wave.uid
            one["fa"] = wave.fa
            one["objs"] = objs
            resp["waves"].append(one)
        return resp

    def pack_info(self):
        info = {}
        info["tp"] = 2
        info["d"] = {}
        return info



