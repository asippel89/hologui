import wx
try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
import csdplotsettingspanel as csdsett
import avgplotsettingspanel as avgsett

class MPLPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0), dpi=self.dpi)
        self.ax = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.ax_dict = None
        self.data = []

        # Setup the toolbar/statustextctrl
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.AddSeparator()
        self.statusctrl = wx.StaticText(self.toolbar, style=wx.TE_READONLY, \
                                          size=wx.Size(300,25))
        self.toolbar.AddControl(self.statusctrl)
        
        # Do the layout
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, flag=wx.EXPAND|wx.GROW|wx.ALL)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.canvas.draw()

        # Bind mouse events to mplcanvas
        # Note that event is a MplEvent
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)

        # Observer of Notify events
        # Publisher.subscribe(self.OnEventUpdate, MSG_NOTIFY_ROOT)
        
    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusctrl.SetLabel("x= " + str(x) + "  y=" + str(y))

    def ChangeCursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

class CSDPlotPresenter(object):
    '''
    Will be responsible for handling the data (putting it into ax instances)
    and feeding it to the plot canvas. Can also capture mouse events (clicks
    for specifying region, etc).

    ~Also handles the plot settings toolbar and its presenter~
    Settings panel and canvas still need to be added to the AUI manager in the
    frame presenter, otherwise they will appear floating in the corner

    **Note**
    This presenter should not have knowledge of its caption and/or placement,
    or whether or not there are other similar presenters, this is handled in the
    view or frame presenter.
    '''
    def __init__(self, frame):
        self.frame = frame
        self.canvas = MPLPanel(self.frame)
        # Create settings toolbar presenter
        self.settingspresenter = csdsett.CSDSettPresenter(self.frame)
        self.settings = self.settingspresenter.panel

    def notify_frame_presenter(self):
        '''Not sure if this will be necessary'''
        pass
        
    def process_data(self, data):
        pass

class AVGPlotPresenter(object):
    '''
    Will differ greatly from CSDPlotPresenter in how it handles the incoming data
    '''
    def __init__(self, frame):
        self.frame = frame
        self.canvas = MPLPanel(self.frame)
        # Create settings toolbar presenter
        self.settingspresenter = avgsett.AVGSettPresenter(self.frame)
        self.settings = self.settingspresenter.panel

    def notify_frame_presenter(self):
        '''Not sure if this will be necessary'''
        pass
        
    def process_data(self, data):
        pass
    

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.plotpresenter = CSDPlotPresenter(self)
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 200), \
                                       style=wx.TE_MULTILINE)
            self._mgr.AddPane(self.textCtrl, aui.AuiPaneInfo().Name('textCtrl').
                              Caption('TextCtrl').Bottom())
            self._mgr.AddPane(self.plotpresenter.canvas, aui.AuiPaneInfo().
                              Name('plotcanvas1').
                              Caption('Plot Canvas 1').Center())
            self._mgr.AddPane(self.plotpresenter.settings, aui.AuiPaneInfo().
                              Name('plotcanvas1settings').
                              Caption('Plot 1 Settings').Left())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="Plot Canvas & Settings Test", \
                        size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()

