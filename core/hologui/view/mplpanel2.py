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
import json

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
        self.dpi = 80
        self.figsize = (13.85,10) 
        self.fig = Figure(figsize=self.figsize, dpi=self.dpi)
        self.gridsize = gridsize
        self.gsleft = 0.05
        self.gsright = .95
        self.gshspace = .5
        self.change_grid_size(self.gridsize, 
                              left=self.gsleft, 
                              right=self.gsright, 
                              hspace=self.gshspace
                              )
        self.canvas = FigCanvas(self, -1, self.fig)
        # Initialize Subplot Info list
        self.sp_info = []
        self.do_layout()
        
    def change_grid_size(self, gridsize, update=False, **kwargs):
        self.gs = matplotlib.gridspec.GridSpec(gridsize[0],gridsize[1])
        self.gs.update(**kwargs)
        if update:
            self.canvas.draw()
        
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
            self.testButton4 = wx.Button(self.toolbar, label='save_config')            
            self.testButton5 = wx.Button(self.toolbar, label='load_config')            
            self.toolbar.AddControl(self.testButton)
            self.toolbar.AddControl(self.testButton2)
            self.toolbar.AddControl(self.testButton3)
            self.toolbar.AddControl(self.testButton4)
            self.toolbar.AddControl(self.testButton5)
            self.testButton.Bind(wx.EVT_BUTTON, self.onTestButton)
            self.testButton2.Bind(wx.EVT_BUTTON, self.onTestButton2)
            self.testButton3.Bind(wx.EVT_BUTTON, self.onTestButton3)
            self.testButton4.Bind(wx.EVT_BUTTON, self.onTestButton4)
            self.testButton5.Bind(wx.EVT_BUTTON, self.onTestButton5)
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
            
    def onTestButton4(self,event):
        self.save_config('TestConfig.json')

    def onTestButton5(self,event):
        self.load_config('TestConfig.json')
            
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
        # Add location info to sp_info
        loc_info = {}
        loc_info['x_pos'] = x
        loc_info['y_pos'] = y
        loc_info['colspan'] = colspan
        loc_info['rowspan'] = rowspan
        self.sp_info.append(loc_info)
        # View Ax Info
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()
        return ax

    def del_sp(self, axindex):
        self.fig.delaxes(self.fig.axes[axindex])
        # remove from sp_info
        self.sp_info.pop(axindex)
        # update view info if active
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()

    def add_figtext(self, x, y, s, **kwargs):
        self.fig.text(x, y, s, kwargs)
        self.canvas.draw()

    def save_config(self, filename):
        cf = {}
        # Add figure info
        cf['dpi'] = self.dpi
        cf['figsize'] = self.figsize
        cf['gridsize'] = self.gridsize
        cf['gridspec_options'] = {'left':self.gsleft,
                                  'right':self.gsright, 
                                  'hspace':self.gshspace
                                  }
        # Add subplot info
        cf['subplots'] = self.sp_info
        f = open(filename, 'w')
        json.dump(cf, f, sort_keys=True, indent=4, separators=(',',': '))
        f.close()
        print 'Num Subplots:', len(cf['subplots'])
        return cf
        
    def load_config(self, filename):
        """
        Loads from JSON the config file
        """
        f = open(filename, 'r')
        cf = json.load(f)
        f.close()
        print 'len sp_info at load', len(self.sp_info)
        self.sp_info = []
        # Update/Load Figure Configuration
        self.fig.clear()
        for ax in self.fig.axes:
            self.fig.delaxes(ax)
        self.dpi = cf['dpi']
        print 'DPI at load:', self.dpi
        self.fig.set_dpi(self.dpi)
        self.figsize = tuple(cf['figsize'])
        print 'Reported figsize at load:', self.figsize
        # self.fig.set_size_inches(self.figsize)
        print 'Actual figsize after load:', self.fig.get_size_inches()
        self.gridsize = tuple(cf['gridsize'])
        gs_opts = cf['gridspec_options']
        self.change_grid_size(self.gridsize,
                              left=gs_opts['left'],
                              right=gs_opts['right'],
                              hspace=gs_opts['hspace']
                              )
        # Update/Load Subplots
        for ax_info in cf['subplots']:
            self.add_sp(ax_info['x_pos'],ax_info['y_pos'],ax_info['colspan'],ax_info['rowspan'])
        self.canvas.draw()


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

