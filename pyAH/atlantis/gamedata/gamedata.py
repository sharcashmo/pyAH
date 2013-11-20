"""This module implements an Atlantis game data manager.

Main class defined in this module is
:class:`~atlantis.gamedata.gamedata.GameData`, a class that implements
:class:`atlantis.parsers.reportparser.ReportConsumer` and thus will
hold all data read from Atlantis PBEM reports."""

from atlantis.parsers.reportparser import ReportConsumer
from atlantis.gamedata.map import Map, HEX_EXITS
from atlantis.gamedata.region import Region

class GameData(ReportConsumer):
    """This class hold all data of an Atlantis PBEM game.
    
    It implements
    :class:`~atlantis.parsers.reportparser.ReportConsumer`
    interface defined in :mod:`atlantis.parsers.reportparser` module,
    so it will be in charge of handling data parsed by 
    :class:`~atlantis.parsers.reportparser.ReportParser`.
    
    All objects managed by
    :class:`~atlantis.gamedata.gamedata.GameData` mimics as much as
    possible the structure in Atlantis PBEM source code, to make it
    easier to implement simulation engines of any type (battle or
    economic simulators).
    
    """
    
    # Current region
    _region = None
    _descr_in_region = False
    
    # Last line read
    _line = None
    
    def __init__(self):
        self.map = Map()
    
    def line(self, line):
        """Handle a new line.
        
        Whenever a line is read, it is sent to the consumer in case
        it wants to use it for the read entity description.
        
        The line is send just before the parsed object is sent to
        the consumer, so it should store it in a temporary buffer,
        and when the parsed entity is received attach the line(s)
        to it as a description.
        
        :param line: read line.
            
        """
        self._line = line
        if self._descr_in_region:
            self._region.append_report_description(self._line)
            
    
    def region(self, terrain, name, xloc, yloc, zloc=None,
                population=0, racenames=None, wealth=0, town=None):
        """Handle first line of region report.
        
        Implements
        :meth:`ReportConsumer.region
        <atlantis.parsers.reportparser.ReportConsumer.region>`.
        See this method documentation for further information.
        
        :param xloc: X coordinates of the hexagon.
        :param yloc: Y coordinates of the hexagon.
        :param zloc: Z coordinates of the hexagon. If *None* is given
            the hexagon is on surface.
        :param terrain: Terrain type.
        :param name: Region name the hexagon belongs to.
        :param population: Population of the hexagon, if any. Some
            terrain types as oceans have no population.
        :param racenames: Name of the race (plural form) of region
            inhabitants.
        :param wealth: Maximum amount available for taxing.
        :param town: If present, a dictionary with *name* and *type* of
            the town there. Allowed *type* values are ``village``,
            ``town`` and ``city``.
        
        """
        
        self._region = Region((xloc, yloc, zloc), terrain, name,
                              population, racenames, wealth, town)
        self._region.append_report_description(self._line)
        self._descr_in_region = True
        self.map.add_region_info(self._region)
    
    def region_weather(self, weather, nxtweather,
                         clearskies=False, blizzard=False):
        """Handle region weather report.
        
        Reports last and next month weather. Next month weather will be
        the one affecting movement orders given this turn. Weather can
        be ``clear``, ``winter``, ``monsoon season`` or ``blizzard``.
        
        Also, if weather was affected by magic it is also reported.
        
        :param weather: last month weather. Valid values are ``clear``,
            ``winter``, ``monsoon season`` and ``blizzard``.
        :param nxtweather: next month weather. Valid values are
            ``clear``, ``winter`` and ``monsoon season``. Unnatural
            values are not reported here.
        :param clearskies: if *True*, last month weather was caused by
            a Clear Skies spell. Defaults to *False*.
        :param blizzard: if *True*, last month weather was caused by a
            Blizzard spell. Defaults to *False*.
                
        """
        self._region.set_weather(weather, nxtweather, clearskies, blizzard)
    
    def region_wages(self, productivity, amount):
        """Handle region wages report.
        
        This method report wages per month, and total available amount.
        Wages are a float value with one decimal value (ex. $14.3), but
        the total amount are truncated per unit.
        
        :param productivity: wages obtained per man and month.
        :param amount: total amount of wages available in the region.
        
        """
        self._region.set_wages(productivity, amount)
    
    def region_market(self, market, items):
        """Handle region market report.
        
        This method is called up to twice per region. One for the sell
        market (products that players can *sell* to the market) and one
        for the buy market (products that players can *buy* from the
        market). Each market is a list of items with their sell/buy
        prices.
        
        :param market: market type. Allowed values are ``sell`` and
            ``buy``.
        :param items: list of
            :class:`~atlantis.gamedata.item.ItemMarket` objects.
        
        """
        self.update_item_definitions(items)
        self._region.set_market(market, items)
    
    def region_entertainment(self, amount):
        """Handle region entertainment report.
        
        Implements
        :meth:`ReportConsumer.region_entertainment
        <atlantis.parsers.reportparser.ReportConsumer.region>`.
        See this method documentation for further information.
        
        :param amount: Entertainment available in the region.
        
        """
        self._region.set_entertainment(amount)
    
    def region_products(self, products):
        """Handle region products report.
        
        The only parameter of this method is a list of available
        products in the region.
        
        New products can be discovered in the region when units get
        the appropiate skill.
        
        :param products: list of
            :class:`~atlantis.gamedata.item.ItemAmount` objects.
        
        """
        self._region.set_products(products)
        self._descr_in_region = False
    
    def region_exits(self, direction, terrain, name,
                     xloc, yloc, zloc='surface', town=None):
        """Handle a region exit direction.
        
        Each region has a number of linked hexagons. Each of them
        are reported by calling this method. When an exit is found some
        basic information of the linked hexagon is attached.
        
        :param direction: direction of the exit. Allowed values are
            ``North``, ``Northeast``, ``Southeast``, ``South``,
            ``Southwest``, ``Northwest``. 
        :param xloc: X coordinates of the hexagon.
        :param yloc: Y coordinates of the hexagon.
        :param zloc: Z coordinates of the hexagon. If *None* is given
            the hexagon is on surface.
        :param terrain: terrain type.
        :param name: region name the hexagon belongs to.
        :param town: if present, a dictionary with *name* and *type* of
            the town there. Allowed *type* values are ``village``,
            ``town`` and ``city``.
        
        """
        
        self._region.set_exit(direction.lower(), (xloc, yloc, zloc))
        self.map.add_region_info(Region((xloc, yloc, zloc), terrain, name,
                                        town=town), HEX_EXITS)
        
    # Methods handling definitions
    def update_item_definitions(self, items):
        pass