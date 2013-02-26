#!/usr/bin/python

#csdframe.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
import conn_settings_view as consett
import mplpanel
import connsettingstoolbar as connTB
import loggerctrl
import csdviewtoolbar
from wx.lib.pubsub import Publisher as pub

class CSDFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(CSDFrame, self).__init__(*args, **kwargs)
        self._mgr = aui.AuiManager(self)
        self.presenter_dict = {}
        # Variables for number of plot tabs of each type
        self.num_rms_plots = 0
        self.num_csd_plots = 0
        self.tab_settings_dict = {}

        # Initiate Presenters
        self.connsettpresenter = connTB.ConnSettingsPresenter(self)

        # Create Center Plot Notebook
        self.auinb = aui.AuiNotebook(self, size=wx.Size(500,300))
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.on_page_changing)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)

        # Create other View Objects
        self.logger = loggerctrl.LoggerCtrl(self, size=wx.Size(800, 100), \
                                     style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.conntoolbar = self.connsettpresenter.tb
        self.csdviewtoolbar = csdviewtoolbar.Toolbar(self, -1, wx.DefaultPosition,\
                                                     wx.DefaultSize, \
                                                     agwStyle=aui.AUI_TB_OVERFLOW|\
                                                     aui.AUI_TB_TEXT|\
                                                     aui.AUI_TB_HORZ_TEXT)
                                                         
        self.Bind(wx.EVT_BUTTON, self.on_button)
        # Add Initial View Objects to Manager
        self._mgr.AddPane(self.conntoolbar, aui.AuiPaneInfo().Name('connTB').
                          Caption('Connection Settings').
                          ToolbarPane().Bottom())
        self._mgr.AddPane(self.logger, aui.AuiPaneInfo().\
                              Caption('Notifications').Bottom().\
                              MaximizeButton().MinimizeButton())
        self._mgr.AddPane(self.auinb, aui.AuiPaneInfo().\
                              Caption('Plots').Center().MaximizeButton())
        self._mgr.AddPane(self.csdviewtoolbar, aui.AuiPaneInfo().\
                              Caption('CSD View Options').\
                              ToolbarPane().Bottom())

        # Populate with a couple initial plot panels
        self.create_plot_tab('RMS')
        self.create_plot_tab('CSD')
        self._mgr.Update()

    def on_page_close(self, event):
        active_tab = self.auinb.GetSelection()
        active_tab_label = self.auinb.GetPageText(active_tab)
        # Unsubscribe pane's presenter from pubsub
        # using presenter_dict
        canvas = self.auinb.GetCurrentPage() # this is the actual plot canvas
        presenter = self.presenter_dict[canvas]
        presenter.unsubscribe_all()
        self._mgr.ClosePane(self._mgr.
                            GetPane(self.tab_settings_dict[active_tab_label]))
        self._mgr.Update()

    def on_page_changing(self, event):
        active_tab_index = self.auinb.GetSelection()
        if active_tab_index == -1:
            pass
        else:
            active_tab_label = self.auinb.GetPageText(active_tab_index)
            self._mgr.GetPane(self.tab_settings_dict[active_tab_label]).Hide()
            self._mgr.Update()

    def on_page_changed(self, event):
        new_active_tab_index = self.auinb.GetSelection()
        new_active_tab_label = self.auinb.GetPageText(new_active_tab_index)
        self._mgr.GetPane(self.tab_settings_dict[new_active_tab_label]).Show()
        self._mgr.Update()
    
    def on_button(self, event):
        if event.GetEventObject() == self.csdviewtoolbar.addCSDButton:
            self.create_plot_tab('CSD')
        else:
            self.create_plot_tab('RMS')

    def create_plot_tab(self, plot_type):
        if 'RMS' in plot_type:
            self.num_rms_plots += 1
            rmsplotpresenter = mplpanel.RMSPlotPresenter(self)
            canvas = rmsplotpresenter.canvas
            settings = rmsplotpresenter.settings
            plotlabel = 'RMS Plot '+str(self.num_rms_plots)
            settingslabel = 'rmssett'+str(self.num_rms_plots)
            # add to presenter_dict
            self.presenter_dict[canvas] = rmsplotpresenter
            self.tab_settings_dict[plotlabel] = settingslabel
            self.auinb.AddPage(canvas, plotlabel, \
                                   select=True)
            self._mgr.AddPane(settings, aui.AuiPaneInfo().
                              Name(settingslabel).
                              Caption(plotlabel+' Settings').
                              Left().MinimizeButton())
            
            self._mgr.Update()
        if 'CSD' in plot_type:
            self.num_csd_plots += 1
            csdplotpresenter = mplpanel.CSDPlotPresenter(self)
            canvas = csdplotpresenter.canvas
            settings = csdplotpresenter.settings
            plotlabel = 'CSD Plot ' +str(self.num_csd_plots)
            settingslabel = 'csdsett'+str(self.num_csd_plots)
            # add to presenter_dict
            self.presenter_dict[canvas] = csdplotpresenter
            self.tab_settings_dict[plotlabel] = settingslabel
            self.auinb.AddPage(canvas, plotlabel,\
                                   select=True)
            self._mgr.AddPane(settings, aui.AuiPaneInfo().
                              Name(settingslabel).
                              Caption(plotlabel+' Settings').
                              Left().MinimizeButton())
            self._mgr.Update()

if __name__ == '__main__':
    import time

    app = wx.App(False)
    frame = CSDFrame(None, title='CSD View', size=(1000,700))
    frame.Show(True)
    app.MainLoop()
