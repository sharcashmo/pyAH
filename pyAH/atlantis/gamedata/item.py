"""Handles Atlantis PBEM items.

*Items* are one the main entities in Atlantis PBEM. Men, monsters, raw
materials, manufactured items, weapons, money, ships, etc. All of them
are items.

*Items* are the smaller pieces in Atlantis PBEM. *Units* can be thought
as list of items, and *items* forming them are what give these *units*
their main stats.

This module does not have information about *items* characteristics.
That is handled by :class:`atlantis.gamedata.rules.ItemType`. Classes
defined in :mod:`atlantis.gamedata.item`, instead, reference actual
instances of *items* in the game.

Actual *items* form *units*, are sold in *markets*, produced by
*regions*, etc, and this data is managed by
:mod:`atlantis.gamedata.item`.

"""


from atlantis.helpers.json import JsonSerializable
from atlantis.helpers.comparable import RichComparable # For testing


class Item(JsonSerializable, RichComparable):
    """Item reference.
    
    This class holds any reference to an item: an item is referenced by
    its abbreviature and its name or names (depending on the context).
    *abr* is always present, but only one of *name* or *names* will be
    given.
    
    Public attributes of :class:`Item` are:
    
    .. attribute:: abr
    
       Four (or less) characters abbreviature of the item, as ``hors``.
       
    .. attribute:: name
    
       Singular name of the item, as ``horse``.
    
    .. attribute:: names
    
       Plural name of the item, as ``horses``.
    
    """
    def __init__(self, abr=None, name=None, names=None):
        """:class:`Item` constructor.
        
        :param abr: abbreviature of the item.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        self.abr = abr
        self.name = name
        self.names = names
    
    def json_serialize(self):
        """Return a serializable version of :class:`Item`.
        
        :return: a *dict* representing the :class:`Item`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return {'abr': self.abr, 'name': self.name, 'names': self.names}
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`Item` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`Item` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return Item(**json_object)


class ItemAmount(Item):
    """Item amount.
    
    This class holds any reference to a number of items. This can
    appear in any entity description formed by a number of items, as
    units descriptions, region products, etc.
    
    This class extends :class:`Item` adding an amount attribute.
    
    Public attributes in addition to those defined in :class:`Item`:
    
    .. attribute:: amt
    
       Number of items.
    
    """
    def __init__(self, abr=None, amt=1, name=None, names=None):
        """:class:`ItemAmount` constructor.
        
        :param abr: abbreviature of the item.
        :param amt: number of items.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        Item.__init__(self, abr, name, names)
        self.amt = amt
    
    def json_serialize(self):
        """Return a serializable version of :class:`ItemAmount`.
        
        :return: a *dict* representing the :class:`ItemAmount`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        json_object = Item.json_serialize(self)
        json_object.update(amt=self.amt)
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`ItemAmount` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`ItemAmount` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return ItemAmount(**json_object)


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
        """:class:`ItemMarket` constructor.
        
        :param abr: abbreviature of the item.
        :param amt: number of items.
        :param price: price of the item.
        :param name: singular name of the item.
        :param names: plural name of the item.
        
        """
        ItemAmount.__init__(self, abr, amt, name, names)
        self.price = price
    
    def json_serialize(self):
        """Return a serializable version of :class:`ItemMarket`.
        
        :return: a *dict* representing the :class:`ItemMarket`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        json_object = ItemAmount.json_serialize(self)
        json_object.update(price=self.price)
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`ItemMarket` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`ItemMarket` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return ItemMarket(**json_object)


class ItemUnit(ItemAmount):
    """Items in an unit.
    
    This class holds information about items in an unit. This class
    extends :class:`ItemAmount` adding information about it's
    finished of unfinished, and if it's an illusion.
    
    Public attributes in addition to those defined in
    :class:`ItemAmount`:
    
    .. attribute:: unfinished
    
       Amount of work needed to finish the item.
    
    .. attribute:: illusion
    
       *True* if the item is an illusion.
    
    """
    def __init__(self, abr, amt, name=None, names=None,
                 unfinished=0, illusion=False):
        """:class:`ItemUnit` constructor.
        
        :param abr: abbreviature of the item.
        :param amt: number of items.
        :param name: singular name of the item.
        :param names: plural name of the item.
        :param unfinished: amount of work needed to finish the item.
        :param illusion: *True* if the item is an illusion.
        
        """
        
        ItemAmount.__init__(self, abr, amt, name, names)
        self.unfinished = unfinished
        self.illusion = illusion
    
    def json_serialize(self):
        """Return a serializable version of :class:`ItemUnit`.
        
        :return: a *dict* representing the :class:`ItemUnit`
            object.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        
        json_object = ItemAmount.json_serialize(self)
        json_object.update(unfinished=self.unfinished, illusion=self.illusion)
        return json_object
    
    @staticmethod
    def json_deserialize(json_object):
        """Load :class:`ItemUnit` from a deserialized json object.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`ItemUnit` object from json data.
        
        .. seealso::
           :class:`atlantis.helpers.json.JsonSerializable`
        
        """
        return ItemUnit(**json_object)