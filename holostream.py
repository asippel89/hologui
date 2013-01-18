#!/usr/bin/python

#holostream.py

import wx
import wx.aui
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from wx.lib.pubsub import Publisher
import p2acnet
import threading
import numpy as np
import matplotlib.pyplot as plt
import time
import random

# PubSub message classification
MSG_NOTIFY_ROOT = ('root',)

class Notifier(object):
    def __init__(self):
        super(Notifier, self).__init__()
        self._data = dict()

    def SetValue(self, key, value):
        self._data[key] = value
        # Notify all observers of config change
        Publisher.sendMessage(MSG_NOTIFY_ROOT + (key,), value)

    def GetValue(self, key):
        return self._data.get(key, None)

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

#------------------Begin Main GUI Classes---------------------#

class ControlPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self.createControls()
        self.bindEvents()
        self.doLayout()
        self.datagen = DataGen()
        self.redraw_timer = wx.Timer(self)
        self.is_paused = 0
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        Publisher.subscribe(self.updateDisplay, MSG_NOTIFY_ROOT)        

    def createControls(self):
        self.runButton = wx.Button(self, label="Run")
        self.resetButton = wx.Button(self, label="Reset")
        self.resetButton.Disable()
        self.testButton = wx.Button(self, label="TestThread")
        self.titleLabel = wx.StaticText(self, label="Title:")
        self.titleTextCtrl = wx.TextCtrl(self, value="Enter plot title here")
        self.verboseCheckBox = wx.CheckBox(self, label="Do you want verbose output?")
        self.verboseCheckBox.SetValue(True)

    def doLayout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [(self.titleLabel, expandOption),
                 emptySpace,
                 (self.titleTextCtrl, expandOption),
                 emptySpace,
                 (self.verboseCheckBox, noOptions),
                 emptySpace,
                 (self.runButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace,
                 (self.testButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace,
                 (self.resetButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace]:
            gridSizer.Add(control, **options)
        self.SetSizer(gridSizer)

    def bindEvents(self):
        for control, event, handler in \
            [(self.runButton, wx.EVT_BUTTON, self.onRun),
             (self.testButton, wx.EVT_BUTTON, self.onTestThread),
             (self, wx.EVT_TEXT, self.onTextEntered),
             (self, wx.EVT_COMBOBOX, self.onComboChanged),
             (self, wx.EVT_CHECKBOX, self.onCheckboxChanged),
             (self.resetButton, wx.EVT_BUTTON, self.onReset)]:
            control.Bind(event, handler)

    def onTextEntered(self, event):
        # evt_obj = event.GetEventObject()
        # print "Entered Text into %s" % evt_obj.GetLabel()
        pass

    def onComboChanged(self, event):
        # evt_obj = event.GetEventObject()
        # print "Changed the combobox for %s" %evt_obj
        pass

    def onCheckboxChanged(self, event):
        # evt_obj = event.GetEventObject()
        # print "Changed the checkbox for %s" %evt_obj
        pass

    def onRun(self, event):
        """
        Runs the thread, sending the query to acnet and reporting the results
        to the mplpanel via the custom event ResultEvent
        """
        self.runButton.Disable()
        Title = self.titleTextCtrl.GetValue()
        if Title == 'Enter plot title here':
            Title = ''
        Verbose = self.verboseCheckBox.GetValue()
        # mplcanvas_msg_dict = dict([('title', Title), ('start', start_fmt), \
        #                               ('end', end_fmt), ('grid', Grid)])
        # wx.PostEvent(self, ResultEvent(['mpl_canvas', mplcanvas_msg_dict]))
        def innerrun():
            pass
        Query = threading.Thread(target=innerrun)
        Query.start()
        self.printLogger('Query Started')
        
    def onTestThread(self, event):
        if self.is_paused == 0:
            self.redraw_timer.Start(200)
            self.testButton.SetLabel('Pause')
            self.resetButton.Enable()
            self.is_paused = 1
        elif self.is_paused == 1:
            self.redraw_timer.Stop()
            self.testButton.SetLabel('Resume')
            self.is_paused = 0

    def on_redraw_timer(self, event):
        def innerrun():
            # self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
            # self.redraw_timer.Start(200)
            newval = self.datagen.next()
            wx.PostEvent(self, ResultEvent(['plot_data', newval]))
        Query = threading.Thread(target=innerrun)
        Query.start()

    def onReset(self, event):
        wx.PostEvent(self, ResultEvent(['reset_data', 'do it']))

    def printLogger(self, msg):
        wx.PostEvent(self, ResultEvent(['logger', msg+'\n']))
        
    def updateDisplay(self, msg):
        if msg.topic[-1] == 'control':
            if msg.data in 'update button':
                self.runButton.Enable()

class MPLPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0), dpi=self.dpi)
        self.ax = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax_dict = None
        self.avg = []

        # Setup the toolbar
        self.toolbar = NavigationToolbar(self.canvas)

        # Do the layout
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.canvas.draw()

        # Observer of Notify events
        Publisher.subscribe(self.OnEventUpdate, MSG_NOTIFY_ROOT)

    def OnEventUpdate(self, msg):
        if msg.topic[-1] == 'plot_data':
            if len(self.avg) == 0:
                self.avg.append(msg.data)
            else:
                i = len(self.avg)
                self.avg.append((msg.data + i*self.avg[i-1])/(i+1))
            self.OnPlotUpdate()
        if msg.topic[-1] == 'reset_data':
            self.avg =[]
            self.ax.clear()
            self.canvas.draw()

    def OnPlotUpdate(self):
        if not self.ax:
            self.ax = self.fig.add_subplot(111)
        # self.x_data = np.arange(len(self.avg))
        # self.y_data = np.array(self.avg)
        self.plot_data = self.ax.plot(range(len(self.avg)), self.avg, color='b')
        
        self.canvas.draw()

class MPLPanel2(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel2, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0), dpi=self.dpi)
        self.ax = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax_dict = None
        self.data = []

        # Setup the toolbar/statustextctrl
        self.toolbar = NavigationToolbar(self.canvas)
        self.statusctrl = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_RIGHT)
        

        # Do the layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.toolbar, 0)
        hbox.Add(self.statusctrl, 1)
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(hbox, 0, flag=wx.EXPAND|wx.GROW|wx.ALL)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.canvas.draw()

        # Bind mouse events to mplcanvas
        # Note that event is a MplEvent
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)

        # Add the statusbar
        # self.statusBar = wx.StatusBar(self)
        # self.statusBar.SetFieldsCount(1)
        # self.SetStatusBar(self.statusBar)


        # Observer of Notify events
        Publisher.subscribe(self.OnEventUpdate, MSG_NOTIFY_ROOT)
        
    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusctrl.SetValue("x= " + str(x) + "  y=" +str(y))

    def ChangeCursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

    def OnEventUpdate(self, msg):
        if msg.topic[-1] == 'plot_data':
            self.data.append(msg.data)
            self.OnPlotUpdate()
        if msg.topic[-1] == 'reset_data':
            self.data = []
            self.ax.clear()
            self.canvas.draw()
                     
    def OnPlotUpdate(self):
        if not self.ax:
            self.ax = self.fig.add_subplot(111)
        # self.x_data = np.arange(len(self.data))
        # self.y_data = np.array(self.data)
        self.plot_data = self.ax.plot(range(len(self.data)), self.data, color='b')

        self.canvas.draw()

class LoggerCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(LoggerCtrl, self).__init__(*args, **kwargs)
        # Observer of Notify events
        Publisher.subscribe(self.updateDisplay, MSG_NOTIFY_ROOT)

    def updateDisplay(self, msg):
        """
        Receives data from thread and updates the display
        """
        if msg.topic[-1] == 'logger':
            t = msg.data
            self.AppendText(t)

class StreamFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(StreamFrame, self).__init__(*args, **kwargs)
        self._mgr = wx.aui.AuiManager(self)
        mplpanel = MPLPanel(self)
        mplpanel2 = MPLPanel2(self)
        loggerctrl = LoggerCtrl(self, size=wx.Size(800, 100), \
                                    style=wx.TE_MULTILINE|wx.TE_READONLY)
        controlpanel = ControlPanel(self, size=wx.Size(250, 400))
        
        self._mgr.AddPane(controlpanel,\
                          wx.aui.AuiPaneInfo().Caption('Controls').
                          Left().MinimizeButton(True))
        self._mgr.AddPane(mplpanel2, wx.aui.AuiPaneInfo().Caption('Plot Canvas').
                           Center().MinimizeButton(True).MaximizeButton(True))
        self._mgr.AddPane(mplpanel, wx.aui.AuiPaneInfo().Caption('AVG Plot').
                          Center().MaximizeButton(True))
        self._mgr.AddPane(loggerctrl, wx.aui.AuiPaneInfo().Caption('Notifications').
                          Bottom().MinimizeButton(True).MaximizeButton(True))
        self._mgr.Update()

class StreamApp(wx.App):
    def OnInit(self):
        self.frame = StreamFrame(None, title="HoloStream", size=(1000, 700))
        self.frame.Show(True)
        # Initialize the notification system
        self.notify = Notifier()
        # Make the app the subscriber to our made up ResultEvents
        EVT_RESULT(self, self.ReportNotifier)
        return True                    

    def GetNotify(self):
        return self.notify

    def ReportNotifier(self, notifydict):
        '''
        @param: notifydata is a dictionary, where each key
        is a differnt subscriber of the notification system
        to send its value (the data) to 
        '''
        data = notifydict.data
        if type(data) == dict:
            for key in data.keys():
                self.notify.SetValue(key, data[key])
        else:
            self.notify.SetValue(data[0], data[1])
        return

class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init
        
    def next(self):
        self._recalc_data()
        return self.data
    
    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8: 
            # attraction to the initial value
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta

if __name__ == '__main__':
    app = StreamApp()
    app.MainLoop()


