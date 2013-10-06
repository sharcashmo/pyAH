"""Unit tests for :mod:`atlantis.helpers.json`."""

from atlantis.helpers.json import json_dump_list
from atlantis.helpers.json import json_load_list
from atlantis.helpers.json import json_dump_dict
from atlantis.helpers.json import json_load_dict
from atlantis.helpers.json import JsonSerializable

from io import StringIO
import json

import unittest


class TestFunctions(unittest.TestCase):
    """Test functions declared at :mod:`atlantis.helpers.json`."""

    def test_json_dump_list(self):
        """Test :func:`json_dump_list`.

        """
        io = StringIO()
        
        my_list = ['a', [1, 2, 3], {'k': 11, 'j': 'pedro'}]
        json_dump_list(io, my_list)
        io.seek(0)
        saved_list = json.load(io)
        self.assertEqual(my_list, saved_list)
        
        class NoSerializableClass():
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_list = [NoSerializableClass('pedro', 'juan'),
                   NoSerializableClass('marta', 'rosa')]
        self.assertRaises(TypeError, json_dump_list, io, my_list)
        
        class VirtualClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_list = [VirtualClass('pedro', 'juan'),
                   VirtualClass('marta', 'rosa')]
        self.assertRaises(NotImplementedError, json_dump_list, io, my_list)
        
        class SerializableClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
            def json_serialize(self):
                return {'a': self.a, 'b': self.b}
            
        io.seek(0)    
        io.truncate(0)
        my_list = [SerializableClass('pedro', 'juan'),
                   SerializableClass('marta', 'rosa')]
        json_dump_list(io, my_list)
        io.seek(0)
        my_list = [{'a': ob.a, 'b': ob.b} for ob in my_list]
        saved_list = json.load(io)
        self.assertEqual(my_list, saved_list)

    def test_json_load_list(self):
        """Test :func:`json_load_list`.

        """
        io = StringIO()
        
        my_list = ['a', [1, 2, 3], {'k': 11, 'j': 'pedro'}]
        json.dump(my_list, io)
        io.seek(0)
        returned_list = json_load_list(io)
        self.assertEqual(my_list, returned_list)
        
        class NoSerializableClass():
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_list = [{'a': 'pedro', 'b': 'juan'},
                   {'a': 'marta', 'b': 'rosa'}]
        json.dump(my_list, io)
        io.seek(0)
        self.assertRaises(TypeError, json_load_list, io, NoSerializableClass)
        
        class VirtualClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_list = [{'a': 'pedro', 'b': 'juan'},
                   {'a': 'marta', 'b': 'rosa'}]
        json.dump(my_list, io)
        io.seek(0)
        self.assertRaises(NotImplementedError, json_load_list,
                          io, VirtualClass)
        
        class SerializableClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
                
            def __eq__(self, other):
                if self.a == other.a and self.b == other.b:
                    return True
                else:
                    return False
            
            @staticmethod
            def json_deserialize(json_object):
                return SerializableClass(**json_object)
            
        io.seek(0)    
        io.truncate(0)
        my_list = [{'a': 'pedro', 'b': 'juan'},
                   {'a': 'marta', 'b': 'rosa'}]
        json.dump(my_list, io)
        io.seek(0)
        my_list = [SerializableClass(**e) for e in my_list]
        returned_list = json_load_list(io, SerializableClass)
        self.assertEqual(returned_list, my_list)

    def test_json_dump_dict(self):
        """Test :func:`json_dump_dict`.

        """
        io = StringIO()
        
        my_dict = dict(zip(('one', 'two', 'three'),
                           ['a', [1, 2, 3], {'k': 11, 'j': 'pedro'}]))
        json_dump_dict(io, my_dict)
        io.seek(0)
        saved_dict = json.load(io)
        self.assertEqual(my_dict, saved_dict)
        
        class NoSerializableClass():
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [NoSerializableClass('pedro', 'juan'),
                            NoSerializableClass('marta', 'rosa')]))
        self.assertRaises(TypeError, json_dump_dict, io, my_dict)
        
        class VirtualClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [VirtualClass('pedro', 'juan'),
                            VirtualClass('marta', 'rosa')]))
        self.assertRaises(NotImplementedError, json_dump_dict, io, my_dict)
        
        class SerializableClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
            def json_serialize(self):
                return {'a': self.a, 'b': self.b}
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [SerializableClass('pedro', 'juan'),
                            SerializableClass('marta', 'rosa')]))
        json_dump_dict(io, my_dict)
        io.seek(0)
        my_dict = dict([(k, {'a': ob.a, 'b': ob.b}) \
                        for (k, ob) in my_dict.items()])
        saved_dict = json.load(io)
        self.assertEqual(my_dict, saved_dict)

    def test_json_load_dict(self):
        """Test :func:`json_load_dict`.

        """
        io = StringIO()
        
        my_dict = dict(zip(('one', 'two', 'three'),
                           ['a', [1, 2, 3], {'k': 11, 'j': 'pedro'}]))
        json.dump(my_dict, io)
        io.seek(0)
        returned_dict = json_load_dict(io)
        self.assertEqual(my_dict, returned_dict)
        
        class NoSerializableClass():
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [{'a': 'pedro', 'b': 'juan'},
                            {'a': 'marta', 'b': 'rosa'}]))
        json.dump(my_dict, io)
        io.seek(0)
        self.assertRaises(TypeError, json_load_dict, io, NoSerializableClass)
        
        class VirtualClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [{'a': 'pedro', 'b': 'juan'},
                            {'a': 'marta', 'b': 'rosa'}]))
        json.dump(my_dict, io)
        io.seek(0)
        self.assertRaises(NotImplementedError, json_load_dict,
                          io, VirtualClass)
        
        class SerializableClass(JsonSerializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b
                
            def __eq__(self, other):
                if self.a == other.a and self.b == other.b:
                    return True
                else:
                    return False
            
            @staticmethod
            def json_deserialize(json_object):
                return SerializableClass(**json_object)
            
        io.seek(0)    
        io.truncate(0)
        my_dict = dict(zip(('one', 'two'),
                           [{'a': 'pedro', 'b': 'juan'},
                            {'a': 'marta', 'b': 'rosa'}]))
        json.dump(my_dict, io)
        io.seek(0)
        my_dict = dict([(k, SerializableClass(**e)) \
                        for (k, e) in my_dict.items()])
        returned_dict = json_load_dict(io, SerializableClass)
        self.assertEqual(returned_dict, my_dict)

if __name__ == '__main__':
    unittest.main()
