#!/usr/bin/python

#formgenerator.py

import wx
import json
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

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

fields_dict = {}

fields_dict['update_int'] = {'type':'textCtrl', 'label':'Update Interval (sec)',
                             'value':.5
                             }
fields_dict['fsamp'] = {'type':'textCtrl', 
                        'label':'Sampling Frequency (MegaSamples/sec)',
                        'value':100
                        }
fields_dict['NFFT'] = {'type':'textCtrl', 'label':'NFFT', 'value':2**12
                       }
noise_level_list = ['P_1W_var_1s', 
                    'P_2kW_var_1s'
                    ]
fields_dict['noise_level'] = {'type':'comboBox', 
                              'label':'Noise Level', 
                              'choices': noise_level_list, 
                              'default': noise_level_list[1]
                              }

setup_dict = {}

setup_dict['title'] = 'Simulation Settings'
setup_dict['fields'] = fields_dict

if __name__ == '__main__':

    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            self.testFrame = Form(setup_dict, None)
            self.testFrame.SetSize(self.testFrame.GetBestSize())
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(400, 100), 
                                       style=wx.TE_MULTILINE)
            self.testButton = wx.Button(self, label='Test')
            self.testButton.Bind(wx.EVT_BUTTON, self.on_test_button)
            self.testFrame.closeButton.Bind(wx.EVT_BUTTON, self.on_frame_close)
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.AddPane(self.testButton, aui.AuiPaneInfo().Name('button').
                              Caption('Button').
                              Bottom())
            self._mgr.Update()
        
        def on_test_button(self, event):
            self.testFrame.Show(True)

        def on_frame_close(self, event):
            self.testFrame.Show(False)
    
    app = wx.App(False)
    frame = MyFrame(None, title='FormGenTest', size=wx.Size(400,400))
    app.MainLoop()
