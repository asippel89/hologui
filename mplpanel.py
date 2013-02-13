import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt

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
        self.statusctrl = wx.TextCtrl(self.toolbar, style=wx.TE_READONLY, \
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
            self.statusctrl.SetValue("x= " + str(x) + "  y=" + str(y))

    def ChangeCursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

    # def OnEventUpdate(self, msg):
    #     if msg.topic[-1] == 'plot_data':
    #         self.data.append(msg.data)
    #         self.OnPlotUpdate()
    #     if msg.topic[-1] == 'reset_data':
    #         self.data = []
    #         self.ax.clear()
    #         self.canvas.draw()
                     
    # def OnPlotUpdate(self):
    #     if not self.ax:
    #         self.ax = self.fig.add_subplot(111)
    #     # self.x_data = np.arange(len(self.data))
    #     # self.y_data = np.array(self.data)
    #     self.plot_data = self.ax.plot(range(len(self.data)), self.data, color='b')

    #     self.canvas.draw()
