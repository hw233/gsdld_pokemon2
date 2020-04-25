#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
import datetime

from corelib.gtime import get_days, getZeroTime, cur_day_hour_time

from game.res.resdefine import ResActivity as ResActivityBase
from corelib.frame import Game

class ResActivity(ResActivityBase):

    def isOpen(self, serverInfo):
        now = int(time.time())
        if self.openDayRange:
            openDay = get_days(serverInfo.get("opentime", 0)) + 1
            if openDay < self.openDayRange[0] or  (self.openDayRange[1] != 0 and openDay > self.openDayRange[1]):
                return 0
        elif self.mergeDayRange:
            mergeDay = get_days(serverInfo.get("mergetime", 0))+ 1
            if mergeDay < self.mergeDayRange[0] or  (self.mergeDayRange[1] != 0 and mergeDay > self.mergeDayRange[1]):
                return 0

        if self.everyday:
            startTime, endTime = self.getEverydayTime()
            if now < startTime or now > endTime:
                return 0
        elif self.everyweek:
            startTime, endTime = self.getEveryweekTime()
            if now < startTime or now > endTime:
                return 0
        elif self.dateRange:
            startTime, endTime = self.getDateRangeTime()
            if now < startTime or now > endTime:
                return 0
        return 1

    def isOpenNoServerInfo(self):
        now = int(time.time())

        if self.everyday:
            startTime, endTime = self.getEverydayTime()
            if now < startTime or now > endTime:
                return 0
        elif self.everyweek:
            startTime, endTime = self.getEveryweekTime()
            if now < startTime or now > endTime:
                return 0
        elif self.dateRange:
            startTime, endTime = self.getDateRangeTime()
            if now < startTime or now > endTime:
                return 0
        return 1


    def getCycleEndTime(self, serverInfo=None):
        l=[]
        for v in Game.res_mgr.res_cycle.values():
            if v.activityID==self.id:
                l.append(v)
        
        

        for v in l:
            if v.openDayRange:
                
                openDay = get_days(serverInfo.get("opentime", 0)) + 1

                dd=v.openDayRange[1]
                if v.openDayRange[1]==0:
                    v.openDayRange[1]=3650000
                
                # print("=========",v.openDayRange[0],openDay,v.openDayRange[1])
                
                if v.openDayRange[0]<=openDay<=v.openDayRange[1]:
                    if not dd:
                        return 0

                    xx = v.openDayRange[1]-(openDay-1)
                    zero_day_time = int(cur_day_hour_time(24*xx))

                    return zero_day_time

            if v.mergeDayRange:
                
                mergeDay = get_days(serverInfo.get("mergetime", 0)) + 1

                dd=v.mergeDayRange[1]
                if v.mergeDayRange[1]==0:
                    v.mergeDayRange[1]=3650000
                
                
                if v.mergeDayRange[0]<=mergeDay<=v.mergeDayRange[1]:
                    if not dd:
                        return 0

                    xx = v.mergeDayRange[1]-(mergeDay-1)
                    zero_day_time = int(cur_day_hour_time(24*xx))

                    return zero_day_time
            
            if v.day:
                # TODO
                return 0
            
        
        return 0

    def getCycleFuncID(self, serverInfo=None):
        l=[]
        for v in Game.res_mgr.res_cycle.values():
            if v.activityID==self.id:
                l.append(v)
        
        

        for v in l:
            if v.openDayRange:
                
                openDay = get_days(serverInfo.get("opentime", 0)) + 1

                if v.openDayRange[1]==0:
                    v.openDayRange[1]=3650000
                
                # print("=========",v.openDayRange[0],openDay,v.openDayRange[1])
                
                if v.openDayRange[0]<=openDay<=v.openDayRange[1]:
                    return v.cycleFuncID

            if v.mergeDayRange:
                
                mergeDay = get_days(serverInfo.get("mergetime", 0)) + 1

                if v.mergeDayRange[1]==0:
                    v.mergeDayRange[1]=3650000
                
                
                if v.mergeDayRange[0]<=mergeDay<=v.mergeDayRange[1]:
                    return v.cycleFuncID
            
            if v.day:
                # TODO
                return 0
            
        
        return 0


    def getCycleFuncIDresid(self, serverInfo=None):
        l=[]
        for v in Game.res_mgr.res_cycle.values():
            if v.activityID==self.id:
                l.append(v)
        
        

        for v in l:
            if v.openDayRange:
                
                openDay = get_days(serverInfo.get("opentime", 0)) + 1

                if v.openDayRange[1]==0:
                    v.openDayRange[1]=3650000
                
                # print("=========",v.openDayRange[0],openDay,v.openDayRange[1])
                
                if v.openDayRange[0]<=openDay<=v.openDayRange[1]:
                    return v.id

            if v.mergeDayRange:
                
                mergeDay = get_days(serverInfo.get("mergetime", 0)) + 1

                if v.mergeDayRange[1]==0:
                    v.mergeDayRange[1]=3650000
                
                
                if v.mergeDayRange[0]<=mergeDay<=v.mergeDayRange[1]:
                    return v.id
            
            if v.day:
                # TODO
                return 0
            
        
        return 0


    def getStartTimeAndEndTime(self, serverInfo=None):
        if self.everyday:
            return self.getEverydayTime()
        elif self.everyweek:
            return self.getEveryweekTime()
        elif self.dateRange:
            return self.getDateRangeTime()

        if serverInfo:
            if self.openDayRange:
                opentime = serverInfo.get("opentime", 0)
                startTime = opentime
                if self.openDayRange[1]:
                    endTime = getZeroTime(opentime) + 24*60*60*self.openDayRange[1]
                else:
                    endTime = 0
                return startTime, endTime
            elif self.mergeDayRange:
                mergetime = serverInfo.get("mergetime", 0)
                startTime = mergetime
                if self.mergeDayRange[1]:
                    endTime = getZeroTime(mergetime) + 24 * 60 * 60 * self.mergeDayRange[1]
                else:
                    endTime = 0
                return startTime, endTime

        return 0, 0



    def getEverydayTime(self):
        # 转换成localtime
        time_local = time.localtime(time.time())
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = time.strftime("%Y-%m-%d", time_local)

        curnow = int(time.time())
        rsStartTime = 0
        rsEndTime = 0
        for one in self.everyday:
            startTime = "%s %s:00" % (dt, one[0])
            endTime = "%s %s:00" % (dt, one[1])
            # 转换成时间数组
            startTime = time.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            endTime = time.strptime(endTime, "%Y-%m-%d %H:%M:%S")
            # 转换成时间戳
            startTime = int(time.mktime(startTime))
            endTime = int(time.mktime(endTime))

            #隔天需求 23:00_01:00
            if endTime < startTime:
                endTime += 3600 * 24

            if startTime <= curnow < endTime:
                rsStartTime = startTime
                rsEndTime = endTime
                break

        return rsStartTime, rsEndTime

    def getEveryweekTime(self):
        curnow = int(time.time())
        now = datetime.datetime.now()
        #0代表周日
        #1-6代表周一至周六
        weekday = now.weekday() #0-6是星期一到星期日
        weekday = weekday + 1 #转化成 1-7
        # if weekday == 7: #星期天转化成0
        #     weekday = 0
        rsStartTime = 0
        rsEndTime = 0
        for one in self.everyweek:
            startDay = int(one[0])
            if startDay==0:
                startDay=7
            startTime = one[1]
            endDay = int(one[2])
            if endDay==0:
                endDay=7
            endTime = one[3]
            if startDay <= weekday <= endDay:
                # 转换成localtime
                time_local = time.localtime(time.time())
                # 转换成新的时间格式(2016-05-05 20:28:54)
                dt = time.strftime("%Y-%m-%d", time_local)
                startTime = "%s %s:00" % (dt, startTime)
                endTime = "%s %s:00" % (dt, endTime)
                # 转换成时间数组
                startTime = time.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                endTime = time.strptime(endTime, "%Y-%m-%d %H:%M:%S")
                # 转换成时间戳
                startTime = int(time.mktime(startTime))
                endTime = int(time.mktime(endTime))
                #换算
                startTime -= 3600 * 24 * (weekday - startDay)
                endTime += 3600 * 24 * (endDay - weekday)

                if startTime <= curnow < endTime:
                    rsStartTime = startTime
                    rsEndTime = endTime
                    break

        return rsStartTime, rsEndTime

    def getDateRangeTime(self):
        curnow = int(time.time())
        rsStartTime = 0
        rsEndTime = 0
        for one in self.dateRange:
            #20180814_00:00_20180820_00:00  开始日期_开始时间_结束日期_结束时间
            startDate = one[0]
            startTime = one[1]
            endDate = one[2]
            endTime = one[3]

            startDate = "%s-%s-%s"%(startDate[:4], startDate[4:6], startDate[6:8])
            endDate = "%s-%s-%s" % (endDate[:4], endDate[4:6], endDate[6:8])
            startTime = "%s %s:00" % (startDate, startTime)
            endTime = "%s %s:00" % (endDate, endTime)

            # 转换成时间数组
            startTime = time.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            endTime = time.strptime(endTime, "%Y-%m-%d %H:%M:%S")
            # 转换成时间戳
            startTime = int(time.mktime(startTime))
            endTime =int(time.mktime(endTime))

            if startTime <= curnow < endTime:
                rsStartTime = startTime
                rsEndTime = endTime
                break

        return rsStartTime, rsEndTime






