# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts, rm, GetCookieDir, ReadTextFile, WriteTextFile
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
###################################################

###################################################
# FOREIGN import
###################################################
from binascii import hexlify
from hashlib import md5
import urllib
from datetime import datetime
from Components.config import config, ConfigText, getConfigListEntry
###################################################

###################################################
# E2 GUI COMMPONENTS 
###################################################
from Screens.MessageBox import MessageBox
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.dixmax_login     = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.dixmax_password  = ConfigText(default = "", fixed_size = False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_("login"), config.plugins.iptvplayer.dixmax_login))
    optionList.append(getConfigListEntry(_("password"), config.plugins.iptvplayer.dixmax_password))
    return optionList
###################################################

def gettytul():
    return 'http://turcjatv.pl'

class TurcjaTv(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'turcjatv.pl', 'cookie':'turcjatv.pl.cookie'})

        self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
        self.defaultParams = {'header':self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}

        self.MAIN_URL = 'http://turcjatv.pl/'
        self.DEFAULT_ICON_URL = self.getFullIconUrl('/wp-content/uploads/2017/05/0e0nwZk.png')

    def getPage(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}: addParams = dict(self.defaultParams)
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listMain(self, cItem):
        printDBG("TurcjaTv.listMain")
        sts, data = self.getPage(self.getMainUrl())
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])

        subItems = []
        tmp = ph.find(data, ('<ul', '>', 'menu-depth'), '</ul>', flags=0)[1]
        tmp = ph.findall(tmp, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(tmp), 2):
            url = ph.getattr(tmp[idx-1], 'href')
            title = self.cleanHtmlStr(tmp[idx])
            subItems.append( MergeDicts(cItem, {'good_for_fav':True, 'category':'list_items', 'title':title, 'url':url}) )

        MAIN_CAT_TAB = [{'category':'sub_items',      'title': 'SERIALE ABC',   'url':self.getMainUrl(), 'sub_items':subItems},
                        {'category':'list_items',     'title': 'SERIALE',       'url':self.getMainUrl()},
                        {'category':'list_items',     'title': 'FILMY',         'url':self.getFullUrl('channel/filmy/')},
                        {'category':'search',         'title': _('Search'),       'search_item':True       },
                        {'category':'search_history', 'title': _('Search history'),                        }]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listSubItems(self, cItem):
        printDBG("TurcjaTv.listSubItems")
        self.currList = cItem['sub_items']

    def listItems(self, cItem):
        printDBG("TurcjaTv.listItems")
        page = cItem.get('page', 0)
        post_data = cItem.get('post_data', None)
        nextPage = cItem['url']
        if page == 0:
            sts, data = self.getPage(cItem['url'])
            if not sts: return
            self.setMainUrl(self.cm.meta['url'])

            tmp = ph.find(data, ('<div', '>', 'entry-content'), '<footer')[1].split('page-navigation', 1)
            if len(tmp) == 2:
                template = ph.getattr(tmp[-1], 'data-template')
                playlist = ph.getattr(tmp[-1], 'id_post_playlist')

                np = ph.search(data.split('<body', 1)[-1], 'var\s+?cactus_ajax_paging\s*?=\s*?(\{[^>]+\})')[0]
                printDBG(">> \n%s" % np)
                try:
                    np = json_loads(np)
                    nextPage = self.getFullUrl(np['ajaxurl'])
                    post_data = {'vars':np['query_vars'], 'action':'load_more', 'template':template, 'id_playlist':playlist}
                    printDBG(post_data)
                except Exception:
                    printExc()
            data = tmp[0]
        else:
            post_data['page'] = page
            sts, data = self.getPage(cItem['url'], post_data=self.cm.buildHTTPQuery(post_data))
            if not sts: return
            printDBG("++++++++++++++++++++++++++++++++++++++++++")
            printDBG(data)
            printDBG("++++++++++++++++++++++++++++++++++++++++++")

        data = ph.rfindall(data, '</div>', ('<div', '>', 'entry-content'), flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A_HREF_URI_RE)[1])
            icon = self.getFullIconUrl(ph.search(item, ph.IMAGE_SRC_URI_RE)[1])
            item = item.split('</h3>', 1)
            title = self.cleanHtmlStr( item[0] )
            desc = []
            tmp = ph.findall(item[-1], ('<div', '>'), '</div>', flags=0)
            for t in tmp:
                t = self.cleanHtmlStr(t)
                if t: desc.append(t)

            params = {'good_for_fav':True, 'title':title, 'url':url, 'icon':icon, 'desc':' | '.join(desc)}
            if '/channel/' in url or '/playlist/' in url:
                params.update({'name':'category', 'category':cItem['category']})
                self.addDir( params )
            else:
                self.addVideo( params )

        if post_data:
            post_data['page'] = page + 1
            sts, data = self.getPage(nextPage, post_data=self.cm.buildHTTPQuery(post_data))
            if not sts: return
            if data.count('entry-content'):
                self.addDir(MergeDicts(cItem, {'url':nextPage, 'title':_('Next page'), 'post_data':post_data, 'page':page + 1}))

    def listSearchResult(self, cItem, searchPattern=None, searchType=None):
        page = cItem.get('page', 0)
        if page == 0:
            url = self.getFullUrl('/?s=%s' % urllib.quote(searchPattern))
        else:
            url = cItem['url']

        sts, data = self.getPage(url)
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])

        nextPage = ''
        tmp = ph.find(data, ('{', '}', 'maxPages'))[1]
        try:
            nextPage = self.getFullUrl(json_loads(tmp)['nextLink'])
        except Exception:
            printExc()

        data = ph.find(data, ('<div', '>', 'post-'), '</section>')[1]
        data = ph.rfindall(data, '</div>', ('<div', '>', 'post-'), flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A_HREF_URI_RE)[1])
            icon = self.getFullIconUrl(ph.search(item, ph.IMAGE_SRC_URI_RE)[1])
            item = item.split('</h3>', 1)
            title = self.cleanHtmlStr( item[0] )
            desc = []
            tmp = ph.findall(item[-1], ('<span', '>'), '</span>', flags=0)
            for t in tmp:
                t = self.cleanHtmlStr(t)
                if t: desc.append(t)

            params = {'good_for_fav':True, 'title':title, 'url':url, 'icon':icon, 'desc':' | '.join(desc)}
            if '/channel/' in url or '/playlist/' in url:
                params.update({'name':'category', 'category':'list_items'})
                self.addDir( params )
            else:
                self.addVideo( params )

        if nextPage:
            self.addDir(MergeDicts(cItem, {'category':'list_search_items', 'url':nextPage, 'title':_('Next page'), 'page':page + 1}))

    def getLinksForVideo(self, cItem):

        sts, data = self.getPage(cItem['url'])
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])

        data = ph.find(data, ('<div', '>', 'player'), '</div>')[1]
        url = self.getFullUrl(ph.search(data, '''<iframe[^>]+?src=['"]([^"^']+?)['"]''', flags=ph.IGNORECASE)[0])
        return self.up.getVideoLinkExt(url)

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        printDBG( "handleService: ||| name[%s], category[%s] " % (name, category) )
        self.currList = []

    #MAIN MENU
        if name == None:
            self.listMain({'name':'category', 'type':'category'})

        elif category == 'sub_items':
            self.listSubItems(self.currItem)

        elif category == 'list_items':
            self.listItems(self.currItem)

        elif category == 'list_search_items':
            self.listSearchResult(self.currItem)

    #SEARCH
        elif category in ["search"]:
            cItem = dict(self.currItem)
            cItem.update({'search_item':False, 'name':'category'}) 
            self.listSearchResult(cItem, searchPattern, searchType)
    #HISTORIA SEARCH
        elif category == "search_history":
            self.listsHistory({'name':'history', 'category': 'search'}, 'desc', _("Type: "))
        else:
            printExc()
        
        CBaseHostClass.endHandleService(self, index, refresh)

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, TurcjaTv(), True, [])
