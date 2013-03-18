#!/usr/bin/python

#formgenerator.py

import wx
import json
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

setup_dict = {'fields': {'update_int': {'type': 'textCtrl', 'value': 0.5, 'label': 'Update Interval (sec)'}, 'fsamp': {'type': 'textCtrl', 'value': 100, 'label': 'Sampling Frequency (MegaSamples/sec)'}, 'noise_level': {'default': 'P_2kW_var_1s', 'choices': ['P_1W_var_1s', 'P_2kW_var_1s'], 'type': 'comboBox', 'label': 'Noise Level'}, 'NFFT': {'type': 'textCtrl', 'value': 4096, 'label': 'NFFT'}}, 'title': 'Simulation Settings'}


class Form(wx.Frame):

    def __init__(self, setup_dict, parent, *args, **kwargs):
        self.setup_dict = setup_dict
        self.field_gui_dict = {}
        super(Form, self).__init__(parent=parent, *args, **kwargs)
        self.create_items()
        self.do_layout()
        
    def create_items(self):
        self.titleLabel = wx.StaticText(self, label=self.setup_dict['title'])
        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.titleLabel.SetFont(font)
        for field, value_dict in self.setup_dict['fields'].items():
            label = wx.StaticText(self, label=value_dict['label'])
            if value_dict['type'] == 'textCtrl':
                ctrl = wx.TextCtrl(self, value=str(value_dict['value']))
                self.field_gui_dict[field] = {'label':label, 'ctrl':ctrl}
            if value_dict['type'] == 'comboBox':
                ctrl = wx.ComboBox(self, choices=value_dict['choices'],
                                   style=wx.CB_DROPDOWN|wx.CB_READONLY,
                                   value=str(value_dict['default']))
                self.field_gui_dict[field] = {'label':label, 'ctrl':ctrl}
        self.savesettingsButton = wx.Button(self, label='Save Settings')
        self.closeButton = wx.Button(self, label='Close Window')


    def do_layout(self):
        vSizer = wx.BoxSizer(wx.VERTICAL)
        # gridSizer = wx.FlexGridSizer(rows=len(self.field_gui_dict)+4, cols=2, vgap=10,
        #                              hgap=10)
        # Prepare some reusable arguments for calling sizer.Add():
        emptySpace = (10, 10)
        # Add the controls to the sizers:
        vSizer.AddSpacer(emptySpace)
        vSizer.Add(self.titleLabel, wx.EXPAND)
        vSizer.AddSpacer(emptySpace)
        for field in self.field_gui_dict.keys():
            vSizer.Add(self.field_gui_dict[field]['label'], wx.EXPAND)
            vSizer.Add((self.field_gui_dict[field]['ctrl']))
        vSizer.AddSpacer(emptySpace)
        vSizer.Add(self.savesettingsButton, wx.EXPAND)
        vSizer.Add(self.closeButton, wx.EXPAND)
        vSizer.Add(emptySpace)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddSpacer(emptySpace)
        hSizer.Add(vSizer)
        hSizer.Add(emptySpace)

        self.SetSizer(hSizer)
    
    def report_values(self):
        pass

    def set_values(self):
        pass

class Toolbar(aui.AuiToolBar):

    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
        self.simulateButton = wx.Button(self, label='Start Simulation')
        self.viewsettingsButton = wx.Button(self, label='Simulation Settings')
        self.popupframe = Form(setup_dict, self)
        self.popupframe.SetSize(self.popupframe.GetBestSize())
        # Add GUI Items to Toolbar
        self.AddControl(self.simulateButton)
        self.AddControl(self.viewsettingsButton)
        # Bind Buttons
        self.viewsettingsButton.Bind(wx.EVT_BUTTON, self.on_view_button)

    def on_view_button(self, event):
        self.viewsettingsButton.Disable()
        self.popupframe.Show(True)

if __name__ == '__main__':
    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(400, 100), 
                                       style=wx.TE_MULTILINE)
            self.toolbar = Toolbar(self, -1, wx.DefaultPosition, 
                                             wx.DefaultSize, 
                                             agwStyle=aui.AUI_TB_OVERFLOW |
                                             aui.AUI_TB_TEXT |
                                             aui.AUI_TB_HORZ_TEXT)
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.AddPane(self.toolbar, aui.AuiPaneInfo().Name('tb').
                              Caption('ToolBar').
                              ToolbarPane().Bottom())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Form Generator Test", size=wx.Size(400, 400))
    frame.Show(True)
    app.MainLoop()
