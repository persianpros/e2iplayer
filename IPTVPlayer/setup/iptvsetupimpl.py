# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools           import printDBG, printExc, GetBinDir, GetTmpDir, GetPyScriptCmd, IsFPUAvailable, ReadGnuMIPSABIFP, GetResourcesServerUri
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
    def __init__():
        printDBG("IPTVSetupImpl.__init__ -------------------------------")
        Screen.__init__(self, session)

        self.tmpDir = GetTmpDir()

        self.ffmpegVersion = ""
        self.gstreamerVersion = ""
        self.openSSLVersion = ""
        self.libSSLPath = ""
        self.platform = "unknown"
        self.glibcVersion = -1

        # wget members
        self.wgetpaths = ["wget", "/usr/bin/wget"]

        # rtmpdump members
        self.rtmpdumppaths = ["/usr/bin/rtmpdump", "rtmpdump"]
        
        # f4mdump member
        self.f4mdumppaths = ["/usr/bin/f4mdump", GetBinDir("f4mdump", "")]
                                          
        # uchardet member
        self.uchardetpaths = ["/usr/bin/uchardet", GetBinDir("uchardet", "")]

        # gstplayer
        self.gstplayerpaths = ["/usr/bin/gstplayer", GetBinDir("gstplayer", "")]

        # exteplayer3
        self.exteplayer3paths = ["/usr/bin/exteplayer3", GetBinDir("exteplayer3", "")]
                                          
        # flumpegdemux
        self.flumpegdemuxpaths = ["/usr/lib/gstreamer-0.10/libgstflumpegdemux.so"]
        
        # gstifdsrc
        self.gstifdsrcPaths = ["/usr/lib/gstreamer-1.0/libgstifdsrc.so"]
        
        # subparser
        self.subparserPaths = [resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/libs/iptvsubparser/_subparser.so')]

        # e2icjson
        self.e2icjsonPaths = [resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/libs/e2icjson/e2icjson.so')]

        # hlsdl
        self.hlsdlPaths = ["/usr/bin/hlsdl"]
        
        # cmdwrap
        self.cmdwrapPaths = ["/usr/bin/cmdwrapper"]
        
        # duk
        self.dukPaths = ["/usr/bin/duk"]
        
        self.tries = 0
        self.hasAbiFlags = None
        self.abiFP = None
        
        self.finish()
