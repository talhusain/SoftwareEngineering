"""
All plugin related logic should go here.
This file might eventually need broken into a seperate package,
depending on how complex it gets.
"""

from db import Database

class Loader(object):
    def __init__(self, db):
        self._db = db
        self._load_plugins()
    def _load_plugins(self):
        pass


class RegistryHolder(type):

    REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        """
        Here the name of the class is used as key but it could be any class
        parameter.
        """
        
        cls.REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        return dict(cls.REGISTRY)


class Plugin:
    __metaclass__ = RegistryHolder
    """
    Any class that will inherits from Plugin will be included inside the dict
    RegistryHolder.REGISTRY, the key being the name of the class and the
    associated value, the class itself.
    """
    pass