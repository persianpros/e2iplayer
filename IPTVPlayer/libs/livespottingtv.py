#!/usr/bin/python
# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.components.ihost import CBaseHostClass
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
###################################################

###################################################
# Config options for HOST
###################################################
def GetConfigList():
    optionList = []
    return optionList
###################################################

class LivespottingTvApi:
    MAIN_URL = 'http://livespotting.tv/'

    def __init__(self):
        self.COOKIE_FILE = GetCookieDir('livespottingtv.cookie')
        self.cm = common()
        self.up = urlparser()
        self.http_params = {}
        self.http_params.update({'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIE_FILE})
        self.cache = {}
        
    def cleanHtmlStr(self, str):
        return CBaseHostClass.cleanHtmlStr(str)
        
    def getChannelsList(self, cItem):
        printDBG("WkylinewebcamsCom.getChannelsList")
        list = []
        sts, data = self.cm.getPage('http://livespotting.tv/api/api.json')
        if not sts: return list
        try:
            data = json_loads(data)
            for item in data['streams']:
                if 'stream' not in item: continue
                try:
                    item = item['stream']['data']
                    title = item['content']['title']
                    icon  = item['images'].get('snapshot-343x192', '')
                    desc  = self.cleanHtmlStr(item['content'].get('longtext', ''))
                    camId = item['camID']['camid']
                    if camId.startswith('LS_'): camId = camId[3:]
                    url   =  'rtmp://stream.livespotting.tv/windit-edge/%s.stream live=1' % camId
                    list.append({'title':title, 'url':url, 'icon':icon, 'desc':desc})
                except Exception: printExc()
        except Exception:
            printExc()

        return list
