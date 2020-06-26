# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSelOneLink
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist
###################################################

###################################################
# FOREIGN import
###################################################
import urlparse
import re
try:    import json
except Exception: import simplejson as json
from Components.config import config, ConfigSelection, ConfigYesNo, getConfigListEntry
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.fokustv_format = ConfigSelection(default = "1280", choices = [("0",  "najgorsza"),
                                                                                        ("480",  "480x270"),
                                                                                        ("640",  "640x360"),
                                                                                        ("860",  "852x480"),
                                                                                        ("1280", "1280x720"),
                                                                                        ("1920", "1920x1080"),
                                                                                        ("999999", "najlepsza")])
config.plugins.iptvplayer.fokustv_df  = ConfigYesNo(default = True)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry("Domyślna jakość wideo",          config.plugins.iptvplayer.fokustv_format))
    optionList.append(getConfigListEntry("Używaj domyślnej jakości wideo", config.plugins.iptvplayer.fokustv_df))
    return optionList
###################################################

def gettytul():
    return 'http://fokus.tv/'

class FokusTV(CBaseHostClass):
    
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'fokus.tv', 'cookie':'fokus.tv.cookie'})
        self.DEFAULT_ICON_URL = 'https://upload.wikimedia.org/wikipedia/commons/4/47/Fokus_TV_logo_2015.jpg'
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self.MAIN_URL = 'http://www.fokus.tv/'
        self.HEADER = {'User-Agent': self.USER_AGENT, 'DNT':'1', 'Accept': 'text/html', 'Accept-Encoding':'gzip, deflate', 'Referer':self.getMainUrl(), 'Origin':self.getMainUrl()}
        self.AJAX_HEADER = dict(self.HEADER)
        self.AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding':'gzip, deflate', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Accept':'application/json, text/javascript, */*; q=0.01'} )
        
        self.cacheFilters  = {}
        self.cacheLinks   = {}
        self.defaultParams = {'header':self.HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
        
        self.MAIN_CAT_TAB = [
                             {'category':'list_vod_cats',         'title': 'VOD',             'url':self.getFullUrl('/vod') },
                             {'category':'list_cats',             'title': 'Kategorie',       'url':self.getMainUrl() },
                             #{'category':'search',                'title': _('Search'),              'search_item':True, },
                             #{'category':'search_history',        'title': _('Search history'),                          } 
                            ]
    
    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        
        origBaseUrl = baseUrl
        baseUrl = self.cm.iriToUri(baseUrl)
        
        def _getFullUrl(url):
            if self.cm.isValidUrl(url):
                return url
            else:
                return urlparse.urljoin(baseUrl, url)
            
        addParams['cloudflare_params'] = {'domain':self.up.getDomain(baseUrl), 'cookie_file':self.COOKIE_FILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}
        return self.cm.getPageCFProtection(baseUrl, addParams, post_data)
        
    def listMainMenu(self, cItem):
        printDBG("FokusTV.listMainMenu")
        
        params = dict(cItem)
        params.update({'good_for_fav':True, 'title': 'Oglądaj Fokus TV', 'url':self.getFullUrl('/player')})
        self.addVideo(params)
        self.listsTab(self.MAIN_CAT_TAB, cItem)
        
    def listVodCats(self, cItem, nextCategory):
        printDBG("FokusTV.listVodCats")
        
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        data = self.cm.ph.getAllItemsBeetwenNodes(data, ('<div', '>', 'title_ftv'), ('<a', '>', 'video_img more'))
        for item in data:
            url   = self.cm.ph.getSearchGroups(item, '''(<a[^>]+?video_img more[^>]*?>)''')[0]
            url   = self.getFullUrl( self.cm.ph.getSearchGroups(url, '''href=['"]([^'^"]+?)['"]''')[0] )
            title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenReMarkers(item, re.compile('<h'), re.compile('</h[0-9]>'))[1] )
            params = dict(cItem)
            params.update({'good_for_fav':False, 'category':nextCategory, 'title':title, 'url':url})
            self.addDir(params)
        
    def listCats(self, cItem, nextCategory):
        printDBG("FokusTV.listCats")
        
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        data = self.cm.ph.getDataBeetwenReMarkers(data, re.compile('''<div[^>]+?class=['"]cat_'''), re.compile('</div>'))[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
        for item in data:
            url   = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0] )
            title = self.cleanHtmlStr( item )
            params = dict(cItem)
            params.update({'good_for_fav':False, 'category':nextCategory, 'title':title, 'url':url})
            self.addDir(params)
    
    def listChannels(self, cItem, nextCategory):
        printDBG("FokusTV.listChannels")
        
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        sp = re.compile('''<div[^>]+?class=['"]channel['"][^>]*?>''')
        data = self.cm.ph.getDataBeetwenReMarkers(data, sp, re.compile('''<div[^>]+?class=['"]site\-footer['"][^>]*?>'''), False)[1]
        
        data = sp.split(data)
        for item in data:
            url   = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0] )
            icon  = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^'^"]+?)['"]''')[0] )
            title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<span', '</span>')[1] ) 
            desc  = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<p', '</p>')[1] )
            params = dict(cItem)
            params.update({'good_for_fav':True, 'category':nextCategory, 'title':title, 'desc':desc, 'url':url, 'icon':icon})
            self.addDir(params)
        
    def listItems(self, cItem, nextCategory):
        printDBG("FokusTV.listItems [%s]" % cItem)
        
        page = cItem.get('page', 1)
        url = cItem['url']
        
        if page > 1: url += '/%s' % page
        
        sts, data = self.getPage(url)
        if not sts: return
        
        nextPage = self.cm.ph.getSearchGroups(data, '''(<a[^>]+?class="next_ftv"[^>]*?>)''')[0]
        nextPage = self.cm.ph.getSearchGroups(nextPage, '''href=['"]([^'^"]+?)['"]''')[0]
        if nextPage != '': nextPage = True
        else: nextPage = False
        
        data = self.cm.ph.getAllItemsBeetwenNodes(data, ('<div', '>', 'box_small_video'), ('</div', '>'))
        for item in data:
            url   = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0] )
            icon  = self.getFullIconUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^'^"]+?)['"]''')[0] )
            title = self.cleanHtmlStr( item )
            params = dict(cItem)
            params.update({'good_for_fav':True, 'category':nextCategory, 'title':title, 'url':url, 'icon':icon})
            self.addDir(params)
        
        if nextPage and len(self.currList) > 0:
            params = dict(cItem)
            params.update({'good_for_fav':False, 'title':_("Next page"), 'page':page+1})
            self.addDir(params)
            
    def listItems2(self, cItem, nextCategory):
        printDBG("FokusTV.listItems2 [%s]" % cItem)
        
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        splitReObj = re.compile('''<div[^>]+?box_small_video_image[^>]+?>''')
        tmp = self.cm.ph.getAllItemsBeetwenNodes(data, ('<div', '>', 'box_small_video'), ('<a', '>', 'class="more"'))
        for data in tmp:
            data = splitReObj.split(data)
            if len(data): del data[0]
            for item in data:
                tmp = self.cm.ph.getDataBeetwenReMarkers(item, re.compile('''<a[^>]+?cat_vod'''), re.compile('''</a>'''))[1]
                catUrl   = self.getFullUrl( self.cm.ph.getSearchGroups(tmp, '''href=['"]([^'^"]+?)['"]''')[0] )
                catTitle = self.cleanHtmlStr( tmp )
                
                tmp = self.cm.ph.getDataBeetwenReMarkers(item, re.compile('''<a[^>]+?video_title'''), re.compile('''</a>'''))[1]
                url   = self.getFullUrl( self.cm.ph.getSearchGroups(tmp, '''href=['"]([^'^"]+?)['"]''')[0] )
                icon  = self.getFullIconUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^'^"]+?)['"]''')[0] )
                title = self.cleanHtmlStr( tmp )
                desc  = self.cleanHtmlStr( item.split('</div>', 1)[0] )
                params = dict(cItem)
                params.update({'good_for_fav':True, 'category':nextCategory, 'title':title, 'desc':desc, 'url':url, 'cat_url':catUrl, 'cat_title':catTitle, 'icon':icon})
                self.addDir(params)
        
    def exploreItem(self, cItem):
        printDBG("FokusTV.exploreItem [%s]" % cItem)
        
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        
        cItem = dict(cItem)
        
        catUrl   = cItem.pop('cat_url', '')
        catTitle = cItem.pop('cat_title', '')
        
        desc = []
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div class="wideo_info', '</div>')[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<span', '</span>')
        for item in tmp:
            t = self.cleanHtmlStr( item )
            if t != '':
                pg = self.cm.ph.getSearchGroups(item, '''pg_([0-9]+?)[^0-9]''')[0]
                if pg != '': pg = ' ' + pg
                desc.append(t + pg)
        
        desc = ' | '.join(desc) + '[/br]' + self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(data, '<p class="desc_opis"', '</p>')[1] )
        
        if '<video' in data: haveVideoSource = True
        else: haveVideoSource = False
        
        listVideos = False
        if 'Sezon' in data:
            data = ''.join(self.cm.ph.getAllItemsBeetwenNodes(data, ('Sezon', 'box_small'), ('<div', '>', 'class="clear"'), False))
            listVideos = True
        elif 'zobacz wszystkie odcinki' in data or ('zobacz wszystko' in data and 'Odcinki' in data):
            listVideos = True
        
        if listVideos:
            data = self.cm.ph.getAllItemsBeetwenNodes(data, ('<div class="box_small', '>', 'video'), ('</div', '>'))
            for item in data:
                url = self.cm.ph.getSearchGroups(item, '''href=['"]([^'^"]+?)['"]''')[0]
                if url in ['', '#']: continue
                icon  = self.getFullIconUrl( self.cm.ph.getSearchGroups(item, '''src=['"]([^'^"]+?)['"]''')[0] )
                title = self.cleanHtmlStr( item )
                params = dict(cItem)
                params.update({'good_for_fav':True, 'title':title, 'url':self.getFullUrl(url), 'icon':icon, 'desc':desc})
                self.addVideo(params)
        
        if haveVideoSource and 0 == len(self.currList):
            params = dict(cItem)
            params.update({'desc':desc})
            self.addVideo(params)
            if self.cm.isValidUrl(catUrl):
                params = dict(cItem)
                params.update({'title':catTitle, 'url':catUrl})
                self.addDir(params)
        
    def getLinksForVideo(self, cItem):
        printDBG("FokusTV.getLinksForVideo [%s]" % cItem)
        urlTab = []
        
        url = cItem['url']
        sts, data = self.getPage(url)
        if not sts: return []
        
        if url.endswith('/player'):
            tab = ['fokustv-p/stream1']
            data = self.cm.ph.getDataBeetwenMarkers(data, '$.post(', 'function', withMarkers=False)[1]
            secureUri =  self.cm.ph.getSearchGroups(data, '''(https?://[^'^"]+?)['"]''')[0]
            streamUri = self.cm.ph.getSearchGroups(data, '''streamUri['"\s]*?:\s*?['"]([^'^"]+?)['"]''')[0]
            
            if secureUri == '': secureUri = 'https://api.stream.smcdn.pl/api/secureToken.php'
            elif streamUri not in tab: tab.insert(0, streamUri)
            
            for streamUri in tab:
                sts, url = self.getPage(secureUri, post_data={'streamUri':streamUri})
                if not sts: continue
                
                if self.cm.isValidUrl(url):
                    data = getDirectM3U8Playlist(url, checkExt=True, checkContent=True)
                    for item in data:
                        item['url'] = strwithmeta(item['url'], {'iptv_proto':'m3u8', 'iptv_livestream':True})
                        urlTab.append(item)
        else:
            data = self.cm.ph.getDataBeetwenMarkers(data, '<video', '</video>')[1]
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<source ', '>', False, False)
            for item in data:
                url  = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''')[0].replace('&amp;', '&')
                if url.startswith('//'):
                    url = 'http:' + url
                if not url.startswith('http'):
                    continue
                
                if 'video/mp4' in item:
                    type = self.cm.ph.getSearchGroups(item, '''type=['"]([^"^']+?)['"]''')[0]
                    res  = self.cm.ph.getSearchGroups(item, '''res=['"]([^"^']+?)['"]''')[0]
                    label = self.cm.ph.getSearchGroups(item, '''label=['"]([^"^']+?)['"]''')[0]
                    if label == '': label = res
                    if label == '': label = type
                    url = strwithmeta(url, {'Referer':cItem['url'],  'User-Agent':self.USER_AGENT})
                    urlTab.append({'name':'{0}'.format(label), 'url':url})
                elif 'mpegurl' in item:
                    url = strwithmeta(url, {'iptv_proto':'m3u8', 'Referer':cItem['url'], 'Origin':self.up.getDomain(cItem['url'], False), 'User-Agent':self.USER_AGENT})
                    tmpTab = getDirectM3U8Playlist(url, checkExt=True, checkContent=True)
                    for idx in range(len(tmpTab)): tmpTab[idx]['url'].meta['iptv_proto'] = 'm3u8'
                    urlTab.extend(tmpTab)
                    
        if 1 < len(urlTab):
            maxQuality = int(config.plugins.iptvplayer.fokustv_format.value) + 20
            def __getLinkQuality( itemLink ):
                try: return int(itemLink['with'])
                except Exception: return 0
            oneLink = CSelOneLink(urlTab, __getLinkQuality, maxQuality)
            if config.plugins.iptvplayer.fokustv_df.value:
                urlTab = oneLink.getOneLink()
            else:
                urlTab = oneLink.getSortedLinks()
                        
        return urlTab
    
    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        mode     = self.currItem.get("mode", '')
        
        printDBG( "handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] " % (name, category) )
        self.currList = []
        
    #MAIN MENU
        if name == None:
            self.listMainMenu({'name':'category'})
        elif category == 'list_vod_cats':
            self.listVodCats(self.currItem, 'list_items')
        elif category == 'list_cats':
            self.listCats(self.currItem, 'list_items_2')
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'list_items_2':
            self.listItems2(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem)
    #SEARCH
        elif category in ["search", "search_next_page"]:
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
        CHostBase.__init__(self, FokusTV(), True, [])
    
    