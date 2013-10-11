"""Unit tests for :mod:`atlantis.gamedata.item`."""

from atlantis.gamedata.item import ItemRef, ItemAmount, ItemMarket

from io import StringIO

import json
import unittest

class TestItemRef(unittest.TestCase):
    """Test class :class:`atlantis.gamedata.item.ItemRef`."""
    
    def test_constructor(self):
        """Test :class:`~atlantis.gamedata.item.ItemRef` constructor.
        
        Test both forms of constructors, with *name* and *names* as
        parameters.
        
        """
        it = ItemRef('HORS', names='horses')
        
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)
        
        
        it = ItemRef('HORS', name='horse')
        
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.name, 'horse')
        self.assertIsNone(it.names)

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface."""
        io = StringIO()
        
        it = ItemRef('SWOR', name='sword')
        json.dump(it, io, default=ItemRef.json_serialize)
        io.seek(0)
        it_new = ItemRef.json_deserialize(json.load(io))
        
        self.assertEqual(it, it_new)
        

class TestItemAmount(unittest.TestCase):
    """Test class :class:`atlantis.gamedata.item.ItemAmount`."""
    
    def test_constructor(self):
        """Test :class:`~atlantis.gamedata.item.ItemAmount`
        constructor.
        
        Test both forms of constructors, with *name* and *names* as
        parameters, with and without the *amt* parameter.
        
        """
        it = ItemAmount('HORS', amt=5, names='horses')
        
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 5)
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)
        
        
        it = ItemAmount('HORS', name='horse')
        
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 1)
        self.assertEqual(it.name, 'horse')
        self.assertIsNone(it.names)

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface.
        
        """
        io = StringIO()
        
        it = ItemAmount('SWOR', amt=10, names='swords')
        json.dump(it, io, default=ItemAmount.json_serialize)
        io.seek(0)
        it_new = ItemAmount.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)
        
        io.seek(0)
        io.truncate()
        it2 = ItemAmount('SWOR', amt=5, names='swords')
        json.dump(it2, io, default=ItemAmount.json_serialize)
        io.seek(0)
        it_new = ItemAmount.json_deserialize(json.load(io))
        self.assertEqual(it2, it_new)
        self.assertNotEqual(it, it_new)
        

class TestItemMarket(unittest.TestCase):
    """Test class :class:`atlantis.gamedata.item.ItemMarket`."""
    
    def test_constructor(self):
        """Test :class:`~atlantis.gamedata.item.ItemMarket`
        constructor.
        
        Test both forms of constructors, with *name* and *names* as
        paremeters.
        
        """
        it = ItemMarket('HORS', 5, 64, names='horses')
        
        self.assertEqual(it.abr, 'HORS')
        self.assertEqual(it.amt, 5)
        self.assertEqual(it.price, 64)
        self.assertEqual(it.names, 'horses')
        self.assertIsNone(it.name)

    def test_json_methods(self):
        """Test implementation of 
        :meth:`~atlantis.helpers.json.JsonSerializeble` interface.
        
        """
        io = StringIO()
        
        it = ItemMarket('SWOR', 10, 72, names='swords')
        json.dump(it, io, default=ItemMarket.json_serialize)
        io.seek(0)
        it_new = ItemMarket.json_deserialize(json.load(io))
        self.assertEqual(it, it_new)

if __name__ == '__main__':
    unittest.main()
