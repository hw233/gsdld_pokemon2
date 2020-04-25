#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game import Game
from corelib.frame import MSG_FRAME_STOP
from game.define import constant
from game.models.mail import ModelMail, ModelPublicMail
from collections import OrderedDict
from time import time
from corelib import log, spawn
from gevent import sleep, event
from game.common import utility


class MailMgr(utility.DirtyFlag):
    _rpc_name_ = "rpc_mail_mgr"
    TIME_OUT = 0.1
    DATA_CLS = ModelPublicMail

    def __init__(self):
        utility.DirtyFlag.__init__(self)

        self.playerMail = {}               # pid:MailBox
        self.publicMail = OrderedDict()    # 公共邮件 pmid: Mail
        self.maxPmid = 0

        self.data = None
        self._save_loop_task = None
        self.save_cache = {}

        Game.sub(MSG_FRAME_STOP, self._frame_stop)

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def hasUnread(self, pid):
        self.getNewPublicMail(pid)
        mailBox = self.getPlayerMail(pid)
        return mailBox.hasUnread()

    def getMailList(self, pid):
        self.getNewPublicMail(pid)
        mailBox = self.getPlayerMail(pid)
        return mailBox.getMailList()

    def getPlayerMail(self, pid):
        if pid not in self.playerMail:
            mailBox = MailBox(pid)
            self.playerMail[pid] = mailBox
            new = mailBox.load()
            # 新玩家从当前最大邮件id开始
            if new:
                mailBox.setMaxPmid(self.maxPmid)

            mailBox.loaded = True
            mailBox.waiter.set()
            return mailBox
        else:
            mailBox = self.playerMail.get(pid, None)
            if mailBox and not mailBox.loaded:
                mailBox.waiter.wait()
            return mailBox

    def getOneMail(self, pid, mid, pack=True):
        self.getNewPublicMail(pid)
        mailBox = self.getPlayerMail(pid)
        mailBox.read(mid)
        return mailBox.getOneMail(mid, pack=pack)

    def sendPersonMail(self, pid, title, content, attachment, show=False, push=True):
        self.getNewPublicMail(pid, push=push)
        mailBox = self.getPlayerMail(pid)
        mailBox.new(title, content, attachment, int(time()), show=show, push=push)

    def sendPersonMails(self, pid, title, content, attachment, show=False, push=True, num=1):
        for i in range(num):
            self.sendPersonMail(pid, title, content, attachment, show=show, push=push)

    def sendPublicMail(self, title, content, attachment, show=False):
        self.maxPmid += 1
        mail = Mail(self.maxPmid, title, content, attachment, int(time()), show=show)
        self.publicMail[self.maxPmid] = mail
        if show:
            pids = Game.rpc_player_mgr.get_online_ids()
            for pid in pids:
                self.getNewPublicMail(pid)

        self.markDirty()

    def readMail(self, pid, mid):
        mailBox = self.getPlayerMail(pid)
        mailBox.read(mid)

    def takeAttachment(self, pid, mid):
        mailBox = self.getPlayerMail(pid)
        mailBox.takeAttachment(mid)

    def getNewPublicMail(self, pid, push=True):
        mailBox = self.getPlayerMail(pid)
        for x in range(mailBox.maxPmid+1, self.maxPmid+1):
            pMail = self.publicMail.get(x, None)
            if pMail:
                mailBox.new(pMail.title, pMail.content, pMail.attachment, pMail.addTime, show=pMail.show, push=push)
                mailBox.setMaxPmid(x)

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["maxPmid"] = self.maxPmid
            self.save_cache["public_mail"] = []
            for mail in self.publicMail.values():
                self.save_cache["public_mail"].append(mail.to_save_dict())
        return self.save_cache

    def load_from_dict(self, data):
        self.maxPmid = data.get("maxPmid", 0)
        public_mail = data.get("public_mail", [])
        for mailData in public_mail:
            pmid = mailData.get("mid", 0)
            if pmid > 0:
                title = mailData.get("title", "")
                content = mailData.get("content", "")
                addTime = mailData.get("addTime", 0)
                attachment = {}
                attachmentData = mailData.get("attachment", [])
                for item in attachmentData:
                    k = item.get("id", 0)
                    v = item.get("num", 0)
                    if k > 0 and v > 0:
                        attachment[k] = v

                mail = Mail(pmid, title, content, attachment, addTime)
                self.publicMail[pmid] = mail

    def start(self):
        self.data = self.DATA_CLS.load(Game.store, self.DATA_CLS.TABLE_KEY)
        if not self.data:
            self.data = self.DATA_CLS()
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.set_owner(self)

        self._save_loop_task = spawn(self._saveLoop)

    def _frame_stop(self):
        if self._save_loop_task:
            self._save_loop_task.kill(block=False)
            self._save_loop_task = None

        self.save(forced=True, no_let=True)

    def _saveLoop(self):
        stime = 30 * 60
        while True:
            sleep(stime)
            try:
                self.save()
            except:
                log.log_except()

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

        keys = list(self.playerMail.keys())
        for pid in keys:
            mailbox = self.playerMail.get(pid)
            if mailbox:
                mailbox.save(forced=forced, no_let=no_let)

                if int(time()) - mailbox.getActiveTime() > 3 * 3600:
                    self.playerMail.pop(pid, None)

                if forced and no_let:
                    pass
                else:
                    sleep()


