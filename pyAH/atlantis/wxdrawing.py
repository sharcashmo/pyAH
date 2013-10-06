import wx

class DoodleWindow(wx.Window):
    colours = ['Black', 'Yellow', 'Red', 'Green', 'Blue', 'Purple', 'Brown',
               'Aquamarine', 'Forest Green', 'Light Blue', 'Goldenrod',
               'Cyan', 'Orange', 'Navy', 'Dark Grey', 'Light Grey']
    thicknesses = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    
    def __init__(self, parent):
        super(DoodleWindow, self).__init__(
                parent, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.initDrawing()
        self.makeMenu()
        self.bindEvents()
        self.initBuffer()
        
    def initDrawing(self):
        self.SetBackgroundColour('WHITE')
        self.currentThickness = self.thicknesses[0]
        self.currentColour = self.colours[0]
        self.lines = []
        self.previousPosition = (0, 0)
    
    def bindEvents(self):
        for event, handler in [
                (wx.EVT_LEFT_DOWN, self.onLeftDown),
                (wx.EVT_LEFT_UP, self.onLeftUp),
                (wx.EVT_MOTION, self.onMotion),
                (wx.EVT_RIGHT_UP, self.onRightUp),
                (wx.EVT_SIZE, self.onSize),
                (wx.EVT_IDLE, self.onIdle),
                (wx.EVT_PAINT, self.onPaint),
                (wx.EVT_WINDOW_DESTROY, self.cleanup)]:
            self.Bind(event, handler)
    
    def initBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.drawLines(dc, *self.lines)
        self.reInitBuffer = False
        
    def makeMenu(self):
        self.menu = wx.Menu()
        self.idToColourMap = self.addCheckableMenuItems(self.menu,
                                                        self.colours)
        self.bindMenuEvents(menuHandler=self.onMenuSetColour,
                            updateUIHandler=self.onCheckMenuColours,
                            ids=self.idToColourMap.keys())
        self.menu.Break()
        self.idToThicknessMap = self.addCheckableMenuItems(self.menu,
                                                           self.thicknesses)
        self.bindMenuEvents(menuHandler=self.onMenuSetThickness,
                            updateUIHandler=self.onCheckMenuThickness,
                            ids=self.idToThicknessMap.keys())
    
    @staticmethod
    def addCheckableMenuItems(menu, items):
        idToItemMapping = {}
        for item in items:
            menuId = wx.NewId()
            idToItemMapping[menuId] = item
            menu.Append(menuId, str(item), kind=wx.ITEM_CHECK)
        return idToItemMapping
    
    def bindMenuEvents(self, menuHandler, updateUIHandler, ids):
        sortedIds = sorted(ids)
        firstId, lastId = sortedIds[0], sortedIds[-1]
        for event, handler in [(wx.EVT_MENU_RANGE, menuHandler),
                               (wx.EVT_UPDATE_UI_RANGE, updateUIHandler)]:
            self.Bind(event, handler, id=firstId, id2=lastId)
    
    def onLeftDown(self, event):
        self.currentLine = []
        self.previousPosition = tuple(event.GetPosition())
        self.CaptureMouse()
        
    def onLeftUp(self, event):
        if self.HasCapture():
            self.lines.append((self.currentColour, self.currentThickness,
                               self.currentLine))
            self.currentLine = []
            self.ReleaseMouse()
    
    def onRightUp(self, event):
        self.PopupMenu(self.menu)
    
    def onMotion(self, event):
        if event.Dragging() and event.LeftIsDown():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            currentPosition = tuple(event.GetPosition())
            lineSegment = self.previousPosition + currentPosition
            self.drawLines(dc, (self.currentColour, self.currentThickness,
                                [lineSegment]))
            self.currentLine.append(lineSegment)
            self.previousPosition = currentPosition
    
    def onSize(self, event):
        self.reInitBuffer = True
        
    def onIdle(self, event):
        if self.reInitBuffer:
            self.initBuffer()
            self.Refresh(False)
    
    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)
        
    def cleanup(self, event):
        if hasattr(self, 'menu'):
            self.menu.Destroy()
            del self.menu
    
    def onCheckMenuColours(self, event):
        colour = self.idToColourMap[event.GetId()]
        event.Check(colour == self.currentColour)
    
    def onCheckMenuThickness(self, event):
        thickness = self.idToThicknessMap[event.GetId()]
        event.Check(thickness == self.currentThickness)
    
    def onMenuSetColour(self, event):
        self.currentColour = self.idToColourMap[event.GetId()]
    
    def onMenuSetThickness(self, event):
        self.currentThickness = self.idToThicknessMap[event.GetId()]
    
    @staticmethod
    def drawLines(dc, *lines):
        for colour, thickness, lineSegments in lines:
            pen = wx.Pen(wx.Colour(colour), thickness, wx.SOLID)
            dc.SetPen(pen)
            for lineSegment in lineSegments:
                dc.DrawLine(*lineSegment)

class DoodleFrame(wx.Frame):
    def __init__(self, parent=None):
        super(DoodleFrame, self).__init__(parent, title='Doodle Frame',
                                          size=(800, 600),
                                          style = wx.DEFAULT_FRAME_STYLE | \
                                                  wx.NO_FULL_REPAINT_ON_RESIZE)
        doodle = DoodleWindow(self)

if __name__ == '__main__':
    app = wx.App()
    frame = DoodleFrame()
    frame.Show()
    app.MainLoop()