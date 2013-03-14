#!/usr/bin/python

#simulatesettingsform.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
from wx.lib.pubsub import Publisher as pub
import formgenerator as fgen

class SimulateSettingsFrame(wx.Frame):
    
    def __init__(self, options_dict, parent, *args, **kwargs):
        self.setup_options_dict = options_dict
        self.options_dict = None
        super(SimulateSettingsFrame, self).__init__(parent=parent, *args, **kwargs)
        self.create_items()
        self.set_form_values(self.setup_options_dict)
        self.do_layout()

    def create_items(self):
        self.panelLabel = wx.StaticText(self, 
                                        label='Simulation Settings')
        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.panelLabel.SetFont(font)
        self.update_intLabel = wx.StaticText(self, 
                                           label='Update Interval (sec)')
        self.update_intCtrl = wx.TextCtrl(self, value='')
        self.fsampLabel = wx.StaticText(self, 
                                        label='Sampling Frequendy (MegaSamples/sec)')
        self.fsampCtrl = wx.TextCtrl(self, value='')
        self.NFFTLabel = wx.StaticText(self, label='NFFT')
        self.NFFTCtrl = wx.TextCtrl(self, value='')
        self.noise_levelLabel = wx.StaticText(self,
                                              label='Noise Level')
        self.noise_levelCtrl = wx.ComboBox(self, 
                                           choices=\
                                               self.setup_options_dict['noise_level'],
                                           style=wx.CB_DROPDOWN|wx.CB_READONLY,
                                           value='')
        self.savesettingsButton = wx.Button(self, label='Save Settings')
        self.closeButton = wx.Button(self, label='Close Window')

    def do_layout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=15, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 emptySpace,
                 (self.panelLabel, expandOption),
                 emptySpace,
                 emptySpace, emptySpace,
                 (self.update_intLabel, noOptions),
                 emptySpace,
                 (self.update_intCtrl, expandOption),
                 emptySpace,
                 (self.fsampLabel, expandOption),
                 emptySpace,
                 (self.fsampCtrl, expandOption),
                 emptySpace,
                 (self.NFFTLabel, expandOption),
                 emptySpace,
                 (self.NFFTCtrl, expandOption),
                 emptySpace,
                 (self.noise_levelLabel, expandOption),
                 emptySpace,
                 (self.noise_levelCtrl, expandOption),
                 emptySpace,
                 emptySpace, emptySpace,
                 (self.savesettingsButton, expandOption), emptySpace,
                 (self.closeButton, expandOption), emptySpace,
                 emptySpace, emptySpace]:
            gridSizer.Add(control, **options)

        # Finally, add a horizontal sizer to give extra space
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer((10, 0))
        hsizer.Add(gridSizer)
            
        self.SetSizer(hsizer)

    def report_field_values(self):
        if self.options_dict is None:
            self.options_dict = {}
        self.options_dict['update_int'] = float(self.update_intCtrl.GetValue())
        self.options_dict['fsamp'] = int(self.fsampCtrl.GetValue())
        self.options_dict['NFFT'] = int(self.NFFTCtrl.GetValue())
        self.options_dict['noise_level'] = self.noise_levelCtrl.GetValue()
        return self.options_dict 

    def set_form_values(self, value_dict):
        self.update_intCtrl.SetValue(str(value_dict['update_int']))
        self.fsampCtrl.SetValue(str(value_dict['fsamp']))
        self.NFFTCtrl.SetValue(str(value_dict['NFFT']))
        self.noise_levelCtrl.SetValue(str(value_dict['noise_level'][1]))

class SimulationToolbar(aui.AuiToolBar):

    def __init__(self, *args, **kwargs):
        super(SimulationToolbar, self).__init__(*args, **kwargs)
        # Keep default options dict as reference
        self.noise_level_list = ['P_1W_var_1s', 
                                 'P_2kW_var_1s'
                                 ]
        self.setup_options_dict = {'update_int':.5, 'fsamp':100, 'NFFT':2**12, 
                                   'noise_level':self.noise_level_list}
        self.default_options_dict = {'update_int':.5, 'fsamp':100, 'NFFT':2**12, 
                                     'noise_level':self.noise_level_list[1]}
        self.options_dict = None
        # Create GUI Items
        self.simulateButton = wx.Button(self, label='Start Simulation')
        self.viewsettingsButton = wx.Button(self, label='Simulation Settings')
        self.popupframe = SimulateSettingsFrame(self.setup_options_dict, self)
        self.popupframe.SetSize(self.popupframe.GetBestSize())
        # Add GUI Items to Toolbar
        self.AddControl(self.simulateButton)
        self.AddControl(self.viewsettingsButton)
        # Bind Buttons
        self.viewsettingsButton.Bind(wx.EVT_BUTTON, self.on_view_button)
        self.simulateButton.Bind(wx.EVT_BUTTON, self.on_simulate_start)
        self.popupframe.closeButton.Bind(wx.EVT_BUTTON, self.on_frame_close)
        self.popupframe.savesettingsButton.Bind(wx.EVT_BUTTON, 
                                                self.update_options_dict)
        # Bind Frame Close
        self.popupframe.Bind(wx.EVT_CLOSE, self.on_frame_close)

    def update_options_dict(self, event):
        new_dict = self.popupframe.report_field_values()
        self.options_dict = new_dict

    def on_simulate_start(self, event):
        if self.options_dict is None:
            pub.sendMessage('controller.simulate', self.default_options_dict)
        else:
            pub.sendMessage('controller.simulate', self.options_dict)

    def on_view_button(self, event):
        self.viewsettingsButton.Disable()
        self.popupframe.Show(True)

    def on_frame_close(self, event):
        self.viewsettingsButton.Enable()
        self.popupframe.Show(False)

if __name__ == '__main__':
    
    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(400, 100), 
                                       style=wx.TE_MULTILINE)
            self.toolbar = SimulationToolbar(self, -1, wx.DefaultPosition, 
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
    frame = MyFrame(None, title="Simulation Settings Test", size=wx.Size(400, 400))
    frame.Show(True)
    app.MainLoop()