class MailBox(utility.DirtyFlag):
    DATA_CLS = ModelMail

    def __init__(self, pid):
        utility.DirtyFlag.__init__(self)

        self.pid = pid                # 玩家id
        self.maxMid = 0               # 邮件最大id(自增)
        self.maxPmid = 0              # 已添加最大公众邮件id
        self.inbox = OrderedDict()    # mid:Mail

        self.data = None
        self.save_cache = {}
        self.loaded = False
        self.waiter = event.Event()

        self.lastActiveTime = int(time())

    def markActive(self):
        self.lastActiveTime = int(time())

    def getActiveTime(self):
        return self.lastActiveTime

    def markDirty(self):
        utility.DirtyFlag.markDirty(self)
        self.data.modify()

    def to_save_dict(self, forced=False):
        if self.isDirty() or forced or not self.save_cache:
            self.save_cache = {}
            self.save_cache["maxMid"] = self.maxMid
            self.save_cache["maxPmid"] = self.maxPmid
            self.save_cache["inbox"] = []
            for mail in self.inbox.values():
                self.save_cache["inbox"].append(mail.to_save_dict())
        return self.save_cache

    def load_from_dict(self, data):
        self.maxMid = data.get("maxMid", 0)
        self.maxPmid = data.get("maxPmid", 0)
        inbox = data.get("inbox", [])
        for mailData in inbox:
            mid = mailData.get("mid", 0)
            if mid > 0:
                title = mailData.get("title", "")
                content = mailData.get("content", "")
                status = mailData.get("status", 0)
                addTime = mailData.get("addTime", 0)
                show = mailData.get("show", 0)
                attachment = {}
                attachmentData = mailData.get("attachment", [])
                for item in attachmentData:
                    k = item.get("id", 0)
                    v = item.get("num", 0)
                    if k > 0 and v > 0:
                        attachment[k] = v

                mail = Mail(mid, title, content, attachment, addTime, show=show, status=status)
                self.inbox[mid] = mail

                # 合服适配处理
                if len(self.inbox) > constant.MAX_MAIL:
                    self.inbox.popitem(last=False)

    def save(self, forced=False, no_let=False):
        self.data.save(Game.store, forced=forced, no_let=no_let)

    def load(self):
        self.data = self.DATA_CLS.load(Game.store, self.pid)
        new = False
        if not self.data:
            self.data = self.DATA_CLS()
            new = True
        else:
            self.load_from_dict(self.data.dataDict)

        self.data.setOwner(self)
        return new

    def hasUnread(self):
        for mail in self.inbox.values():
            if mail.hasUnread():
                return True
        return False

    def getMailList(self):
        mailList = []
        for mail in self.inbox.values():
            mailList.append(mail.getBriefInfo())
        self.markActive()
        return mailList

    def getOneMail(self, mid, pack=True):
        self.markActive()
        mail = self.inbox.get(mid, None)
        if mail:
            return mail.getDetailInfo(pack=pack)

    def new(self, title, content, attachment, addTime, show=False, push=True):
        self.maxMid += 1
        mail = Mail(self.maxMid, title, content, attachment, addTime, show=show)
        self.inbox[self.maxMid] = mail

        if len(self.inbox) > constant.MAX_MAIL:
            self.inbox.popitem(last=False)

        if push:
            from game.mgr.player import get_rpc_player
            player = get_rpc_player(self.pid, offline=True)
            if player:
                player.sendMail(mail.getBriefInfo())


        Game.glog.log2File("newMail", "%s|%s|%s|%s|%s|%s" % (self.pid, self.maxMid, title, content, attachment, addTime))
        self.markDirty()
        self.markActive()

    def setMaxPmid(self, pmid):
        self.maxPmid = pmid
        self.markDirty()
        self.markActive()

    def read(self, mid):
        mail = self.inbox.get(mid, None)
        if mail:
            mail.read()
        self.markDirty()
        self.markActive()

    def takeAttachment(self, mid):
        mail = self.inbox.get(mid, None)
        if mail:
            mail.takeAttachment()
        self.markDirty()
        self.markActive()


class Mail(object):
    def __init__(self, mid, title, content, attachment, addTime, show=False, status=constant.MAIL_STATUS_1):
        self.mid = mid                  # mid
        self.title = title              # 标题
        self.content = content          # 内容
        self.attachment = attachment    # 附件
        self.status = status            # 0未读 1已读未领取附件 2已读已领取附件
        self.addTime = addTime          # 收件时间
        self.show = show                # 是否弹出提示


    def hasUnread(self):
        if self.attachment:
            if self.status < constant.MAIL_STATUS_3:
                return True
        else:
            if self.status < constant.MAIL_STATUS_2:
                return True

    def getBriefInfo(self):
        brief = {}
        brief["mid"] = self.mid
        brief["title"] = self.title
        brief["status"] = self.status
        brief["addTime"] = self.addTime
        brief["show"] = self.show
        brief["hasAttachment"] = 0
        if self.attachment:
            brief["hasAttachment"] = 1

        return brief

    def getDetailInfo(self, pack=True):
        detail = {}
        detail["mid"] = self.mid
        detail["status"] = self.status
        detail["content"] = self.content
        if pack:
            detail["attachment"] = []
            for k, v in self.attachment.items():
                detail["attachment"].append({"id": k, "num": v})
        else:
            detail["attachment"] = self.attachment

        return detail

    def to_save_dict(self):
        save = {}
        save["mid"] = self.mid
        save["title"] = self.title
        save["content"] = self.content
        save["status"] = self.status
        save["addTime"] = self.addTime
        save["show"] = self.show
        save["attachment"] = []
        for k, v in self.attachment.items():
            save["attachment"].append({"id": k, "num": v})

        return save

    def read(self):
        if self.status < constant.MAIL_STATUS_2:
            self.status = constant.MAIL_STATUS_2

    def takeAttachment(self):
        if self.status < constant.MAIL_STATUS_3:
            self.status = constant.MAIL_STATUS_3

