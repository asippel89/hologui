#!/usr/bin/python

#loggerctrl.py

import wx
from wx.lib.pubsub import Publisher as pub
from threading import Lock

class LoggerCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(LoggerCtrl, self).__init__(*args, **kwargs)
        self.mutex = Lock()
        # Observer of Notify Events
        pub.subscribe(self.updateDisplay, 'logger')

    def updateDisplay(self, msg_data):
        if 'logger' in msg_data.topic:
            with self.mutex:
                self.AppendText(str(msg_data.data)+'\n')
