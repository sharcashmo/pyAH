"""Handles Atlantis PBEM structures.

:class:`Structure` represent buildings, roads, ships, ruins, shafts and
so on. A :class:`Structure` is in between of
:class:`~atlantis.gamedata.region.Region` and
:class:`~atlantis.gamedata.unit.Unit` in the Atlantis objects hierarchy.

Each :class:`~atlantis.gamedata.region.Region` can have several
:class:`Structure` objects, which represent places in the
:class:`~atlantis.gamedata.region.Region` where
:class:`~atlantis.gamedata.unit.Unit` stack.
In fact in Atlantis PBEM sourcecode even the
:class:`~atlantis.gamedata.unit.Unit` stacking in
a :class:`~atlantis.gamedata.region.Region` and outside any
:class:`Structure` are actually stacking in an invisible
:class:`Structure` named ``dummy``.

So :class:`Structure` objects are placed into
:class:`~atlantis.gamedata.region.Region` and hold a list of
:class:`~atlantis.gamedata.unit.Unit` objects. In addition
:class:`Structure` has several properties, the most important of them
being its ``num``, and others as their ``structure_type``, ``name`` or
``inner_location``. :class:`Structure` also implements
:class:`~atlantis.helpers.json.JsonSerializable` and
:class:`~atlantis.helpers.comparable.RichComparable` interfaces.

Further details about Atlantis PBEM objects hierarchy can be found at
:ref:`atlantis.gamedata` package documentation.

"""

from atlantis.gamedata.item import ItemAmount

from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing

class Structure(JsonSerializable, RichComparable):
    """Holds all data of a structure.
    
    :class:`Structure` has the following public attributes:
    
    .. attribute:: report
    
       List of report lines describing the :class:`Structure`.
    
    .. attribute:: num
    
       Unique number identifying the :class:`Structure` inside the
       :class:`~atlantis.gamedata.region.Region`.
    
    .. attribute:: name
    
       Name of the :class:`Structure`. Owners of the structure can set
       it.
    
    .. attribute:: structure_type
    
       Type of the :class:`Structure`. This is the name of the
       structure, as **Mine** or **Castle**.
       
    .. attribute:: items
    
       List of :class:`~atlantis.gamedata.item.ItemAmount` elements
       that build the :class:`Structure`. It will only exist in case
       the structure is a fleet of ships.
    
    .. attribute:: incomplete
    
       Amount of work needed to complete the :class:`Structure`. It's
       zero if the :class:`Structure` is finished.
    
    .. attribute:: about_to_decay
    
       Flags if the :class:`Structure` is *about to decay*. A
       :class:`Structure` is *about to decay* if there's a chance the
       :class:`Structure` is completely ruined the next turn if not
       repaired.
    
    .. attribute:: needs_maintenance
    
       Flags if the :class:`Structure` *needs maintenance*. A
       :class:`Structure` *needs maintenance* if it's damaged, but not
       so much that there's a chance the :class:`Structure` is
       completely ruined the next turn if not repaired.
    
    .. attribute:: inner_location
    
       Some :class:`Structure` have inner locations, other
       :class:`~atlantis.gamedata.region.Region` that can be reached
       by moving *in* from inside the :class:`Structure`.
       
       ``inner_location`` will be *False* if :class:`Structure` has no
       inner location, *True* if it has an inner location but it's
       unknown, and the inner location as a three elements tuple if the
       inner location is known. 
    
    .. attribute:: has_runes
    
       Flags if the :class:`Structure` has engraved runes of ward.
    
    .. attribute:: can_enter
    
       Flags if the :class:`Structure` can be entered by players.
       
    """
    
    def __init__(self, num, name, structure_type, items=None, incomplete=False,
                 about_to_decay=False, needs_maintenance=False,
                 inner_location=False, has_runes=False, can_enter=True):
        """Create a new :class:`Structure`.
        
        :param num: unique number identifying the :class:`Structure`.
        :param name: name of the :class:`Structure`.
        :param structure_type: type of the :class:`Structure`.
        :param items: list of
            :class:`~atlantis.gamedata.item.ItemAmount` elements
            that build the :class:`Structure`.
        :param incomplete: amount of work needed to complete the
            :class:`Structure`.
        :param about_to_decay: flags if the :class:`Structure` is
            *about to decay*.
        :param needs_maintenance: flags if the :class:`Structure`
            *needs maintenance*.
        :param inner_location: *False* if the :class:`Structure` has
            no inner location, *True* if it has an inner location but
            it is unknown, and destination location as a three elements
            tuple if known.
        :param has_runes: flags if the :class:`Structure` has engraved
            runes of ward.
        :param can_enter: flags if the :class:`Structure` can be
            entered by players.
        
        """
        
        self.num = num
        self.name = name
        self.structure_type = structure_type
        if items:
            self.items = items
        else:
            self.items = []
        self.incomplete = incomplete
        self.about_to_decay = about_to_decay
        self.needs_maintenance = needs_maintenance
        self.inner_location = inner_location
        self.has_runes = has_runes
        self.can_enter = can_enter
        self.report = []
        self.units = []
        
    def append_report_description(self, line):
        """Append a new report line to :class:`Structure` description.
        
        :param line: report line to be appended to :class:`Structure`
            description.
        
        """
        self.report.append(line)
    
    # JsonSerializable methods
    def json_serialize(self):
        """Return a serializable version of :class:`Structure`.
        
        :return: a *dict* representing the :class:`Structure` object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        json_object = {'num': self.num,
                       'name': self.name,
                       'structure_type': self.structure_type,
                       'incomplete': self.incomplete,
                       'about_to_decay': self.about_to_decay,
                       'needs_maintenance': self.needs_maintenance,
                       'inner_location': self.inner_location,
                       'has_runes': self.has_runes,
                       'can_enter': self.can_enter,
                       'report': self.report}
        
        json_object['items'] = [it.json_serialize() for it in self.items]
#         json_object['units'] = [un.json_serialize() for un in self.units]
                
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Structure` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`Structure` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        items = [ItemAmount.json_deserialize(it) for it in json_object['items']]
        s = Structure(json_object['num'], json_object['name'],
                      json_object['structure_type'], items,
                      json_object['incomplete'], json_object['about_to_decay'],
                      json_object['needs_maintenance'], json_object['inner_location'],
                      json_object['has_runes'], json_object['can_enter'])
        
        s.report = json_object['report']
#         s.units = [Unit.json_deserialize(un) for un in json_object['units']]
        
        return s