import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    NONLOCAL_AGW = True
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.dates as mdates
import datetime as dt

MPL_VERSION = matplotlib.__version__

class MPLPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0))
        self.ax1 = None
        self.ax2 = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.do_layout()
        self.load_config()

    def do_layout(self):
        # Setup the toolbar/statustextctrl
        self.toolbar = NavigationToolbar(self.canvas)
        if wx.Platform == '__WXMAC__':
            self.SetToolBar(self.toolbar)
        else:
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            self.toolbar.SetSize(wx.Size(fw, th))
        self.toolbar.dynamic_update()
        self.toolbar.AddSeparator()
        self.testButton = wx.Button(self.toolbar, label='Pause')
        self.toolbar.AddControl(self.testButton)
        self.statusctrl = wx.StaticText(self.toolbar, style=wx.TE_READONLY, size=wx.Size(300,25))
        self.toolbar.AddControl(self.statusctrl)
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, flag=wx.EXPAND|wx.GROW|wx.ALL)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.toolbar.Realize()
        self.canvas.draw()

    def load_config(self, plottype=None):
        """
        Loads from JSON the config file
        """
        pass

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.panel = MPLPanel(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 200), \
                                       style=wx.TE_MULTILINE)
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textCtrl').
                              Caption('TextCtrl').Bottom())
            self._mgr.AddPane(self.panel, aui.AuiPaneInfo().
                              Name('plotcanvas1').
                              Caption('Plot Canvas 1').Center())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Plot Canvas & Settings Test", \
                        size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()

