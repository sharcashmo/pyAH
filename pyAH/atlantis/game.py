"""This file is only for tests.

It creates an application showing current state of the art."""

import wx
import sys
from atlantis.wxgui.hexmap import HexMapWindow
from atlantis.wxgui.hexmap import HexMapData
from atlantis.wxgui.hexmap import EVT_HEX_SELECTED

from atlantis.gamedata.gamedata import GameData
from atlantis.parsers.reportparser import ReportParser

from atlantis.gamedata.rules import AtlantisRules

if __name__ == '__main__':
    class TestFrame(wx.Frame):
        def __init__(self, parent=None):
            wx.Frame.__init__(self, parent, size=(500, 500),
                              title='Test frame', style=wx.DEFAULT_FRAME_STYLE)
            self.mapwindow = HexMapWindow(self)
            
            self.Bind(EVT_HEX_SELECTED, self.OnSelectHex, source=self.mapwindow)
        
        def OnSelectHex(self, event):
            print(event.hexagon)

    app = wx.App()
    frame = TestFrame(None)
    
    openDirDialog = wx.DirDialog(None, 'Choose rules folder', '/home/david/Data/Atlantis/pyAH/rulesets',
                                 wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    
    if openDirDialog.ShowModal() == wx.ID_CANCEL:
        sys.exit()
    
    ar = AtlantisRules.read_folder(openDirDialog.GetPath())
    
    for tt in ar.gui_colors['terrain_types']:
        print(ar.gui_colors['terrain_types'][tt])
        brush = wx.Brush(wx.Colour(*(ar.gui_colors['terrain_types'][tt])))
        frame.mapwindow.add_terrain_type(tt, brush)
    
    openFileDialog = wx.FileDialog(None, 'Choose report file', '/home/david/Data/Atlantis/games/havilah', '',
                                   'Report files (*.rep)|*.rep',
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
        sys.exit()
    
    gd = GameData()
    parser = ReportParser(gd)
    
    with open(openFileDialog.GetPath()) as f:
        parser.parse(f)
    
    map_data = [HexMapData(tuple(list(r.location)[:2]), r.terrain, None, None) for r in gd.map.regions.values()]
    
    frame.mapwindow.set_map_data(map_data)

    frame.Show()
    app.MainLoop()