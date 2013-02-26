#!/usr/bin/python

#csdviewtoolbar.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
from wx.lib.pubsub import Publisher as pub

class Toolbar(aui.AuiToolBar):

    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
        
        self.create_items()
        self.add_items()

        self.SetToolDropDown(wx.ID_ANY, True)
        self.Realize()

    def create_items(self):
        self.addCSDButton = wx.Button(self, label="Add CSD Plot Tab")
        self.addRMSButton = wx.Button(self, label="Add RMS Plot Tab")

    def add_items(self):
        self.AddControl(self.addCSDButton)
        self.AddControl(self.addRMSButton)

