#!/usr/bin/python

#connsettingstoolbar.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

class Toolbar(aui.AuiToolBar):

    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
        
        self.create_items()
        self.add_items()

        self.SetToolDropDown(wx.ID_ANY, True)
        self.Realize()

    def create_items(self):
        self.hostLabel = wx.StaticText(self, label="Host:")
        self.hostCtrl = wx.TextCtrl(self, value="localhost")
        self.portLabel = wx.StaticText(self, label="Port:")
        self.portCtrl = wx.TextCtrl(self, value="12345")
        self.connectButton = wx.Button(self, label="Connect")

    def add_items(self):
        self.AddControl(self.hostLabel)
        self.AddControl(self.hostCtrl)
        self.AddControl(self.portLabel)
        self.AddControl(self.portCtrl)
        self.AddSeparator()
        self.AddControl(self.connectButton)

if __name__ == '__main__':

    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            textCtrl = wx.TextCtrl(self, size=wx.Size(800, 300), \
                                       style=wx.TE_MULTILINE)
            tb = Toolbar(self, -1, wx.DefaultPosition, wx.DefaultSize, 
                         agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT |\
                             aui.AUI_TB_HORZ_TEXT)
            self._mgr.AddPane(tb, aui.AuiPaneInfo().Name('tb').
                              Caption('Connection Settings').
                              ToolbarPane().Top())
            self._mgr.AddPane(textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Toolbar Test")
    frame.Show(True)
    app.MainLoop()
