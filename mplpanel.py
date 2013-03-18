import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.cm as cm
import matplotlib.dates as mdates
import datetime as dt
import csdplotsettingspanel as csdsett
import rmsplotsettingspanel as rmssett
from wx.lib.pubsub import Publisher as pub
from collections import defaultdict
import numpy as np

class MPLPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0), dpi=self.dpi)
        self.ax1 = None
        self.ax2 = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.data = []

        # Setup the toolbar/statustextctrl
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.dynamic_update()
        self.testButton = wx.Button(self.toolbar, label='Pause')
        self.toolbar.AddControl(self.testButton)
        self.toolbar.AddSeparator()
        self.statusctrl = wx.StaticText(self.toolbar, style=wx.TE_READONLY, \
                                          size=wx.Size(300,25))
        self.toolbar.AddControl(self.statusctrl)
        
        # Do the layout
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, flag=wx.EXPAND|wx.GROW|wx.ALL)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.canvas.draw()


class CSDPlotPresenter(object):
    '''
    Will be responsible for handling the data (putting it into ax instances)
    and feeding it to the plot canvas. Can also capture mouse events (clicks
    for specifying region, etc).

    ~Also handles the plot settings toolbar and its presenter~
    Settings panel and canvas still need to be added to the AUI manager in the
    frame presenter, otherwise they will appear floating in the corner

    **Note**
    This presenter should not have knowledge of its caption and/or placement,
    or whether or not there are other similar presenters, this is handled in the
    view or frame presenter.
    '''
    def __init__(self, frame):
        self.frame = frame
        self.canvas = MPLPanel(self.frame)
        self.current_available_channels = []
        self.csd_data = {}
        self.phase_data = {}
        self.subscribed_channels = []
        self.plot_dict = {}
        self.run_info = None
        self.y_label = None
        self.x_label = None
        self.f_samp = None
        self.NFFT = None
        self.title = ''
        self.grid = None
        self.legend = None
        self.showphase = False
        self.update_state = True
        # Create settings toolbar presenter
        self.settingspresenter = csdsett.CSDSettPresenter(self.frame)
        self.settings = self.settingspresenter.panel
        # Bind update button of the settings Panel
        pub.subscribe(self.update_channels, 'available_channels')
        pub.subscribe(self.process_data, 'avg_data')
        pub.subscribe(self.process_run_info, 'run_info')
        # Bind mouse events to mplcanvas
        # Note that event is a MplEvent
        self.canvas.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        # Bind plot button
        self.settings.Bind(wx.EVT_BUTTON, self.on_update_button)
        self.canvas.Bind(wx.EVT_BUTTON, self.on_plot_button)

    def on_plot_button(self, event):
        if self.update_state:
            self.canvas.testButton.SetLabel('Resume')
        else:
            self.canvas.testButton.SetLabel('Pause')
        self.toggle_update_state()
        return

    def toggle_update_state(self):
        self.update_state = not self.update_state
        return

    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            if len(self.csd_data) > 0:
                x, y = event.xdata, event.ydata
                self.canvas.statusctrl.SetLabel("x= " + str(x) + 
                                                "  y=" + str(y)
                                                )
            else:
                pass

    def process_run_info(self, event):
        """Method to set label values to be shown in plot based on run_info"""
        if self.run_info == None:
            self.run_info = event.data
            self.y_label = self.run_info['yunits']
            self.x_label = self.run_info['xunits']
            self.f_samp = self.run_info['ADC_settings']['f_samp']
            self.NFFT = self.run_info['NFFT']
        else:
            pass

    def process_data(self, event):
        data_dict = event.data[1]
        phase_dict = event.data[2]
        if data_dict is None:
            pass
        else:
            self.csd_data.clear()
            self.phase_data.clear()
            for key in data_dict.keys():
                if str(key) in self.subscribed_channels:
                    self.csd_data[str(key)] = data_dict[key]
                    self.phase_data[str(key)] = phase_dict[key]
        self.plot_update()

    def plot_update(self):
        if not self.showphase:
            if self.canvas.ax1 is None:
                self.canvas.ax1 = self.canvas.fig.add_subplot(111)
            else:
                self.canvas.ax1.clear()
                for i, channel in enumerate(self.csd_data.keys()):
                    # Need to change this once actual data is coming in!!
                    x_data_len = len(self.csd_data[channel])
                    f_nyquist = self.f_samp/2
                    x_data = np.linspace(1, f_nyquist, x_data_len)
                    self.plot_dict[channel] = \
                        self.canvas.ax1.plot(x_data, 
                                             abs(self.csd_data[channel])**.5, 
                                             '-', label=channel
                                             )
                if len(self.csd_data) > 0:
                    if self.legend:
                        self.canvas.ax1.legend(loc='upper right')
                    if self.grid is not None:
                        self.canvas.ax1.grid(self.grid, which='both')
                    self.canvas.ax1.set_title(self.title)
                    self.canvas.ax1.set_ylabel(self.y_label)
                    self.canvas.ax1.set_xlabel(self.x_label)
                    self.canvas.ax1.set_yscale('log')
                if self.update_state:
                    self.canvas.canvas.draw()
        elif self.showphase:
            if self.canvas.ax1 is None:
                self.canvas.ax1 = self.canvas.fig.add_subplot(211)
            if self.canvas.ax2 is None:
                self.canvas.ax2 = self.canvas.fig.add_subplot(212)
            else:
                self.canvas.ax1.clear()
                self.canvas.ax2.clear()
                for channel in self.csd_data.keys():
                    # Need to change this once actual data is coming in!!
                    x_data_len = len(self.csd_data[channel])
                    # divide f_nyquist by 10**6 to make units correct
                    f_nyquist = self.f_samp/2
                    x_data = np.linspace(1, f_nyquist, x_data_len)
                    self.plot_dict[channel] = \
                        [self.canvas.ax1.plot(x_data, 
                                             abs(self.csd_data[channel])**.5,
                                             '-', label=channel
                                             ),
                         self.canvas.ax2.plot(x_data, 
                                              self.phase_data[channel], 
                                              '-', label=channel
                                              )
                         ]
                if len(self.csd_data) > 0:
                    if self.legend:
                        self.canvas.ax1.legend(loc='upper right')
                    if self.grid is not None:
                        self.canvas.ax1.grid(self.grid, which='both')
                        self.canvas.ax2.grid(self.grid, which='both')
                    self.canvas.ax1.set_title(self.title)
                    self.canvas.ax1.set_ylabel(self.y_label)
                    self.canvas.ax2.set_ylabel('Phase (Deg)')
                    self.canvas.ax2.set_xlabel(self.x_label)
                    self.canvas.ax1.set_yscale('log')
                    self.canvas.ax2.set_ylim((-180, 180))
                    y2tick_val = [-180., -135., -90., -45., 0., 45., 90., 135., 180.]
                    self.canvas.ax2.set_yticks(y2tick_val)
                    self.canvas.fig.subplots_adjust(hspace=.3)
                if self.update_state:
                    self.canvas.canvas.draw()

    def update_plot_settings(self, report_dict):
        self.subscribed_channels = report_dict['checked_view_options'].values()
        self.title = report_dict['title']
        self.grid = report_dict['grid']
        self.legend = report_dict['legend']
        # check if showphase value has changed:
        if report_dict['phase']: 
            self.canvas.fig.axes[0].change_geometry(2,1,1)
        if not report_dict['phase']:
            if len(self.canvas.fig.axes) > 1:
                # Need to figure out how clear phase plot
                self.canvas.fig.delaxes(self.canvas.fig.axes[1])
                self.canvas.fig.axes[0].change_geometry(1,1,1)
        self.showphase = report_dict['phase']
        pub.sendMessage('logger', 'Plot settings updated')        

    def on_update_button(self, event):
        if event.GetEventObject() == self.settings.updateButton:
            report_dict = self.settings.report_field_values()
            self.update_plot_settings(report_dict)

    def update_channels(self, event):
        if self.current_available_channels == event.data:
            pass
        else:
            self.settings.set_view_options(event.data)
            self.current_available_channels = event.data

    def unsubscribe_all(self):
        pub.unsubscribe(self.update_channels)
        pub.unsubscribe(self.process_data)

