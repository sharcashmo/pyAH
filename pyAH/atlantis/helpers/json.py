""":mod:atlantis.helper.json provides helper functions and interfaces
for loading and reading game objects from and into json files."""

import json

def json_dump_list(file, object_list):
    """Save a list of :class:`JsonSerializable` objects into a file.
    
    This function saves a list of :class:`JsonSerializable` objects
    as json into the file-like object give as its first parameter.
    
    If objects in *object_list* doesn't implement
    :class:`JsonSerializable` interface :func:`json_dump_list` tries
    to dump the object directly, raising :exc:`TypeError` if not
    possible.
    
    :param file: file-like object where the json will be saved into.
    :param object_list: list of objects implementing
        :class:`JsonSerializable` interface.
    
    :raise: class:`NotImplementedError` if
        :meth:`JsonSerializable.json_serialize` is not implemented.
    :raise: class:`TypeError` if elements in *object_list* are not
        serializable nor implement :class:`JsonSerializable` interface. 
    
    """
    try:
        serializable_list = [ob.json_serialize() for ob in object_list]
    except AttributeError:
        serializable_list = object_list[:]
        
    json.dump(serializable_list, file)

def json_load_list(file, serializable_class=None):
    """Load a list of objects from a json file.
    
    This function loads a list of objects from a json file. The objects
    can be primitive objects serializable by :func:`json.dump`, in
    which case *deserialize_func* will be None, or can be a instance
    of :class:`JsonSerializable` interface, in which case objects will
    be build from json data calling
    :meth:`JsonSerializable.json_deserialize` on the target class.
    
    :param file: file-like object where json data will be read from.
    :param serializable_class: class of the objects in the list. Must
        implement :class:`JsonSerializable` interface.
    
    :return: the list of objects
    
    :raise: :class:`NotImplementedError` if
        :meth:`JsonSerializable.json_deserialize` is not overriden.
    :raise: :class:`TypeError` if *serializable_class* does not
        implements :class:`JsonSerializable`.
    
    """
    read_list = json.load(file)
    if serializable_class:
        try:
            read_list = [serializable_class.json_deserialize(o) \
                         for o in read_list]
        except AttributeError:
            raise TypeError('non JsonSerializable class')
        except:
            raise
    return read_list

def json_dump_dict(file, object_dict):
    """Save a dictionary of :class:`JsonSerializable` into a file.
    
    This function saves a dictionary of :class:`JsonSerializable`
    objects as json into the file-like object give as its first
    parameter.
    
    If objects in *object_dict* doesn't implement
    :class:`JsonSerializable` interface :func:`json_dump_dict` tries
    to dump the object directly, raising :exc:`TypeError` if not
    possible.
    
    :param file: file-like object where the json will be saved into.
    :param object_dict: dictionary of objects implementing
        :class:`JsonSerializable` interface.
    
    :raise: :class:`NotImplementedError` if
        :meth:`JsonSerializable.json_serialize` is not implemented.
    :raise: :class:`TypeError` if elements in *object_dict* are not
        serializable nor implement :class:`JsonSerializable` interface. 
    
    """
    try:
        serializable_dict = dict([(k, ob.json_serialize()) \
                                 for (k, ob) in object_dict.items()])
    except AttributeError:
        serializable_dict = object_dict.copy()
        
    json.dump(serializable_dict, file)

def json_load_dict(file, serializable_class=None):
    """Load a dictionary of objects from a json file.
    
    This function loads a dictionary of objects from a json file. The
    objects can be primitive objects serializable by :func:`json.dump`,
    in which case *deserialize_func* will be None, or can be a instance
    of :class:`JsonSerializable` interface, in which case objects will
    be build from json data calling
    :meth:`JsonSerializable.json_deserialize` on the target class.
    
    :param file: file-like object where json data will be read from.
    :param serializable_class: class of the objects in the dictionary.
        Must implement :class:`JsonSerializable` interface.
    
    :return: the dictionary of objects
    
    :raise: :class:`NotImplementedError` if
        :meth:`JsonSerializable.json_deserialize` is not overriden.
    :raise: :class:`TypeError` if *serializable_class* does not
        implements :class:`JsonSerializable`.
    
    """
    read_dict = json.load(file)
    if serializable_class:
        try:
            read_dict = dict([(k, serializable_class.json_deserialize(o)) \
                             for (k, o) in read_dict.items()])
        except AttributeError:
            raise TypeError('non JsonSerializable class')
        except:
            raise
    return read_dict


class JsonSerializable():
    """Interface for objects serializable into a json file.
    
    This object defines the public methods that have to be overriden by
    classes implementing :class:`JsonSerializable` interface.
    
    """
        
    def json_serialize(self):
        """Return a serializable version of current object.
        
        Returned object should be serializable by :func:`json.dump`
        
        :return: Serializable object.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('json_serialize must be overriden')
    
    @staticmethod
    def json_deserialize(json_object):
        """Load object from a deserialized json object.
        
        This method should load object from data returned by
        :func:`json.load`.

        :param json_object: object returned by :func:`json.load`.
        
        :return: the :class:`JsonSerializable` object from json data.
        
        :raise: :class:`NotImplementedError` if not overriden.
        
        """
        raise NotImplementedError('json_deserialize must be overriden') 