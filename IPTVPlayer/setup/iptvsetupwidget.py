# -*- coding: utf-8 -*-
#
#  Update iptv setup main window
#


###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools           import printDBG, printExc, GetIPTVPlayerVerstion, GetIconDir
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, IPTVPlayerNeedInit
from Plugins.Extensions.IPTVPlayer.components.cover          import Cover3
from Plugins.Extensions.IPTVPlayer.setup.iptvsetupimpl       import IPTVSetupImpl
###################################################

###################################################
# FOREIGN import
###################################################
from enigma import getDesktop, eTimer
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
###################################################

class IPTVSetupMainWidget(Screen):
    IPTV_VERSION = GetIPTVPlayerVerstion()
    def __init__(self, session, autoStart=False):
        printDBG("IPTVUpdateMainWindow.__init__ -------------------------------")
        Screen.__init__(self, session)

        #flags
        self.autoStart          = autoStart
        self.underCloseMessage  = False
        self.underClosing       = False
        self.deferredAction     = None
        self.started            = True

        self.setupImpl = IPTVSetupImpl(self.finished, self.chooseQuestion, self.showMessage, self.setInfo)
        self.setupImpl.start()

    def showMessage(self, message, type, callback):
        printDBG("IPTVSetupMainWidget.showMessage")
        if self.underClosing: return
        if self.underCloseMessage: self.deferredAction =  boundFunction(self.doShowMessage, message, type, callback)
        else: self.doShowMessage(message, type, callback)
        
    def doShowMessage(self, message, type, callback):
        self.session.openWithCallback(callback, MessageBox, text=message, type=type)
        
    def chooseQuestion(self, title, list, callback):
        printDBG("IPTVSetupMainWidget.chooseQuestion")
        if self.underClosing: return
        if self.underCloseMessage: self.deferredAction =  boundFunction(self.dochooseQuestion, title, list, callback)
        else: self.dochooseQuestion(title, list, callback)
        
    def dochooseQuestion(self, title, list, callback):
        title += "                                                                         " # workaround for truncation message by stupid E2
        title = title.replace('\n', ' ').replace(' ', chr(160))
        self.session.openWithCallback(callback, ChoiceBox, title=title, list = list)
        
    def setInfo(self, title, message):
        if self.underClosing: return
        if None != title: self["sub_title"].setText(title)
        if None != message: self["info_field"].setText(message)
        
    def finished(self):
        if self.underClosing: return
        if self.underCloseMessage: self.deferredAction = self.doFinished
        else: self.doFinished()
        
    def doFinished(self):
        self.close()
