"""This file is only for tests.

It creates an application showing current state of the art."""

import wx
import sys
from atlantis.wxgui.hexmap import HexMapWindow
from atlantis.wxgui.hexmap import EVT_HEX_SELECTED
from atlantis.wxgui import hexmapdata

from atlantis.gamedata.gamedata import GameData
from atlantis.parsers.reportparser import ReportParser

from atlantis.gamedata.rules import AtlantisRules
from atlantis.gamedata.theme import Theme

if __name__ == '__main__':
    class TestFrame(wx.Frame):
        def __init__(self, parent=None):
            wx.Frame.__init__(self, parent, size=(500, 500),
                              title='Test frame', style=wx.DEFAULT_FRAME_STYLE)
            self.mapwindow = HexMapWindow(self)
            
            self.Bind(EVT_HEX_SELECTED, self.OnSelectHex, source=self.mapwindow)
        
        def OnSelectHex(self, event):
            print(event.hexagon)
#             print(self.mapwindow._map_data._map_data.get_region(event.hexagon + (self.mapwindow._map_data._current_level,)))
            print(event.hexagon + (self.mapwindow._map_data._current_level,))
            map_hex = self.mapwindow._map_data._map_data.get_region(event.hexagon + (self.mapwindow._map_data._current_level,))
            print(map_hex.region.__dict__)
            try:
                for s in map_hex.region.structures.values():
                    print(s.num, s.name)
            except AttributeError:
                print('None')

    app = wx.App()
    frame = TestFrame(None)
    
    openDirDialog = wx.DirDialog(None, 'Choose rules folder', '/home/david/Data/Atlantis/pyAH/rulesets',
                                 wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    
    if openDirDialog.ShowModal() == wx.ID_CANCEL:
        sys.exit()
    
    rules_folder = openDirDialog.GetPath()
    ar = AtlantisRules.read_folder(rules_folder)
    
    openDirDialog = wx.DirDialog(None, 'Choose theme folder', '/home/david/Data/Atlantis/pyAH/themes',
                                 wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    
    if openDirDialog.ShowModal() == wx.ID_CANCEL:
        sys.exit()
    
    theme_folder = openDirDialog.GetPath()
    th = Theme.read_folder(theme_folder)
    
    openFileDialog = wx.FileDialog(None, 'Choose report file', '/home/david/Data/Atlantis/games/havilah', '',
                                   'Report files (*.rep)|*.rep',
                                   wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
        sys.exit()
    
    gd = GameData()
    parser = ReportParser(gd)
    
    with open(openFileDialog.GetPath()) as f:
        parser.parse(f)
    
    map_data = hexmapdata.MapData.from_map_and_theme(gd.map, th)
    
    frame.mapwindow.set_map_data(map_data)

    frame.Show()
    app.MainLoop()