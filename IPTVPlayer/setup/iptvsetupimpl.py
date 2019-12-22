# -*- coding: utf-8 -*-

class IPTVSetupImpl:
    def __init__():
        printDBG("IPTVSetupImpl.__init__ -------------------------------")
        Screen.__init__(self, session)

        # wget members
        self.wgetpaths = ["wget", "/usr/bin/wget"]

        # rtmpdump members
        self.rtmpdumppaths = ["/usr/bin/rtmpdump"]

        # f4mdump member
        self.f4mdumppaths = ["/usr/bin/f4mdump"]

        # uchardet member
        self.uchardetpaths = ["/usr/bin/uchardet"]

        # gstplayer
        self.gstplayerpaths = ["/usr/bin/gstplayer"]

        # exteplayer3
        self.exteplayer3paths = ["/usr/bin/exteplayer3"]
                               
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

        self.finish()
