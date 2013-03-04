# coding: utf-8
from copy import (copy)

class Nothing(object):
    """ A sentinal object for when things don't exist. """
    pass

class Stack(list):
    """ A simple wrapper for lists, providing nicer
    semantics for accessing the last element and alternate
    syntax for appending items. """
    def __init__(self, obj=Nothing, *args, **kwargs):
        super(list, self).__init__(*args, **kwargs)
        if obj is not Nothing:
            self.append(obj)
    
    def __call__(self, _copy=False):
        if not _copy:
            return self[-1]
        return copy(self[-1])

    def push(self, *args, **kwargs):
        return self.append(*args, **kwargs)

