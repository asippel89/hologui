#!/usr/bin/python

#avgplotsettingspanel.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
from wx.lib.pubsub import Publisher as pub

RB_View_Options = ['x00', 'x01', 'x02', 'x03', '', 'x11', 'x12', 'x13', '', '', 'x22',\
                       'x23', '', '', '', 'x33']

class AVGPlotSettingsPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(AVGPlotSettingsPanel, self).__init__(*args, **kwargs)
        self.View_Options = []
        
        self.create_items()
        self.do_layout()

    def create_items(self):
        self.viewoptionsLabel = wx.StaticText(self, label="View which X-Spectra RMS?")
        self.viewoptionsCheckLB = wx.CheckListBox(self, -1, wx.DefaultPosition,\
                                                      (70,235), \
                                                      self.View_Options)
        self.titleLabel = wx.StaticText(self, label="Title:")
        self.titleCtrl = wx.TextCtrl(self, value="")
        self.gridCheckBox = wx.CheckBox(self, label="Show Grid?")
        self.gridCheckBox.SetValue(False)
        self.legendCheckBox = wx.CheckBox(self, label="Show Legend?")
        self.dynamicxaxisCheckBox = wx.CheckBox(self, label="Dynamic X-Axis?")
        self.updateButton = wx.Button(self, label="Update")
                                                  
    def do_layout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=9, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 emptySpace,
                 (self.viewoptionsLabel, expandOption),
                 emptySpace, 
                 (self.viewoptionsCheckLB, noOptions),
                 emptySpace,
                 (self.titleLabel, expandOption),
                 emptySpace,
                 (self.titleCtrl, expandOption),
                 emptySpace,
                 (self.gridCheckBox, expandOption),
                 emptySpace,
                 (self.legendCheckBox, expandOption),
                 emptySpace,
                 (self.dynamicxaxisCheckBox, expandOption),
                 emptySpace,
                 (self.updateButton, expandOption),
                 emptySpace]:
            gridSizer.Add(control, **options)

        # Finally, add a horizontal sizer to give extra space
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer((10, 0))
        hsizer.Add(gridSizer)
            
        self.SetSizer(hsizer)

    def set_view_options(self, channel_list):
        self.viewoptionsCheckLB.Clear()
        for element in channel_list:
            self.viewoptionsCheckLB.Append(element)
        return

    def get_checked_view_options(self):
        checked_view_options_indexes = self.viewoptionsCheckLB.GetChecked()
        checked_view_options_strings = self.viewoptionsCheckLB.GetCheckedStrings()
        checked_dict = dict(zip(checked_view_options_indexes, \
                                    checked_view_options_strings))
        return checked_dict

    def report_field_values(self):
        report_dict = {}
        checked_dict = self.get_checked_view_options()
        report_dict['checked_view_options'] = checked_dict
        report_dict['title'] = self.titleCtrl.GetValue()
        report_dict['grid'] = self.gridCheckBox.IsChecked()
        report_dict['legend'] = self.legendCheckBox.IsChecked()
        report_dict['dynamicxaxis'] = self.dynamicxaxisCheckBox.IsChecked()
        return report_dict

class AVGSettPresenter(object):
    def __init__(self, frame):
        self.frame = frame
        self.panel = AVGPlotSettingsPanel(self.frame, size = wx.Size(200,500))
        
        # Event Bindings
        self.panel.Bind(wx.EVT_BUTTON, self.on_button)

    def on_button(self, event):
        report_dict = self.panel.report_field_values()
        pub.sendMessage('logger', report_dict)

if __name__ == '__main__':

    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 300), \
                                       style=wx.TE_MULTILINE)
            self.testButton1 = wx.Button(self, label="Populate View Options")
            self.testButton2 = wx.Button(self, label="Get Checked Views")
            self.testButton3 = wx.Button(self, label="Load Form Test")
            self.Bind(wx.EVT_BUTTON, self.on_test_button)
            self.panel = AVGPlotSettingsPanel(self, size=wx.Size(300, 800))
            self._mgr.AddPane(self.panel, aui.AuiPaneInfo().Name('plotsettingspanel').
                              Caption('Plot Settings').
                              Left().MaximizeButton())
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.AddPane(self.testButton1, aui.AuiPaneInfo().Name('testButton1').
                              Caption('Test Button1').Bottom())
            self._mgr.AddPane(self.testButton2, aui.AuiPaneInfo().Name('testButton2').
                              Caption('Test Button2').Bottom())
            self._mgr.AddPane(self.testButton3, aui.AuiPaneInfo().Name('testButton3').
                              Caption('Test Button3').Bottom())
            self._mgr.Update()

        def on_test_button(self, evt):
            if evt.GetEventObject() == self.testButton1:
                self.panel.set_view_options(['x00', 'x01', 'x02', 'x03', 'x11', 'x12',\
                                                 'x13', 'x22', 'x23', 'x33'])
            if evt.GetEventObject() == self.testButton2:
                checked_options = self.panel.get_checked_view_options() 
                self.textCtrl.AppendText(str(checked_options)+'\n')
            if evt.GetEventObject() == self.panel.updateButton:
                self.textCtrl.AppendText(str(self.panel.report_field_values())+'\n')
            else:
                pass

    app = wx.App(False)
    frame = MyFrame(None, title="Plot Settings Test", size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()
