import wx
import wx.aui

class ConnSettingsPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(ConnSettingsPanel, self).__init__(*args, **kwargs)
        self.createControls()
        self.doLayout()

    def createControls(self):
        self.formLabel = wx.StaticText(self, label="Connection Settings")
        self.hostLabel = wx.StaticText(self, label="Host:")
        self.hostTextCtrl = wx.TextCtrl(self, value="localhost")
        self.portLabel = wx.StaticText(self, label="Port:")
        self.portTextCtrl = wx.TextCtrl(self, value="12345")
        self.connectButton = wx.Button(self, label="Connect")

    def doLayout(self):
        # A GridSizer will contain the controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)

        # Make single rows using sizers:
        hostSizer = wx.BoxSizer(wx.HORIZONTAL)
        hostSizer.Add(self.hostLabel)
        hostSizer.AddSpacer((5,0))
        hostSizer.Add(self.hostTextCtrl)
        
        portSizer = wx.BoxSizer(wx.HORIZONTAL)
        portSizer.Add(self.portLabel)
        portSizer.AddSpacer((5,0))
        portSizer.Add(self.portTextCtrl)

        # Add the controls to the sizers:
        for control, options in \
                [emptySpace,
                 emptySpace,
                 (self.formLabel, expandOption),
                 emptySpace,
                 (hostSizer, expandOption),
                 emptySpace,
                 (portSizer, expandOption),
                 emptySpace,
                 (self.connectButton, dict(flag=wx.ALIGN_CENTER)),
                 emptySpace]:
            gridSizer.Add(control, **options)
        # Add extra space on side
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddSpacer((10,0))
        hSizer.Add(gridSizer)
        self.SetSizer(hSizer)

# class ConnSettingsToolbar(wx.aui.AuiToolBar):
    
#     def __init__(self, *args, **kwargs):
#         super(ConnSettingsToolbar, self).__init__(*args, **kwargs)
#         self.add_content()
    

if __name__ == '__main__':
    
    app = wx.App()
    view = wx.Frame(None)
    panel = ConnSettingsPanel(view, size=wx.Size(400,100))
    view.Show()
    app.MainLoop()
