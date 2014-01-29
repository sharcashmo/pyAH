"""This module implements an Atlantis game data manager.

Main class defined in this module is :class:`GameData`. This class has
two major functions:

#. :class:`GameData` implements
   :class:`~atlantis.parsers.reportparser.ReportConsumer` interface, so
   data parsed from report is directly readed by this class.

#. :class:`GameData` acts as the repository of one turn data. It holds
   faction data, map data, structure, items and skills definitions, etc.
    
"""

from atlantis.parsers.reportparser import ReportConsumer
from atlantis.gamedata.map import Map, HEX_EXITS
from atlantis.gamedata.region import Region
from atlantis.gamedata.structure import Structure
from atlantis.gamedata.rules import StructureType

_SHIP_ID_OFFSET = 100

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
    
    # Current structure
    _structure = None
    
    # Last line read
    _line = None
    
    def __init__(self, rules):
        """:class:`GameData` constructor.
        
        Creates a new :class:`GameData` instance.
        
        :param rules: a :class:`~atlantis.gamedata.rules.AtlantisRules`
            object with the set of rules to be used
            
        """
        
        self.map = Map()
        self.rules = rules
        self.structures = dict()
        self.unknown_structures = list()
    
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
        self._structure = None
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
        
        self._region.set_exit(self.rules.get_direction(direction),
                              (xloc, yloc, zloc))
        self.map.add_region_info(Region((xloc, yloc, zloc), terrain, name,
                                        town=town), HEX_EXITS)
    
    def region_gate(self, gate, gateopen):
        """Handle a gate report.
        
        If a gate is found in the region it is reported.
        
        :param gate: gate number, or 0 if it's closed.
        :param gateopen: *True* if the gate is open, *False* otherwise.
        
        """
        self._region.set_gate(gate, gateopen)
    
    def region_structure(self, num, name, structure_type, items=None,
                           incomplete=False, about_to_decay=False,
                           needs_maintenance=False, inner_location=False,
                           has_runes=False, can_enter=True):
        """Handle a structure in a region report.
        
        A structure is a complex entity in Atlantis. Structures can
        hold player or monster units inside, open paths to other map
        levels, improve resource production, provide protection to
        soldiers inside or, in case of ships, provide sailing or even
        flying transportation.
        
        When a region report is finished with their products listing
        it's time for units and structures. First all units outside
        structures are listed, then each object, followed by their
        stacked units.
        
        :param num: unique number for the structure in the hex.
            Structures will be listed ordered by its number, and it's
            the direction unit must issue in order to enter inside it.
        :param name: name of the structure. Note that this is the name
            given by the owner player to the structure, not the name of
            the structure type.
        :param structure_type: *name* of the structure type.
            This *name* is the generic structure type (like **Mine** or
            **Castle**).
        :param items: list of
            :class:`~atlantis.gamedata.item.ItemAmount` elements.
            ``items`` is only set when the structure is a fleet of
            ships, otherwise is set to *None*. Defaults to *None*.
        :param incomplete: amount of work needed to complete the
            structure. Defaults to zero.
        :param about_to_decay: flags if the structure is *about to
            decay*. A structure is *about to decay* if there's a chance
            the structure is completely ruined the next turn if not
            repaired. Defaults to *False*.
        :param needs_maintenance: glags if the structure *needs
            maintenance*. A structure *needs maintenance* if it's
            damaged but not so much that there's a chance it will be
            completely ruined the next turn if not repaired. Defaults to
            *False*.
        :param inner_location: *True* if the structure has an inner
            location, *False* otherwise. Defaults to *False*.
        :param has_runes: *True* if the structure has engraved runes of
            guard, *False* otherwise. Defaults to *False*.
        :param can_enter: *True* if player units can enter the
            structure, *False* otherwise. Defaults to *True*.
                
        """
        
        if self._descr_in_region:
            self._region.pop_report_description()
            self._descr_in_region = False
        
        if num >= _SHIP_ID_OFFSET:
            self.update_structure_definitions(structure_type, ship=True)
        else:
            self.update_structure_definitions(structure_type, ship=False)

        structure = Structure(num, name, structure_type, items,
                              incomplete, about_to_decay,
                              needs_maintenance, inner_location,
                              has_runes, can_enter)
        structure.append_report_description(self._line)
        
        self._structure = structure
        self._region.append_structure(structure)
        
    def structure(self, name, structuretype,
                  monster=False, nomonstergrowth=False, canenter=False,
                  nobuildable=False,
                  protect=None, defense=None, maxMages=None,
                  specials=None, sailors=None, productionAided=None,
                  neverdecay=False, maxMaintenance=None, maxMonthlyDecay=None,
                  maintFactor=None, maintItem=None):
        """Handle a structure definition.
        
        Structures are places were units can enter into. Main types
        of structures are buildings and ships. Some of them have
        inner locations, like passages into underworld, some are monster
        lairs, forts and castles, production buildings like mines, etc.
        
        :param name: name of the structure type.
        :param structuretype: type of the structure. Can be
            **building**, **ship** or **group of ships**.
        :param monster: *True* if it's a monster lair.
        :param nomonstergrowth: *True* if monsters in this structure
            won't regenerate.
        :param canenter: *True* if player units can enter the structure.
        :param nobuildable: *True* if the structure cannot be built by
            players.
        :param protect: number of soldiers the structure can protect.
        :param defense: defense bonus granted to the soldiers protected
            by the structure. It's a dictionary where keys are the
            attack types and values the bonus granted.
        :param maxMages: number of mages that can study inside the
            structure magic skills beyond 2nd level.
        :param specials: list of special effects affected by the
            structure. Each element in the list is a dictionary with two
            keys:
            
            *specialname*
                name of the special effect affected of the structure.
            *affected*
                if *True*, units inside this structure are affected by
                the special. If *False*, units inside the structure are
                not affected by it.
        :param sailors: number of sailors needed to sail the ship. Only
            for ship structures.
        :param productionAided: *names* string of the item the structure
            aids to produce. *entertainment* is an allowed special value.
        :param neverdecay: *True* if the structure never decay.
        :param maxMaintenance: maximum points of damage taken by the
            structure before it begins to decay.
        :param maxMonthlyDecay: maximum damage the structure will take
            per month as decay.
        :param maintFactor: damage repaired per unit of material used.
        :param maintItem: *name* string of the item used to repair the
            structure. *wood or stone* is a valid special value.
            
        """
        
        self.structures[name] = StructureType(name, structuretype)
        self.update_structure_definitions(structuretype)
        
    # Methods handling definitions
    def update_item_definitions(self, items):
        pass
    
    def update_structure_definitions(self, structure_type, ship=False):
        pass