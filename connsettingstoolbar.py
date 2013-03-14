#!/usr/bin/python

#connsettingstoolbar.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
from wx.lib.pubsub import Publisher as pub
import threading
import random
import spectrum_gen

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

    def toggle_connect_button(self):
        if self.connectButton.GetLabel() == 'Connect':
            self.connectButton.SetLabel('Pause')
        else:
            self.connectButton.SetLabel('Connect')

    def report_field_values(self):
        hostval = self.hostCtrl.GetValue()
        portval = self.portCtrl.GetValue()
        field_dict = dict((('host', hostval), ('port', portval)))
        return field_dict

class ConnSettingsPresenter(object):
    def __init__(self, frame):
        self.frame = frame
        self.tb = Toolbar(self.frame, -1, wx.DefaultPosition, wx.DefaultSize, 
                          agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT |\
                              aui.AUI_TB_HORZ_TEXT)
        self.tb.connectButton.Bind(wx.EVT_BUTTON, self.on_connect_button)
        pub.subscribe(self.update_connsett, 'connsett')

    def update_connsett(self, event):
        if event.data == 'connected':
            self.tb.connectButton.Enable()
            self.tb.connectButton.SetLabel('Disconnect')
        if event.data == 'disconnected':
            self.tb.connectButton.SetLabel('Connect')
        if event.data == 'enable_button':
            self.tb.connectButton.Enable()

    def on_connect_button(self, event):
        if self.tb.connectButton.GetLabel() == 'Connect':
            values_dict = self.tb.report_field_values()
            pub.sendMessage('controller.connect', values_dict)
            # self.tb.connectButton.Disable()
        if self.tb.connectButton.GetLabel() == 'Disconnect':
            pub.sendMessage('controller.disconnect', 'blahh')

if __name__ == '__main__':

    class View(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(View, self).__init__(*args, **kwargs)
            # initiate widget presenters
            self.tbPresenter = ConnSettingsPresenter(self)
            
            # create and populate the AuiManager
            self._mgr = aui.AuiManager(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 300), \
                                       style=wx.TE_MULTILINE)
            self.switchconnectbutton = wx.Button(self, label="Switch Connect Label")
            self.tb = self.tbPresenter.tb
            self._mgr.AddPane(self.tb, aui.AuiPaneInfo().Name('tb').
                              Caption('Connection Settings').
                              ToolbarPane().Top())
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.AddPane(self.switchconnectbutton,\
                                  aui.AuiPaneInfo().Name('otherbutton').\
                                  Bottom())
            self._mgr.Update()

    class Controller(object):
        def __init__(self, app):
            self.view = View(None, title="Toolbar Test")
            self.view.Show(True)
            self.app = app
            # Bind events
            self.view.Bind(wx.EVT_BUTTON, self.on_button)
            pub.subscribe(self.on_logger, 'logger')

            self.app.MainLoop()


        def on_button(self, event):
            if event.GetEventObject() == self.view.switchconnectbutton:
                pub.sendMessage('connsett', 'update_button')
            if event.GetEventObject() == self.view.tb.connectButton:
                self.view.textCtrl.AppendText('Connect Button Clicked\n')

        def on_logger(self, event):
            self.view.textCtrl.AppendText(str(event.data)+'\n')

    app = wx.App(False)
    controller = Controller(app)