class RMSPlotPresenter(object):
    '''
    Will differ greatly from CSDPlotPresenter in how it handles the incoming data
    '''
    def __init__(self, frame):
        self.frame = frame
        self.canvas = MPLPanel(self.frame)
        self.current_available_channels = []
        self.subscribed_channels = []
        self.rms_data = defaultdict(list)
        self.times_data = defaultdict(list)
        self.plot_dict = {}
        # Attributes related to selecting a region of time
        self.t1_sel = None
        self.t2_sel = None
        # Attributes related to plot settings
        self.run_info = None
        self.y_label = None
        self.title = None
        self.grid = None
        self.legend = None
        self.dynamic_x = None
        self.x_min = None
        self.x_max = None
        self.current_x_max = None
        self.update_state = True
        # Create settings toolbar presenter
        self.settingspresenter = rmssett.RMSSettPresenter(self.frame)
        self.settings = self.settingspresenter.panel
        # Bind update button of the settings Panel
        self.settings.Bind(wx.EVT_BUTTON, self.on_button_press)
        pub.subscribe(self.update_channels, 'available_channels')
        pub.subscribe(self.process_data, 'data_dict')
        pub.subscribe(self.process_run_info, 'run_info')
        # Bind mouse events to mplcanvas
        # Note that event is a MplEvent
        self.canvas.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        # Bind button
        self.canvas.Bind(wx.EVT_BUTTON, self.on_button)

    def on_button(self, event):
        if self.update_state:
            self.canvas.testButton.SetLabel('Resume')
        else:
            self.canvas.testButton.SetLabel('Pause')
        self.toggle_update_state()

    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            if len(self.times_data) > 0:
                x, y = event.xdata, event.ydata
                xformat = dt.datetime.strftime(mdates.num2date(x), '%d-%b-%Y-%H:%M')
                self.canvas.statusctrl.SetLabel("x= " + xformat + 
                                                "  y=" + str(y)
                                                )
            else:
                pass

    def toggle_update_state(self):
        self.update_state = not self.update_state
        return

    def set_select_mode_on(self):
        self.cid = self.canvas.canvas.mpl_connect('button_press_event', self.on_click)
        self.rid = self.canvas.canvas.mpl_connect('button_release_event', \
                                                      self.on_release)

    def set_select_mode_off(self):
        self.canvas.canvas.mpl_disconnect(self.cid)
        self.canvas.canvas.mpl_disconnect(self.rid)
        self.settings.selectButton.Enable()
        
    def on_release(self, event):
        if event.xdata is not None:
            self.t2_sel = event.xdata
            t1fmt = dt.datetime.strftime(mdates.num2date(self.t1_sel),\
                                             '%d-%b-%Y-%H:%M:%S')
            t2fmt = dt.datetime.strftime(mdates.num2date(self.t2_sel),\
                                             '%d-%b-%Y-%H:%M:%S')
            logmsg = 'Selected the region: t1 = '+str(t1fmt)+\
                ', t2 = '+str(t2fmt)
            pub.sendMessage('logger', logmsg)
            self.set_select_mode_off()

    def on_click(self, event):
        if event.xdata is not None:
            self.t1_sel = event.xdata
            self.canvas.ax1.axvline(x=self.t1_sel, color='r')
            self.canvas.canvas.draw()
    
    def process_run_info(self, event):
        """Method to set label values to be shown in plot based on run_info"""
        if self.run_info == None:
            self.run_info = event.data
            self.y_label = self.run_info['yunits']
        else:
            pass

    def process_data(self, event):
        timestamp = event.data[0]
        if self.current_x_max is None:
            self.current_x_max = timestamp
        if timestamp > self.current_x_max:
            self.current_x_max = timestamp
        data_dict = event.data[1]
        if data_dict is None:
            pass
        else:
            for key in data_dict.keys():
                if str(key) in self.subscribed_channels:
                    self.rms_data[str(key)].append(np.sum(abs(data_dict[key]))**.5)
                    self.times_data[str(key)].append(timestamp)
        self.plot_update()

    def plot_update(self):
        if self.canvas.ax1 is None:
            self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        else:
            self.canvas.ax1.clear()
            for channel in self.rms_data.keys():
                self.plot_dict[channel] = \
                    self.canvas.ax1.plot_date(self.times_data[channel], 
                                            self.rms_data[channel], '-',
                                                 label=str(channel))
            # Plot Settings Logic
            if len(self.times_data) > 0:
                if self.legend is not None:
                    if self.legend:
                        self.canvas.ax1.legend(loc='upper right')
                if self.grid is not None:
                    self.canvas.ax1.grid(self.grid, which='both')
                if self.title is not None:
                    self.canvas.ax1.set_title(self.title)
                if self.dynamic_x is not None:
                    if self.x_min is None:
                        self.set_x_lim()
                    if self.dynamic_x is False:
                        if self.current_x_max > self.x_max:
                            self.x_max += dt.timedelta(seconds=60)
                        self.canvas.ax1.set_xlim([self.x_min, self.x_max])
            self.canvas.ax1.set_ylabel(self.y_label)
            self.canvas.fig.autofmt_xdate()
            self.canvas.ax1.set_yscale('log')
            if self.update_state:
                self.canvas.canvas.draw()

    def set_x_lim(self):
        if self.x_min is None:
            self.x_min = dt.datetime.now()
        for key in self.times_data.keys():
            if self.x_min < self.times_data[key][0]:
                self.x_min = self.times_data[key][0]
        self.x_max = self.x_min + dt.timedelta(seconds=10)

    def on_button_press(self, event):
        if event.GetEventObject() == self.settings.updateButton:
            report_dict = self.settings.report_field_values()
            self.update_plot_settings(report_dict)
        if event.GetEventObject() == self.settings.selectButton:
            self.set_select_mode_on()
            self.settings.selectButton.Disable()

    def update_plot_settings(self, report_dict):
        self.subscribed_channels = report_dict['checked_view_options'].values()
        #check for different subscribed channels
        diff_keys = set(self.rms_data.keys()) - \
            set(self.subscribed_channels)
        if (len(diff_keys) > 0) & (len(self.rms_data) > len(self.subscribed_channels)):
            for key in diff_keys:
                del(self.rms_data[key])
                del(self.times_data[key])
        self.title = report_dict['title']
        self.grid = report_dict['grid']
        self.legend = report_dict['legend']
        self.dynamic_x = report_dict['dynamicxaxis']
        pub.sendMessage('logger', 'Plot settings updated')

    def update_channels(self, event):
        if self.current_available_channels == event.data:
            pass
        else:
            self.settings.set_view_options(event.data)
            self.current_available_channels = event.data

    def unsubscribe_all(self):
        pub.unsubscribe(self.update_channels)
        pub.unsubscribe(self.process_data)

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.plotpresenter = CSDPlotPresenter(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 200), \
                                       style=wx.TE_MULTILINE)
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textCtrl').
                              Caption('TextCtrl').Bottom())
            self._mgr.AddPane(self.plotpresenter.canvas, aui.AuiPaneInfo().
                              Name('plotcanvas1').
                              Caption('Plot Canvas 1').Center())
            self._mgr.AddPane(self.plotpresenter.settings, aui.AuiPaneInfo().
                              Name('plotcanvas1settings').
                              Caption('Plot 1 Settings').Left())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Plot Canvas & Settings Test", \
                        size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()

