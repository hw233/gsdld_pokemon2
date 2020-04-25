#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from game.res.resdefine import ResCommon as ResCommonBase

class ResCommon(ResCommonBase):

    def load_from_json(self, data):
        self.key = data.get("key", '')
        self.i = data.get("i", 0)
        self.s = data.get("s", '')
        self.arrayint1 = data.get("arrayint1", [])

        arraystring2 = data.get("arraystring2", [])  # hp_101;mp_301 = [['hp','101'],['mp','301']]
        for one in arraystring2:
            key = one[0]
            value = one[1]
            self.arraystring2[key] = value

        arrayint2 = data.get("arrayint2", [])  # 1_101;2_301 = [[1,101],[2,301]]
        if self.key in ("yishouzhilingBuyBagSizeCost", "LevelContestChallengeCost",
                        'minggeBuyBagSizeCost', 'groupPKBuyCost', "ActivityChargeStarLucky", "mapQuickCost", "mapQuickCostCharge"):
            self.arrayint2 = arrayint2
        else:
            self.arrayint2={}
            for one in arrayint2:
                if not one:
                    continue
                key = one[0]
                value = one[1:]
                if len(value) == 1:
                    value = int(value[0])
                self.arrayint2[key] = value