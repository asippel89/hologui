#!/usr/bin/python

#hologui.py

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
import matplotlib.dates as mdates
import time
from collections import defaultdict
import datetime as dt

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
        self.channels = ['T-IFO', 'L-IFO', 'Outside Temp']
        self.start_times = ['Last Week', 'Yesterday']
        self.end_times = ['Now']
        self.createControls()
        self.bindEvents()
        self.doLayout()
        
        Publisher.subscribe(self.updateDisplay, MSG_NOTIFY_ROOT)        

    def createControls(self):
        self.runButton = wx.Button(self, label="Run")
        self.titleLabel = wx.StaticText(self, label="Title:")
        self.titleTextCtrl = wx.TextCtrl(self, value="Enter plot title here")
        self.channelLabel = wx.StaticText(self,
            label="Channels:")
        self.channelComboBox = wx.ComboBox(self, choices=self.channels,
            style=wx.CB_DROPDOWN, value="T-IFO")
        self.starttimeLabel = wx.StaticText(self, label="Start Time:")
        self.starttimeComboBox = wx.ComboBox(self, choices=self.start_times,
            style=wx.CB_DROPDOWN, value="Yesterday")
        self.endtimeLabel = wx.StaticText(self, label="End Time:")
        self.endtimeComboBox = wx.ComboBox(self, choices=self.end_times,
            style=wx.CB_DROPDOWN, value="Now")
        self.verboseCheckBox = wx.CheckBox(self, label="Do you want verbose output?")
        self.verboseCheckBox.SetValue(True)
        self.gridCheckBox = wx.CheckBox(self, label="Show Grid?")
        self.gridCheckBox.SetValue(False)
                                          

    def doLayout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=11, cols=2, vgap=10, hgap=10)

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
                 (self.channelLabel, noOptions),
                 emptySpace,
                 (self.channelComboBox, expandOption),
                  emptySpace,
                 (self.starttimeLabel, noOptions),
                 emptySpace,
                 (self.starttimeComboBox, expandOption),
                 emptySpace,
                 (self.endtimeLabel, noOptions),
                 emptySpace,
                 (self.endtimeComboBox, expandOption),
                 emptySpace,
                 (self.verboseCheckBox, noOptions),
                 emptySpace,
                 (self.gridCheckBox, noOptions),
                 emptySpace,
                 (self.runButton, dict(flag=wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)
        self.SetSizer(gridSizer)

    def bindEvents(self):
        for control, event, handler in \
            [(self.runButton, wx.EVT_BUTTON, self.onRun),
             (self, wx.EVT_TEXT, self.onTextEntered),
             (self, wx.EVT_COMBOBOX, self.onComboChanged),
             (self, wx.EVT_CHECKBOX, self.onCheckboxChanged)]:
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
        # notify = wx.GetApp().GetNotify()
        # TestThread(self)
        # notify.SetValue('logger', "Thread started!\n")
        # self.runButton.Disable()

        Title = self.titleTextCtrl.GetValue()
        if Title == 'Enter plot title here':
            Title = ''
        # wx.PostEvent(self, ResultEvent(['mpl_canvas', str(Title)]))
        Channel = str(self.channelComboBox.GetValue())
        if Channel == 'T-IFO':
            Channel_list = ['E:TCIP', 'E:TNIP0', 'E:TNIP1', 'E:TNESIP', 'E:TEIP0',\
                                'E:TEIP1', 'E:TEESIP']
        elif Channel == 'L-IFO':
            Channel_list = ['E:LCIP', 'E:LNIP0', 'E:LNIP1', 'E:LNESIP', 'E:LEIP0',\
                                'E:LEIP1', 'E:LEESIP']
        elif Channel == 'Test':
            Channel_list = ['G:OUTTMP', 'E:TCIP']
        else:
            Channel_list = Channel.split(', ')
        Start_time = str(self.starttimeComboBox.GetValue())
        if Start_time == 'Last Week':
            Start_time = 'Last_Week'
            start_fmt = self.get_date(7)
        elif Start_time == 'Yesterday':
            start_fmt = self.get_date(1)
        else:
            start_fmt = Start_time
        End_time = str(self.endtimeComboBox.GetValue())
        if End_time == 'Now':
            end_fmt = self.get_date()
        Verbose = self.verboseCheckBox.GetValue()
        Grid = self.gridCheckBox.GetValue()
        mplcanvas_msg_dict = dict([('title', Title), ('start', start_fmt), \
                                      ('end', end_fmt), ('grid', Grid)])
        wx.PostEvent(self, ResultEvent(['mpl_canvas', mplcanvas_msg_dict]))
        #------ Not sure why the following gives a type error for the thread.start()
        #------ method...
        # query = ACNETQuery(self, Channel_list, Start_time, End_time)
        # query.start()
        def innerrun():
            query = p2acnet.P2ACNET(Channel_list, Start_time, End_time, \
                                        verbose=Verbose, \
                                        print_method=self.printLogger\
                                        )
            info_dict = query.get_group_info()
            wx.PostEvent(self, ResultEvent(['mpl_canvas_info_dict', info_dict]))
            data = query.get_group_data()
            wx.PostEvent(self, ResultEvent(['plot_data', data]))
        Query = threading.Thread(target=innerrun)
        Query.start()
        self.runButton.Disable()
        self.printLogger('Query Started')

    def get_date(self, days='Today'):
        '''
        This method returns today's date/time formatted according to the ACNET time
        query standard. This helps in plot labeling.
        '''
        today = dt.datetime.today()
        if days == 'Today':
            date_fmt = today.strftime("%d-%b-%Y-%H:%M")
        else:
            interval = dt.timedelta(days)
            date_raw = today - interval
            date_fmt = date_raw.strftime("%d-%b-%Y-%H:%M")
        return date_fmt

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
        self.fig = Figure((4.0, 5.0), dpi=self.dpi)
        self.ax = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax_dict = None

        # Setup the toolbar
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.AddSeparator()
        self.statusctrl = wx.TextCtrl(self.toolbar, style=wx.TE_READONLY, \
                                          size=wx.Size(300,25))
        self.toolbar.AddControl(self.statusctrl)

        # Bind mouse events to mplcanvas
        # Note that event is a MplEvent
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)

        # Do the layout
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.canvas.draw()

        # Observer of Notify events
        Publisher.subscribe(self.OnPlotUpdate, MSG_NOTIFY_ROOT)

    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            x, y = event.xdata, event.ydata
            xformat = dt.datetime.strftime(mdates.num2date(x), '%d-%b-%Y-%H:%M')
            if np.log10(y) < -5:
                yformat = "%e" % y
            else:
                yformat = "%f" % y
            self.statusctrl.SetValue("x=" +xformat + " y=" +yformat)

    def ChangeCursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

    def OnPlotUpdate(self, msg):
        if msg.topic[-1] == 'plot_data':
            # if not self.ax:
            #     self.ax = self.fig.add_subplot(111)
            if self.ax_dict != None:
                for i in self.ax_dict.keys():
                    self.ax_dict[i].clear()
                self.fig.clear()
            data_dict = msg.data
            #-----Decide how many subplots based on units-----#
            units_dict = defaultdict(list)
            for (channel, info_array) in self.info_dict.items():
                units_dict[info_array[1]].append(channel)
            num_units = len(units_dict)
            #------Try making a dictionary of axes instances--#
            self.ax_dict = {}
            #-----Make subplot for each unit------------------#
            for index, key in enumerate(units_dict):
                self.ax_dict[index] = self.fig.add_subplot(num_units, 1, index + 1)
                for channel in units_dict[key]:
                    data = data_dict[channel]
                    xdata = mdates.date2num(data[:,0])
                    ydata = data[:,1]
                    self.ax_dict[index].plot_date(xdata, ydata, '-', label=channel)
                    self.ax_dict[index].set_ylabel(key)
                if index == 0:
                    self.ax_dict[index].set_title(self.title)
                if 'TORR' in key:
                    self.ax_dict[index].set_yscale('log')
                self.ax_dict[index].legend(loc="best").get_frame().set_alpha(.5)
                if index == (num_units-1):
                    self.ax_dict[index].set_xlabel(str("T1 = "+ self.start+\
                                                           "      T2 = "+\
                                                           self.end))
                    self.ax_dict[index].grid(b=self.grid, which='both')
                    # Grid won't show without newest version of matplotlib
            self.fig.autofmt_xdate()
            self.canvas.draw()
            wx.PostEvent(self, ResultEvent(['control', 'update button']))
            wx.PostEvent(self, ResultEvent(['logger', 'Query Finished\n']))
        if msg.topic[-1] == 'mpl_canvas_info_dict':
            self.info_dict = msg.data
        if msg.topic[-1] == 'mpl_canvas':
            self.title = msg.data['title']
            self.start = msg.data['start']
            self.end = msg.data['end']
            self.grid = msg.data['grid']

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
            if isinstance(t, int):
                self.AppendText("Time:%s seconds\n" % t)
            else:
                self.AppendText(t)

class P2Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(P2Frame, self).__init__(*args, **kwargs)
        self._mgr = wx.aui.AuiManager(self)
        mplpanel = MPLPanel(self)
        loggerctrl = LoggerCtrl(self, size=wx.Size(800, 100), \
                                    style=wx.TE_MULTILINE|wx.TE_READONLY)
        controlpanel = ControlPanel(self, size=wx.Size(250, 400))
        
        self._mgr.AddPane(controlpanel,\
                          wx.aui.AuiPaneInfo().Caption('P2ACNET Controls').
                          Left().MinimizeButton(True))
        self._mgr.AddPane(mplpanel, wx.aui.AuiPaneInfo().Caption('Plot Canvas').
                          Center().MinimizeButton(True).MaximizeButton(True))
        self._mgr.AddPane(loggerctrl, wx.aui.AuiPaneInfo().Caption('Notifications').
                          Bottom().MinimizeButton(True).MaximizeButton(True))
        self._mgr.Update()

class P2App(wx.App):
    def OnInit(self):
        self.frame = P2Frame(None, title="P2ACNET GUI", size=(1000, 700))
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


if __name__ == '__main__':
    app = P2App()
    app.MainLoop()


