"""Handles Atlantis PBEM items.

*Items* are one the main entities in Atlantis PBEM. Men, monsters, raw
materials, manufactured items, weapons, money, ships, etc. All of them
are items.

*Items* are the smaller pieces in Atlantis PBEM. *Units* can be thought
as list of items, and *items* forming them are what give these *units*
their main stats.

Main class in :mod:`atlantis.gamedata.item` is :class:`ItemDef`, which
holds and handle all data about an item type definition.

In addition some more classes are defined to hold actual items in game,
as they're :class:`ItemRef`, :class:`ItemAmount` and
:class:`ItemMarket`.

"""

from atlantis.helpers.comparable import RichComparable

class ItemRef(RichComparable):
    """Item reference.
    
    This class holds any reference to an item: an item is referenced by
    its abbreviature and its name or names (depending on the context).
    *abr* is always present, but only one of *name* or *names* will be
    given.
    
    Public attributes of :class:`ItemRef` are:
    
    .. attribute:: abr
    
       Four (or less) characters abbreviature of the item, as ``hors``.
       
    .. attribute:: name
    
       Singular name of the item, as ``horse``.
    
    .. attribute:: names
    
       Plural name of the item, as ``horses``.
    
    """
    def __init__(self, abr, name=None, names=None):
        """:class:`ItemRef` constructor.
        
        :param abr: abbreviature of the item.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        self.abr = abr
        self.name = name
        self.names = names

class ItemAmount(ItemRef):
    """Item amount.
    
    This class holds any reference to a number of items. This can
    appear in any entity description formed by a number of items, as
    units descriptions, region products, etc.
    
    This class extends :class:`ItemRef` adding an amount attribute.
    
    Public attributes in addition to those defined in :class:`ItemRef`:
    
    .. attribute:: amt
    
       Number of items.
    
    """
    def __init__(self, abr, amt=1, name=None, names=None):
        """:class:`ItemAmount` constructor.
        
        :param abr: abbreviature of the item.
        :param amt: number of items.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        ItemRef.__init__(self, abr, name, names)
        self.amt = amt

class ItemMarket(ItemAmount):
    """Items in market.
    
    This class holds information about items in a market. This class
    extends :class:`ItemAmount` adding a price attribute.
    
    Public attributes in addition to those defined in
    :class:`ItemAmount`:
    
    .. attribute:: price
    
       Price of the item.
    
    """
    def __init__(self, abr, amt, price, name=None, names=None):
        """:class:`ItemAmount` constructor.
        
        :param abr: abbreviature of the item.
        :param amt: number of items.
        :param price: price of the item.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        ItemAmount.__init__(self, abr, amt, name, names)
        self.price = price