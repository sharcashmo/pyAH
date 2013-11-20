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
holds and handle all data about these terrain hexes. It implements
:class:`~atlantis.helper.json.JsonSerializable` and
:class:`~atlantis.helper.comparable.RichComparable` interfaces.

"""

from atlantis.gamedata.item import ItemAmount, ItemMarket

from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

class Region(JsonSerializable, RichComparable):
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
       
    .. attribute:: market
    
       Available products in region market. This attribute is a
       dictionary with at most two keys, *sell* and *buy*. Values are a
       list of :class:`~atlantis.gamedata.item.ItemMarket` objects.
    
    .. attribute:: entertainment
    
       Entertainment available in the region.
    
    .. attribute:: products
    
       Available production in region. This attribute is a list of
       :class:`~atlantis.gamedata.item.ItemAmount` objects.
    
    .. attribute:: exits
    
        Available exits from the region. This attribute is dictionary
        with the exit directions are the keys and destination locations
        the values.
        
        Directions are defined in :class:`~atlantis.gamedasta.rules`
        but usually are ``north``, ``northeast``, ``southeast``,
        ``south``, ``southwest`` and ``northwest``.
       
    """
    
    def __init__(self, location, terrain, name=None, population=0,
                  racenames=None, wealth=0, town=None):
        """Create a new region.
        
        Regions will be created by several Atlantis report. When
        reported in battle only location and terrain are given. when
        it's a nearby region we'll get also its name and present
        town, if any. And when we visit the region population and
        wealth information are given.
        
        :param location: location as a three elements tuple, containing
            xloc, yloc and zloc.
        :param terrain: terrain type of the region.
        :param name: name of the region the hexagon belongs to.
        :param population: number of inhabitants of the region.
        :param racenames: name (plural) of the race living in the
            region.
        :param wealth: amount available for taxing.
        :param town: dictionary with *name* and *type* of the town.
        
        """
        
        self.location = tuple(location)
        self.terrain = terrain
        self.name = name
        self.population = population
        self.racenames = racenames
        self.wealth = wealth
        self.town = town
        self.report = []
        
    def append_report_description(self, line):
        """Append a new report line to item description.
        
        :param line: report line to be appended to item description.
        
        """
        self.report.append(line)
    
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
    
    def set_entertainment(self, amount):
        """Set region entertainment.
        
        :param amount: entertainment available in , 'location': the region.
        
        """
        self.entertainment = amount
    
    def set_products(self, products):
        """Set region production available.
        
        :param products: list of
            :class:`~atlantis.gamedata.item.ItemAmount` objects.
        
        """
        self.products = products
    
    def set_exit(self, direction, location):
        """Set an exit from the region.
        
        :param direction: a string with the direction of the exit.
        :param location: location the exit leads to as a three elements
            tuple.
        
        """
        try:
            self.exits[direction] = location
        except AttributeError:
            self.exits = {direction: location}
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`Region`.
        
        :return: a *dict* representing the :class:`Region` object.
        
        .. seealso::
           :meth:`JsonSerializable.json_serialize`
        
        """
        json_object = {'location': self.location,
                       'terrain': self.terrain,
                       'name': self.name,
                       'population': self.population,
                       'racenames': self.racenames,
                       'wealth': self.wealth,
                       'town': self.town,
                       'report': self.report}
        try:
            json_object['weather'] = self.weather
        except AttributeError:
            pass
        try:
            json_object['wages'] = self.wages
        except AttributeError:
            pass
        try:
            md = self.market
        except AttributeError:
            pass
        else:
            json_object['market'] = dict()
            for k in md:
                json_object['market'][k] = [it.json_serialize() \
                                            for it in md[k]]
        try:
            json_object['entertainment'] = self.entertainment
        except AttributeError:
            pass
        try:
            json_object['products'] = [pr.json_serialize() \
                                       for pr in self.products]
        except AttributeError:
            pass
        try:
            json_object['exits'] = self.exits
        except AttributeError:
            pass
                
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Region` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`Region` object from json data.
        
        .. seealso::
           :meth:`JsonSerializable.json_deserialize`
        
        """
        r = Region(json_object['location'], json_object['terrain'],
                   json_object['name'], json_object['population'],
                   json_object['racenames'], json_object['wealth'],
                   json_object['town'])
        if 'report' in json_object.keys():
            r.report = json_object['report']
        if 'weather' in json_object.keys():
            r.weather = json_object['weather']
        if 'wages' in json_object.keys():
            r.wages = json_object['wages']
        if 'market' in json_object.keys():
            r.market = dict()
            for mtype, mlist in json_object['market'].items():
                r.market[mtype] = [ItemMarket.json_deserialize(it) \
                                   for it in mlist]
        if 'entertainment' in json_object.keys():
            r.entertainment = json_object['entertainment']
        if 'products' in json_object.keys():
            r.products = [ItemAmount.json_deserialize(it) \
                          for it in json_object['products']]
        if 'exits' in json_object.keys():
            r.exits = dict([(k, tuple(loc)) \
                            for k, loc in json_object['exits'].items()])
            
        return r
    
    def update(self, region):
        """Update region with new data.
        
        This method will update current region with new data about
        the region. New data can be partial, so not all old data will
        be overwritten.
        
        :param region: A :class:`Region` object with new data.
        :raise: :class:`KeyError` if region it's not the same
            (locations does not coincide).
        
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