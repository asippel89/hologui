#!/usr/bin/python

#rawmplpanel.py

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

class MPLPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(MPLPanel, self).__init__(*args, **kwargs)

        # Setup the canvas
        self.dpi = 100
        self.fig = Figure((3.0, 2.0), dpi=self.dpi)
        self.canvas = FigCanvas(self, -1, self.fig)
        self.plot_dict = None

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

    def add_plot_line(self, data, label):
        if self.ax is None:
            self.ax = self.fig.add_subplot(111)
        else:
            self.plot_dict[label] = self.ax.plot(data)
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()

if __name__ == '__main__':

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwargs):
            super(MyFrame, self).__init__(*args, **kwargs)
            self._mgr = aui.AuiManager(self)
            # Create Objects
            self.plotPanel = MPLPanel(self)

            self.settingsPanel = wx.Panel(self, size=wx.Size(200, 800))
            self._mgr.AddPane(self.plotPanel, aui.AuiPaneInfo().Name('plotPanel').
                              Caption('Plot').Center())
            self._mgr.AddPane(self.settingsPanel, aui.AuiPaneInfo().
                              Name('settingsPanel').
                              Caption('Settings').Left())
            self._mgr.Update()

    app = wx.App(False)
    frame = MyFrame(None, title="MPL Panel Test", \
                        size=wx.Size(1000, 700))
    frame.Show(True)
    app.MainLoop()

