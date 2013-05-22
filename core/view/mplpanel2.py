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
        # Instance variables for storing info
        self.figtext_info = []
        # Plot Update
        self.plot_update = True

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
        self.updateButton = wx.Button(self.toolbar, label='Pause')
        self.updateButton.Bind(wx.EVT_BUTTON, self.on_update_button)
        self.toolbar.AddControl(self.updateButton)
        if self.test:
            self.toolbar.AddSeparator()
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
            self.statusctrl.SetLabel("x= " + str(x) + "  y=" + str(y))
        else:
            pass

    def on_update_button(self,event):
        if self.plot_update:
            self.updateButton.SetLabel('Resume')
        else:
            self.updateButton.SetLabel('Pause')
        self.toggle_plot_update_state()
        return

    def toggle_plot_update_state(self):
        self.plot_update = not self.plot_update
        return

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

    def add_sp(self, x, y, colspan=None, rowspan=None):
        '''
        Method called whenever a subplot is added to the figure, initiates a Subplot instance
        '''
        if not colspan:
            colspan = 1
        if not rowspan:
            rowspan = 1
        span = self.gs[x:x+rowspan,y:y+colspan]
        loc_info = {}
        loc_info['x_pos'] = x
        loc_info['y_pos'] = y
        loc_info['colspan'] = colspan
        loc_info['rowspan'] = rowspan
        ax = Subplot(self.fig, span, loc_info)
        # View Ax Info
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()
        return ax

    def del_sp(self, axindex):
        self.fig.delaxes(self.fig.axes[axindex])
        # update view info if active
        if self.view_ax_info_state:
            self.view_axis_info()
        self.canvas.draw()

    def add_figtext(self, x, y, s, **kwargs):
        self.fig.text(x, y, s, kwargs)
        self.figtext_info.append({'x_pos':x,'y_pos':y,'text':s,'options':kwargs})
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
        # Add figure text info
        cf['figtext'] = self.figtext_info
        # Add subplot info
        cf['subplots'] = []
        for ax in self.fig.axes:
            cf['subplots'].append(ax.get_options_dict())
        f = open(filename, 'w')
        json.dump(cf, f, sort_keys=True, indent=4, separators=(',',': '))
        f.close()
        return cf
        
    def load_config(self, filename):
        """
        Loads from JSON the config file
        """
        f = open(filename, 'r')
        cf = json.load(f)
        f.close()
        self.sp_info = []
        # Update/Load Figure Configuration
        self.fig.clear()
        for ax in self.fig.axes:
            self.fig.delaxes(ax)
        self.dpi = cf['dpi']
        self.fig.set_dpi(self.dpi)
        self.figsize = tuple(cf['figsize'])
        self.gridsize = tuple(cf['gridsize'])
        gs_opts = cf['gridspec_options']
        self.change_grid_size(self.gridsize,
                              left=gs_opts['left'],
                              right=gs_opts['right'],
                              hspace=gs_opts['hspace']
                              )
        # self.fig.set_size_inches(self.figsize) # For some reason this doesn't work
        # Add all figtext
        for text in cf['figtext']:
            # Note that the options unpacking only will work if the 
            # parameters are json serializable
            self.add_figtext(text['x_pos'],text['y_pos'],text['text'],**text['options'])
        # Update/Load Subplots
        for ax_dict in cf['subplots']:
            ax = self.add_sp(ax_dict['x_pos'],
                             ax_dict['y_pos'],
                             ax_dict['colspan'],
                             ax_dict['rowspan']
                             )
            ax.load_from_options(ax_dict)
        self.canvas.draw()

class Subplot(matplotlib.axes.Subplot):
    
    def __init__(self, fig, span, pos_info, *args, **kwargs):
        self.fig = fig
        super(Subplot, self).__init__(fig, span)
        self.fig.add_subplot(self)
        self.options_dict = pos_info
        # Add other options and their hooks here
        self.options_map = {'xlabel':[self.get_xlabel,self.set_xlabel],
                            'ylabel':[self.get_ylabel,self.set_ylabel],
                            'xlim':[self.get_xlim, self.set_xlim],
                            'ylim':[self.get_ylim, self.set_ylim],
                            'title':[self.get_title, self.set_title]
                            }

    def get_options_dict(self):
        '''
        Use this as a dispatcher for the various axis options.
        '''
        # still won't handle latex formatted strings
        for option in self.options_map:
            self.options_dict[option] = self.options_map[option][0]()
        return self.options_dict

    def load_from_options(self, options_dict):
        for option in options_dict:
            if option in ['rowspan','colspan', 'x_pos', 'y_pos']:
                pass
            else:
                self.options_map[option][1](options_dict[option])

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.panel = MPLPanel(self, (12,4))
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

