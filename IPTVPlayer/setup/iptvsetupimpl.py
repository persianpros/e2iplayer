# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools           import printDBG, printExc, GetBinDir, GetTmpDir, GetPyScriptCmd, IsFPUAvailable, ReadGnuMIPSABIFP, GetResourcesServerUri
from Plugins.Extensions.IPTVPlayer.setup.iptvsetuphelper     import CBinaryStepHelper, CCmdValidator, SetupDownloaderCmdCreator
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
###################################################

###################################################
# FOREIGN import
###################################################
from Screens.MessageBox  import MessageBox
from Components.config   import config, configfile
from Tools.BoundFunction import boundFunction
from Tools.Directories   import resolveFilename, SCOPE_PLUGINS
from os                  import path as os_path, chmod as os_chmod, remove as os_remove, listdir as os_listdir, getpid as os_getpid, symlink as os_symlink, unlink as os_unlink
import re
import sys
###################################################

class IPTVSetupImpl:
    def __init__(self, finished, chooseQuestion, showMessage, setInfo):
        printDBG("IPTVSetupImpl.__init__ -------------------------------")
        
        # callbacks
        self._finished    = finished
        self._chooseQuestion = chooseQuestion
        self._showMessage = showMessage
        self._setInfo     = setInfo
        self.workingObj   = None
        self.stepHelper   = None
        self.termination  = False
        
        self.tmpDir = GetTmpDir()
        self.resourceServers = [GetResourcesServerUri()]
        
        self.ffmpegVersion = ""
        self.gstreamerVersion = ""
        self.openSSLVersion = ""
        self.libSSLPath = ""
        self.platform = "unknown"
        self.glibcVersion = -1
        
        # wget members
        self.wgetVersion = 1902 # 1.15 
        self.wgetpaths = ["wget", "/usr/bin/wget", "/usr/bin/fullwget", GetBinDir("wget", "")]
        self._wgetInstallChoiseList = [(_('Install into the "%s".') % ("/usr/bin/fullwget " + _("recommended")), "/usr/bin/fullwget"),
                                       (_('Install into the "%s".') % "IPTVPlayer/bin/wget", GetBinDir("wget", "")),
                                       (_('Install into the "%s".') % "/usr/bin/wget", "/usr/bin/wget"),
                                       (_("Do not install (not recommended)"), "")]
        # rtmpdump members
        self.rtmpdumpVersion = 20151215 #{'sh4':'2015', 'mipsel':'2015', 'armv5t':'2015', 'armv7':'2015', 'default':"Compiled by samsamsam@o2.pl 2015-01-11"} #'K-S-V patch'
        self.rtmpdumppaths = ["/usr/bin/rtmpdump", "rtmpdump"]
        
        # f4mdump member
        self.f4mdumpVersion = 0.80
        self.f4mdumppaths = ["/usr/bin/f4mdump", GetBinDir("f4mdump", "")]
        self._f4mdumpInstallChoiseList = [(_('Install into the "%s".') % ("/usr/bin/f4mdump (%s)" % _("recommended")), "/usr/bin/f4mdump"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/f4mdump", GetBinDir("f4mdump", "")),
                                          (_("Do not install (not recommended)"), "")]
        self._f4mdumpInstallChoiseList2 = [(_('Install into the "%s".') % ("/usr/bin/f4mdump static libstdc++ (%s)" % _("recommended")), "/usr/bin/f4mdump"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/f4mdump _static_libstdc++", GetBinDir("f4mdump", "")),
                                          (_("Do not install (not recommended)"), "")]
                                          
        # uchardet member
        self.uchardetVersion = [0, 0, 6] #UCHARDET_VERSION_MAJOR, UCHARDET_VERSION_MINOR, UCHARDET_VERSION_REVISION
        self.uchardetpaths = ["/usr/bin/uchardet", GetBinDir("uchardet", "")]
        self._uchardetInstallChoiseList = [(_('Install into the "%s".') % ("/usr/bin/uchardet (%s)" % _("recommended")), "/usr/bin/uchardet"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/uchardet", GetBinDir("uchardet", "")),
                                          (_("Do not install (not recommended)"), "")]
        self._uchardetInstallChoiseList2 = [(_('Install into the "%s".') % ("/usr/bin/uchardet static libstdc++ (%s)" % _("recommended")), "/usr/bin/uchardet"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/uchardet _static_libstdc++", GetBinDir("uchardet", "")),
                                          (_("Do not install (not recommended)"), "")]
        # gstplayer
        self.gstplayerVersion = {'0.10':20, '1.0':10021}
        self.gstplayerpaths = ["/usr/bin/gstplayer", GetBinDir("gstplayer", "")]
        self._gstplayerInstallChoiseList = [(_('Install into the "%s".') % ("/usr/bin/gstplayer (%s)" % _("recommended")), "/usr/bin/gstplayer"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/gstplayer", GetBinDir("gstplayer", "")),
                                          (_("Do not install (not recommended)"), "")]
        # exteplayer3
        self.exteplayer3Version = {'sh4':50, 'mipsel':50, 'armv7':50, 'armv5t':50}
        self.exteplayer3paths = ["/usr/bin/exteplayer3", GetBinDir("exteplayer3", "")]
        self._exteplayer3InstallChoiseList = [(_('Install into the "%s".') % ("/usr/bin/exteplayer3 (%s)" % _("recommended")), "/usr/bin/exteplayer3"),
                                          (_('Install into the "%s".') % "IPTVPlayer/bin/exteplayer3", GetBinDir("exteplayer3", "")),
                                          (_("Do not install (not recommended)"), "")]
                                          
        # flumpegdemux
        self.flumpegdemuxVersion = "0.10.85"
        self.flumpegdemuxpaths = ["/usr/lib/gstreamer-0.10/libgstflumpegdemux.so"]
        
        # gstifdsrc
        self.gstifdsrcVersion = "1.1.1"
        self.gstifdsrcPaths = ["/usr/lib/gstreamer-1.0/libgstifdsrc.so"]
        
        # subparser
        self.subparserVersion = 0.5
        self.subparserPaths = [resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/libs/iptvsubparser/_subparser.so')]

        # e2icjson
        self.e2icjsonVersion = 10202 #'1.2.2' int(z[0]) * 10000 + int(z[1]) * 100 + int(z[2])
        self.e2icjsonPaths = [resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/libs/e2icjson/e2icjson.so')]

        # hlsdl
        self.hlsdlVersion = 0.21
        self.hlsdlPaths = ["/usr/bin/hlsdl"]
        
        # cmdwrap
        self.cmdwrapVersion = 2
        self.cmdwrapPaths = ["/usr/bin/cmdwrapper"]
        
        # duk
        self.dukVersion = 6 # "2.1.99 [experimental]" # real version
        self.dukPaths = ["/usr/bin/duk"]
        
        self.binaryInstalledSuccessfully = False
        self.tries = 0
        self.hasAbiFlags = None
        self.abiFP = None
        
        self.finish()

    def __del__(self):
        printDBG("IPTVSetupImpl.__del__ -------------------------------")
        
    def terminate(self):
        printDBG("IPTVSetupImpl.terminate -------------------------------")
        self.termination  = True
        self._finished    = None
        self._chooseQuestion = None
        self._showMessage = None
        self._setInfo     = None 
        if self.workingObj: self.workingObj.terminate()
        
    def finish(self, sts=None, ret=None):
        printDBG("IPTVSetupImpl.finish")
        if self._finished: self._finished()
        
    def chooseQuestion(self, title, list, callback):
        printDBG("IPTVSetupImpl.chooseQuestion")
        if self._chooseQuestion: self._chooseQuestion(title, list, callback)
        
    def showMessage(self, message, type, callback):
        printDBG("IPTVSetupImpl.showMessage")
        if self._showMessage: self._showMessage(message, type, callback)
        
    def setInfo(self, title, message):
        printDBG("IPTVSetupImpl.setInfo")
        if self._setInfo: self._setInfo(title, message)
        
    def setInfoFromStepHelper(self, key):
        if None != self.stepHelper:
            self.setInfo(_(self.stepHelper.getMessage(key,0)), _(self.stepHelper.getMessage(key,1)))
