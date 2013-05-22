import wx
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.cm as cm
import matplotlib.dates as mdates
import datetime as dt
from wx.lib.pubsub import Publisher as pub
from collections import defaultdict
import numpy as np

class CSDPresenter(object):
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
    def __init__(self, axes_channel_dict):
        self.frame = frame
        self.canvas = MPLPanel(self.frame)
        self.current_available_channels = []
        pub.subscribe(self.update_channels, 'available_channels')
        pub.subscribe(self.process_data, 'data_dict')
        pub.subscribe(self.process_run_info, 'run_info')

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
                    self.canvas.ax1.plot(x_data, 
                                             abs(self.csd_data[channel])**.5,
                                             '-', label=channel
                                             )
                    self.canvas.ax2.plot(x_data, 
                                         self.phase_data[channel], 
                                         '-', label=channel
                                         )
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
                    y2tick_val = [-180., -90., 0., 90., 180.]
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
