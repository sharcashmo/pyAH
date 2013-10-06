"""Handles Atlantis PBEM regions.

*Regions* (hexes) are one the main entities in Atlantis PBEM. All game
action takes place in an hexagonal map made of :class:`Region`
elements. Each of these *regions* has a list of :class:`Structure`
*structures*, and each of these *structures* has a list of
:class:`Unit` *units* inside.

*Regions* represent the main point where players interact with
surrounding world. They provide the players of money throught taxing
or Region's markets, control movement, are battle fields, etc.

Main class in :mod:`atlantis.gamedata.region` is :class:`Region`, which
holds and handle all data about these terrain hexes.

"""

class Region():
    """Holds all data of an Atlantis PBEM region.
    
    :class:`Region` has the following public attributes:
    
    .. attribute:: report
       List of report lines describing the region.
    
    .. attribute:: location
       Region location, as a three elements tuple.
    
    .. attribute:: terrain
       Terrain type of the region.
       
    .. attribute:: name
       Name of the region.
    
    .. attribute:: population
       Inhabitants in the region.
    
    .. attribute:: racenames
       Name (plural) of the race living in the region.
    
    .. attribute:: wealth
       Amount available for taxing.
    
    .. attribute:: town
       Dictionary with *name* and *type* of the present town if any.
    
    .. attribute:: entertainment
       Entertainment available in the region.
    
    .. attribute:: weather
       Dictionary with *last*, *next*, *clearskies* and *blizzard*.
       First two keys are weather for *last* and *next* month
       respectively, while the latter are flags telling if last
       month weather was caused by ``Clear Skies`` or ``Blizzard``
       spells.
    
    .. attribute:: wages
       Wages available in the region. It's a dictionary with
       *productivity* and *amount* values. The first is the amount
       received per man and month by work, while the latter is the
       maximum total amount available in the region.
       
    """
    
    def __init__(self, location, terrain, name=None, population=0,
                  racenames=None, wealth=0, town=None):
        """Create a new region.
        
        Regions will be created by several Atlantis report. When
        reported in battle only location and terrain are given. when
        it's a nearby region we'll get also its name and present
        town, if any. And when we visit the region population and
        wealth information are given.
        
        :param location: Location as a three elements tuple, containing
            xloc, yloc and zloc.
        :param terrain: Terrain type of the region.
        :param name: Name of the region the hexagon belongs to.
        :param population: Number of inhabitants of the region.
        :param racenames: Name (plural) of the race living in the
            region.
        :param wealth: Amount available for taxing.
        :param town: Dictionary with *name* and *type* of the town.
        
        """
        
        self.location = tuple(location)
        self.terrain = terrain
        self.name = name
        self.population = population
        self.racenames = racenames
        self.wealth = wealth
        self.town = town
    
    def set_report_description(self, line):
        """Set a new description string from read report line.
        
        :param line: report line describing the item.
        
        """
        self.report = [line]
        
    def append_report_description(self, line):
        """Append a new report line to item description.
        
        :param line: report line to be appended to item description.
        
        """
        self.report.append(line)
    
    def set_entertainment(self, amount):
        """Set region entertainment.
        
        :param amount: Entertainment available in the region.
        
        """
        self.entertainment = amount
    
    def set_weather(self, weather, nxtweather,
                      clearskies=False, blizzard=False):
        """Set region weather information.
        
        :param weather: last month weather. Valid values are **clear**,
            **winter**, **monsoon season** and **blizzard**.
        :param nxtweather: next month weather. Valid values are
            **clear**, **winter** and **monsoon season**. Unnatural
            values are not allowed here.
        :param clearskies: if *True*, last month weather was caused by
            a Clear Skies spell. Defaults to *False*.
        :param blizzard: if *True*, last month weather was caused by a
            Blizzard spell. Defaults to *False*.
        
        """
        self.weather = {'last': weather, 'next': nxtweather,
                        'clearskies': clearskies, 'blizzard': blizzard}
    
    def set_wages(self, productivity, amount):
        """Set region wages.
        
        :param productivity: wages obtained per man and month.
        :param amount: total amount of wages available in the region.
        
        """
        self.wages = {'productivity': productivity, 'amount': amount}
    
    def set_market(self, market, items):
        """Set region market.
        
        :param market: market type. Allowed values are ``sell`` and
            ``buy``.
        :param items: list of
            :class:`~atlantis.gamedata.item.ItemMarket` objects.
        
        """
        try:
            self.market[market] = items
        except AttributeError:
            self.market = {market: items}
    
    def update(self, region):
        """Update region with new data.
        
        This method will update current region with new data about
        the region. New data can be partial, so not all old data will
        be overwritten.
        
        :param region: A :class:`Region` object with new data.
        :raise: `KeyError` if region it's not the same (locations does
            not coincide).
        
        """
        if region.location != self.location:
            raise KeyError('Regions are not the same')
        
        if region.name:
            self.name = region.name
            self.town = region.town
        
        if region.racenames:
            self.racenames = region.racenames
            self.population = region.population
            self.wealth = region.wealth