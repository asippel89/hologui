#!/usr/bin/python

#plotsettingspanel.py

import wx
try:
    from agw import aui
    from agw import pycollapsiblepane as PCP
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    import wx.lib.agw.pycollapsiblepane as PCP

View_Options = ['x00', 'x01', 'x02', 'x03', 'x11', 'x12', 'x13', 'x22', 'x23', 'x33']
RB_View_Options = ['x00', 'x01', 'x02', 'x03', '', 'x11', 'x12', 'x13', '', '', 'x22',\
                       'x23', '', '', '', 'x33']

class Panel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)
        
        self.create_items()
        self.do_layout()

    def create_items(self):
        self.accumCheckBox = wx.CheckBox(self, label="Accumulate?")
        self.viewoptionsLabel = wx.StaticText(self, label="View which X-Spectra?")
        self.viewoptionsCheckLB = wx.CheckListBox(self, -1, wx.DefaultPosition,\
                                                      (70,235), \
                                                      View_Options)
        self.gridCheckBox = wx.CheckBox(self, label="Show Grid?")
        self.gridCheckBox.SetValue(False)
        self.legendCheckBox = wx.CheckBox(self, label="Show Legend?")
        # self.viewoptionsRadioBox = wx.RadioBox(self, -1, choices=RB_View_Options, \
        #                                            majorDimension=4, \
        #                                            style=wx.RA_SPECIFY_COLS)
                                                  
    def do_layout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=7, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Active tab gets its own sizer
        # tab_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # tab_sizer.Add(self.viewoptionsLabel)
        # tab_sizer.AddSpacer((5, 0))
        # tab_sizer.Add(self.viewoptionsCheckLB)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 emptySpace,
                 (self.viewoptionsLabel, expandOption),
                 emptySpace, 
                 (self.viewoptionsCheckLB, noOptions),
                 emptySpace,
                 (self.accumCheckBox, expandOption),
                 emptySpace,
                 (self.gridCheckBox, expandOption),
                 emptySpace,
                 (self.legendCheckBox, expandOption)]:
            gridSizer.Add(control, **options)
        # Finally, add a horizontal sizer to give extra space
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer((10, 0))
        hsizer.Add(gridSizer)
            
        self.SetSizer(hsizer)

if __name__ == '__main__':

    class MyFrame(wx.Frame):

        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            textCtrl = wx.TextCtrl(self, size=wx.Size(800, 300), \
                                       style=wx.TE_MULTILINE)
            panel = Panel(self, size=wx.Size(300, 800))
            self._mgr.AddPane(panel, aui.AuiPaneInfo().Name('plotsettingspanel').
                              Caption('Plot Settings').
                              Left().MaximizeButton())
            self._mgr.AddPane(textCtrl, aui.AuiPaneInfo().Name('textctrl').
                              Caption('Text Control').
                              Center().MaximizeButton())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Plot Settings Test", size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()
