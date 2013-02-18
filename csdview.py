#!/usr/bin/python

#csdview.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
import conn_settings_view as consett
import mplpanel
import connsettingstoolbar as connTB
import csdplotsettingspanel as csdplotsp
import avgplotsettingspanel as avgplotsp
from wx.lib.pubsub import Publisher as pub

MSG_NOTIFY_ROOT = ('root',)

class LoggerCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(LoggerCtrl, self).__init__(*args, **kwargs)
        # Observer of Notify events
        pub.subscribe(self.updateDisplay, 'logger')

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
        # Create Center Plot Notebook
        self.auinb = aui.AuiNotebook(self)
        self.canvas1 = mplpanel.MPLPanel(self)
        self.canvas2 = mplpanel.MPLPanel(self)
        self.auinb.AddPage(self.canvas1, 'CSD Plot', select=True)
        self.auinb.AddPage(self.canvas2, 'AVG Plot')
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        # Create other View Objects
        self.logger = LoggerCtrl(self, size=wx.Size(800, 100), \
                                     style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.csdplotsettings = csdplotsp.CSDPlotSettingsPanel(self, \
                                                            size=wx.Size(200,500))
        self.avgplotsettings = avgplotsp.AVGPlotSettingsPanel(self,\
                                                            size=wx.Size(200,500))
        self.connTB = connTB.Toolbar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT |\
                                 aui.AUI_TB_HORZ_TEXT)
        # Add View Objects to Manager
        self._mgr.AddPane(self.connTB, aui.AuiPaneInfo().Name('connTB').
                          Caption('Connection Settings').
                          ToolbarPane().Bottom())
        self._mgr.AddPane(self.logger, aui.AuiPaneInfo().\
                              Caption('Notifications').Bottom().\
                              MaximizeButton().MinimizeButton())
        self._mgr.AddPane(self.csdplotsettings, aui.AuiPaneInfo().Name('CSDSet').\
                              Caption('CSD Plot Settings').Left().MinimizeButton())
        self._mgr.AddPane(self.avgplotsettings, aui.AuiPaneInfo().Name('AVGSet').\
                              Caption('AVG Plot Settings').Left().MinimizeButton().\
                              Hide())
        self._mgr.AddPane(self.auinb, aui.AuiPaneInfo().\
                              Caption('Plots').Center().MaximizeButton())
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

    def on_page_changed(self, event):
        active_tab_index = self.auinb.GetSelection()
        active_tab_label = self.auinb.GetPageText(active_tab_index)
        if 'AVG' in active_tab_label:
            self._mgr.GetPane('CSDSet').Hide()
            self._mgr.GetPane('AVGSet').Show()
            self._mgr.Update()
        if 'CSD' in active_tab_label:
            self._mgr.GetPane('AVGSet').Hide()
            self._mgr.GetPane('CSDSet').Show()
            self._mgr.Update()

if __name__ == '__main__':

    app = wx.App(False)
    frame = CSDView(None, title='CSD View', size=(1000,700))
    frame.Show(True)
    app.MainLoop()
