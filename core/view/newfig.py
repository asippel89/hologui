#!/usr/bin/python

#newfig.py

import mplpanel2 as mp
import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MyFrame, self).__init__(*args, **kwargs)
        # Create Objects
        self.panel = mp.MPLPanel(self, (12,4), test=True)
        self.panel.add_figtext(.8,.9, "Grid Size (12,4)", 
                                fontsize=15, 
                                fontweight='bold',
                                bbox=dict(facecolor='blue',alpha=0.5)
                                )
        for i in range(12):
            for j in range(4):
                if i==3*j:
                    self.panel.add_sp(3*j,j,rowspan=3)
                if i>3*j:
                    if i%3==0:
                        self.panel.add_sp(i,j,rowspan=2)
                        self.panel.add_sp(i+2,j)
        self.panel.fig.axes[4].get_xaxis().set_visible(False)
        print 'DPI:', self.panel.fig.get_dpi()
        print 'Size Inches:', self.panel.fig.get_size_inches()

app = wx.App(False)
frame = MyFrame(None, title="Plot Canvas & Settings Test", \
                    size=wx.Size(1500, 800))
frame.Show(True)
app.MainLoop()

