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
    def __init__(self, parent, gridsize, test=False, **kwargs):
        self.test = test
        self.view_ax_info_state = self.test
        super(MPLPanel, self).__init__(parent)
        self.gridoptions = kwargs
        if len(self.gridoptions) > 0:
            print self.gridoptions
        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((12, 10))
        self.gridsize = gridsize
        self.gs = matplotlib.gridspec.GridSpec(gridsize[0],gridsize[1])
        self.gs.update(left=.05,right=.95,hspace=.5)
        self.ax1 = None
        self.ax2 = None
        self.canvas = FigCanvas(self, -1, self.fig)
        self.do_layout()

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
        if self.test:
            self.testButton = wx.Button(self.toolbar, label='del_sp(6)')
            self.testButton2 = wx.Button(self.toolbar, label='add_sp(0,1,colspan=3)')
            self.testButton3 = wx.Button(self.toolbar, label='view_axis_info')            
            self.toolbar.AddControl(self.testButton)
            self.toolbar.AddControl(self.testButton2)
            self.toolbar.AddControl(self.testButton3)
            self.testButton.Bind(wx.EVT_BUTTON, self.onTestButton)
            self.testButton2.Bind(wx.EVT_BUTTON, self.onTestButton2)
            self.testButton3.Bind(wx.EVT_BUTTON, self.onTestButton3)
        self.toolbar.AddSeparator()
        self.statusctrl = wx.StaticText(self.toolbar, style=wx.TE_READONLY, size=wx.Size(300,25))
        self.toolbar.AddControl(self.statusctrl)
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        panelvbox.Add(self.canvas, 1, flag=wx.EXPAND|wx.GROW|wx.ALL)
        panelvbox.Add(self.toolbar, 0, flag=wx.EXPAND|wx.GROW|wx.ALL)
        self.SetSizer(panelvbox)
        panelvbox.Fit(self)
        self.toolbar.Realize()
        self.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
        self.canvas.draw()

    def UpdateStatusBar(self, event):
        """Function to update statusbar with mouse position"""
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusctrl.SetLabel("x= " + str(x) + 
                                            "  y=" + str(y)
                                            )
        else:
            pass

    def onTestButton(self, event):
        self.del_sp(6)

    def onTestButton2(self, event):
        self.add_sp(0,1,colspan=3,rowspan=3)

    def onTestButton3(self, event):
        self.view_ax_info_state = not self.view_ax_info_state
        if self.view_ax_info_state:
            self.view_axis_info()
        else: 
            for i,ax in enumerate(self.fig.axes):
                if ax.texts > 0:
                    ax.texts = []
            self.canvas.draw()
            
    def view_axis_info(self):
        for i,ax in enumerate(self.fig.axes):
            if ax.texts > 0:
                ax.texts = []
            geom = ax.get_geometry()
            label = 'Axis #'+str(i)+', Loc: '+str(geom)
            ax.text(.5, .5, label, 
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform = ax.transAxes)
        self.canvas.draw()

    def add_sp(self, x, y, colspan=None, rowspan=None, testax=False):
        if colspan and rowspan:
            ax = self.fig.add_subplot(self.gs[x:x+rowspan,y:y+colspan])
        elif colspan:
            ax = self.fig.add_subplot(self.gs[x,y:y+colspan])
        elif rowspan:
            ax = self.fig.add_subplot(self.gs[x:x+rowspan,y])
        else:    
            ax = self.fig.add_subplot(self.gs[x,y])
        # Add instructive text if testax True
        # if testax:
        #     num = len(self.fig.axes) - 1
        #     location = ax.get_geometry()
        #     ax.text(.5, .5, 'Axes Index: ' + str(num), 
        #              horizontalalignment='center',
        #              verticalalignment='center',
        #              transform = ax.transAxes)
        #     ax.text(.5, .4, 'Geometry: '+str(location),
        #              horizontalalignment='center',
        #              verticalalignment='center',
        #              transform = ax.transAxes)
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()
        return ax

    def del_sp(self, axindex):
        self.fig.delaxes(self.fig.axes[axindex])
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()

    def add_figtext(self, x, y, s, **kwargs):
        self.fig.text(x, y, s, kwargs)
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
            self.textCtrl = wx.TextCtrl(self, size=wx.Size(800, 50), \
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

