#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from game.define import errcode, constant
from game import Game
from game.common import utility


class MailMixin(object):
    if 0:
        from game.core import player as player_md
        player = player_md.Player()


    # 请求邮件列表(getMailList)
    #     请求
    #     返回
    #         邮件列表(mailList, [json])
    #             邮件id(mid, int)
    #             标题(title, string)
    #             时间戳(addTime, int)
    #             状态(status, int)
    #                 0=未读未领取 1=已读未领取 2=已读已领取
    def rc_getMailList(self):
        mailList = Game.rpc_mail_mgr.getMailList(self.player.id)

        resp = {
            "mailList": mailList,
        }

        return 1, resp

    # 请求邮件详情(getOneMail)
    #     请求
    #         邮件id(mid, int)
    #     返回
    #         邮件id(mid, int)
    #         内容(content, string)
    #         附件列表(attachment, [json])
    #             道具或装备配置表id(id, int)
    #             数量(num, int)
    def rc_getOneMail(self, mid):
        detailInfo = Game.rpc_mail_mgr.getOneMail(self.player.id, mid)

        resp = detailInfo

        return 1, resp

    # 领取附件(getMailItem)
    #     请求
    #         邮件id(mid, int)
    #     返回
    #         邮件id(mid, int)
    #         状态(status, int)
    #             0=未读未领取 1=已读未领取 2=已读已领取
    #         主动推送刷新(allUpdate, json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    def rc_getMailItem(self, mid):
        detailInfo = Game.rpc_mail_mgr.getOneMail(self.player.id, mid, pack=False)
        status = detailInfo.get("status", 0)
        if status == constant.MAIL_STATUS_3:
            return 0, errcode.EC_MAIL_ALERAY_GET_ATTACHMENT

        attachment = detailInfo.get("attachment", {})
        respBag = self.player.bag.add(attachment, constant.ITEM_ADD_MAIL_ATTACHMENT, wLog=True)

        Game.rpc_mail_mgr.takeAttachment(self.player.id, mid)

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "mid": mid,
            "allUpdate": dUpdate,
        }
        return 1, resp

    # 一键领取附件(OneKeyGetMailItem)
    #     请求
    #     返回
    #         主动推送刷新(allUpdate, json)
    #             游戏模型-货币
    #             游戏模型-角色背包
    def rc_OneKeyGetMailItem(self):
        mailList = Game.rpc_mail_mgr.getMailList(self.player.id)

        reward = {}

        # freeSize = self.player.bag.getFreeSize()

        untake = []

        for mail in mailList:
            mid = mail.get("mid", 0)
            hasAttachment = mail.get("hasAttachment", 0)
            status = mail.get("status", 0)
            if hasAttachment and status != constant.MAIL_STATUS_3:
                detailInfo = Game.rpc_mail_mgr.getOneMail(self.player.id, mid, pack=False)
                attachment = detailInfo.get("attachment", {})

                # equipCount = 0
                # for k, v in attachment.items():
                #     if k >= constant.EQUIP_START_NO:
                #         equipCount += v

                # if freeSize >= equipCount:
                # freeSize -= equipCount

                for k, v in attachment.items():
                    if k in reward:
                        reward[k] = reward[k] + v
                    else:
                        reward[k] = v

                Game.rpc_mail_mgr.takeAttachment(self.player.id, mid)
                # else:
                #     Game.rpc_mail_mgr.readMail(self.player.id, mid)
                #     untake.append(mid)
            else:
                Game.rpc_mail_mgr.readMail(self.player.id, mid)

        respBag = self.player.bag.add(reward, constant.ITEM_ADD_MAIL_ATTACHMENT, wLog=True, )

        dRole = {}
        dRole["roleBase"] = self.player.base.to_init_data()

        dUpdate = self.player.packRespBag(respBag)
        dUpdate["role"] = dRole
        resp = {
            "untake": untake,
            "allUpdate": dUpdate,
        }
        return 1, resp