import wx

class ControlPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self.createControls()
        self.doLayout()
        self.redraw_timer = wx.Timer(self)
        self.is_paused = 0

    def createControls(self):
        self.runButton = wx.Button(self, label="Run")
        self.resetButton = wx.Button(self, label="Reset")
        self.resetButton.Disable()
        self.testButton = wx.Button(self, label="TestThread")
        self.titleLabel = wx.StaticText(self, label="Title:")
        self.titleTextCtrl = wx.TextCtrl(self, value="Enter plot title here")
        self.verboseCheckBox = wx.CheckBox(self, label="Do you want verbose output?")
        self.verboseCheckBox.SetValue(True)

    def doLayout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)

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
                 (self.verboseCheckBox, noOptions),
                 emptySpace,
                 (self.runButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace,
                 (self.testButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace,
                 (self.resetButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace]:
            gridSizer.Add(control, **options)
        # Give extra space on Left
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddSpacer((10,0))
        hSizer.Add(gridSizer)
        self.SetSizer(hSizer)
