#!/usr/bin/python

#sliderform.py

import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

class SliderPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(SliderPanel, self).__init__(*args, **kwargs)
        self.slider_list = None
        self.value_dict = {}
        self.createControls()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.formLabel = wx.StaticText(self, label="Form Label")
        self.addplotButton = wx.Button(self, label="Add Plot")
        self.clearplotButton = wx.Button(self, label="Clear plot")
        # Create sliders and slider labels
        self.slider1Label = wx.StaticText(self, label="Slider 1")
        self.slider1 = wx.Slider(
            self, id=100, value=25, minValue=1, maxValue=100, pos=(0,0), \
                size=(200, -1), style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS, \
                name='slider1'
            )
        self.slider2Label = wx.StaticText(self, label="Slider 2")
        self.slider2 = wx.Slider(
            self, id=100, value=25, minValue=1, maxValue=100, pos=(0,0), \
                size=(200, -1), style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS, \
                name='slider2'
            )
        self.slider3Label = wx.StaticText(self, label="Slider 3")
        self.slider3 = wx.Slider(
            self, id=100, value=25, minValue=1, maxValue=100, pos=(0,0), \
                size=(200, -1), style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS, \
                name='slider3'
            )
        
    def doLayout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=11, cols=2, vgap=5, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        hbox=wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.addplotButton)
        hbox.AddSpacer((5,0))
        hbox.Add(self.clearplotButton)
        # Add the controls to the sizers:
        for control, options in \
                [emptySpace, emptySpace,
                 (self.formLabel, dict(flag=wx.ALIGN_CENTER)), emptySpace,
                 emptySpace, emptySpace,
                 (self.slider1Label, expandOption), emptySpace, 
                 (self.slider1, noOptions), emptySpace,
                 (self.slider2Label, expandOption), emptySpace,
                 (self.slider2, noOptions), emptySpace,
                 (self.slider3Label, expandOption), emptySpace,
                 (self.slider3, noOptions), emptySpace,
                 emptySpace, emptySpace,
                 (hbox, dict(flag=wx.ALIGN_CENTER)), emptySpace]:
            gridSizer.Add(control, **options)
        # Finally, add a horizontal sizer to give extra space
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer((20, 0))
        hsizer.Add(gridSizer)
            
        self.SetSizer(hsizer)

    def bindEvents(self):
        self.addplotButton.Bind(wx.EVT_BUTTON, self.on_add_plot_button)        
        self.clearplotButton.Bind(wx.EVT_BUTTON, self.on_clear_plot_button)

    def on_add_plot_button(self, event):
        print 'Add plot button pressed'
        print self.retrieve_values()

    def on_clear_plot_button(self, event):
        print 'Clear plot button pressed'

    def retrieve_values(self):
        if self.slider_list is None:
            self.slider_list = [self.slider1, self.slider2, self.slider3]
        for slider in self.slider_list:
            self.value_dict[slider.Name] = slider.GetValue()
        return self.value_dict

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 200), \
                                       style=wx.TE_MULTILINE)
            self.blankPanel = wx.Panel(self, size=wx.Size(600, 400))
            self.sliderPanel = SliderPanel(self, size=wx.Size(250, 600))
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textCtrl').
                              Caption('TextCtrl').Bottom())
            self._mgr.AddPane(self.blankPanel, aui.AuiPaneInfo().
                              Name('blankPanel').
                              Caption('Blank Panel').Center())
            self._mgr.AddPane(self.sliderPanel, aui.AuiPaneInfo().
                              Name('sliderPanel').
                              Caption('Slider Form').Left())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Slider Form Test", \
                        size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()
