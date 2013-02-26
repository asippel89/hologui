#!/usr/bin/python

#csdcontroller.py

import wx
from wx.lib.pubsub import Publisher as pub
import csdframe
import timedatastruct as tds
import time
import threading

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
 
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

def global_report_data(window, listener, data):
    wx.PostEvent(window, ResultEvent([listener, data]))

class MainController(object):

    def __init__(self):
        self.model = tds.TimeData()
        self.frame = csdframe.CSDFrame(None, title='Controller Test', size=(1000,700))
        self.frame.Show(True)
        self.stream = None
        #subscribe to *ALL* Notifications
        pub.subscribe(self.on_control)
        # Bind our ResultEvents
        EVT_RESULT(self.frame, self.on_event_result)
        self.frame.Bind(wx.EVT_CLOSE, self.on_close)

    def on_control(self, msg):
        # print 'Notification Topic:', msg.topic, 'Value:', msg.data
        if msg.topic == ('controller', 'connect'):
            host = msg.data['host']
            port = msg.data['port']
            logmsg = '\tTrying to connect to '+host+' on port '+port
            pub.sendMessage('logger', logmsg)
            self.start_connection(host, port)
            self.start_test_in_thread()
        if 'disconnect' in msg.topic:
            pub.sendMessage('logger', '\tDisconnecting')
            pub.sendMessage('connsett', 'disconnected')
            self.stream.keep_going = False
        if 'newdata' in msg.topic:
            self.handle_new_data(msg.data)

    def handle_new_data(self, data):
        self.model.add_data_object(data)
        new_data = self.model.get_current_data()
        timestamp = self.model.get_current_time()
        run_info = self.model.get_current_run_info()
        pub.sendMessage('run_info', run_info)
        time_data = [timestamp, new_data]
        pub.sendMessage('data_dict', time_data)
        available_channels = self.model.get_current_data().keys()
        pub.sendMessage('available_channels', available_channels)

    def start_connection(self, host, port):
        pass

    def report_data_method(self, data):
        wx.PostEvent(self.frame, ResultEvent(['newdata', data]))

    def start_test_in_thread(self):
        def innerrun():
            time.sleep(2)
            logmsg = '\tConnected Successfully!'
            global_report_data(self.frame, 'logger', logmsg)
            global_report_data(self.frame, 'connsett', 'connected')
            self.stream = tds.StreamDataTest(self.frame, self.report_data_method)
            self.stream._run_stream()
        thread = threading.Thread(target=innerrun)
        thread.start()
        
    def on_event_result(self, event):
        pub.sendMessage(event.data[0], event.data[1])

    def on_close(self, event):
        if self.stream is not None:
            self.stream.keep_going = False
        self.frame.Destroy()

if __name__ == '__main__':

    app = wx.App(False)
    controller = MainController()
    app.MainLoop()
