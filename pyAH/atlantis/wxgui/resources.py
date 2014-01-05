"""Holds common resources for :ref:`atlantis.wxgui` package modules."""

import os
import wx

_resources_folder, dummy = os.path.split(__file__)
_resources_folder = os.path.join(_resources_folder, 'resources')

def get_drag_cursor():
    """Return a :class:`wx.Cursor` to be used for dragging."""
    if wx.Platform == '__WXMSW__':
        return wx.Cursor(
            wx.Image(os.path.join(_resources_folder, 'drag_cursor.cur')))
    else:
        return wx.Cursor(
            wx.Image(os.path.join(_resources_folder, 'drag_cursor.png')))