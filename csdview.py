#!/usr/bin/python

#csdview.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
import conn_settings_view
import mplpanel
import connsettingstoolbar as connTB
import plotsettingspanel as plotsp
from wx.lib.pubsub import Publisher as pub

MSG_NOTIFY_ROOT = ('root',)

class LoggerCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(LoggerCtrl, self).__init__(*args, **kwargs)
        # Observer of Notify events
        pub.subscribe(self.updateDisplay, MSG_NOTIFY_ROOT)

    def updateDisplay(self, msg_data):
        if 'logger' in msg_data.topic:
        #     self.printMessage(msg_data.data)
        # else:
        #     print msg_data.topic[-1]
            self.printMessage(msg_data.data)

    def printMessage(self, msg):
        """
        Receives data from thread and updates the display
        """
        self.AppendText(msg+'\n')

class CSDView(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(CSDView, self).__init__(*args, **kwargs)
        self._mgr = aui.AuiManager(self)
        self.canvas1 = mplpanel.MPLPanel(self)
        self.canvas2 = mplpanel.MPLPanel(self)
        self.logger = LoggerCtrl(self, size=wx.Size(800, 100), \
                                     style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.plotsettingspanel = plotsp.Panel(self, size=wx.Size(300,500))
        self.connTB = connTB.Toolbar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT |\
                                 aui.AUI_TB_HORZ_TEXT)
        self._mgr.AddPane(self.connTB, aui.AuiPaneInfo().Name('connTB').
                          Caption('Connection Settings').
                          ToolbarPane().Top())
        self._mgr.AddPane(self.plotsettingspanel, aui.AuiPaneInfo().\
                              Caption('Plot Settings').Left().MinimizeButton())
        self._mgr.AddPane(self.canvas1, aui.AuiPaneInfo().\
                              Caption('Plot Canvas').Center().\
                              MaximizeButton(True))
        self._mgr.AddPane(self.canvas2, aui.AuiPaneInfo().\
                              Caption('AVG Plot').Center().MaximizeButton())
        self._mgr.AddPane(self.logger, aui.AuiPaneInfo().\
                              Caption('Notifications').Bottom().MaximizeButton())
        self._mgr.Update()

        # View related event Bindings

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

    def OnExit(self, event):
        self.Close()

    def OnClose(self, event):
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()


if __name__ == '__main__':

    app = wx.App(False)
    frame = CSDView(None, title='CSD View', size=(1000,700))
    frame.Show(True)
    app.MainLoop()
