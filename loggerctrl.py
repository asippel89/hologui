#!/usr/bin/python

#loggerctrl.py

import wx
from wx.lib.pubsub import Publisher as pub

class LoggerCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(LoggerCtrl, self).__init__(*args, **kwargs)
        # Observer of Notify Events
        pub.subscribe(self.updateDisplay, 'logger')

    def updateDisplay(self, msg_data):
        if 'logger' in msg_data.topic:
            self.AppendText(str(msg_data.data)+'\n')
