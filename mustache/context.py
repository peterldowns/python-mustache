# coding: utf-8
from stack import (Stack)

class Context(object):
    """ Essentially a wrapper around a Stack of dictionaries,
    this object is used to hold variable information for use in
    templates. Every {{key}} in a template is looked up within
    a Context. """

    default = "" # what to return when no match is found (according to spec)
    def __init__(self, context=None, **kwargs):
        context = context or {}
        context.update(kwargs)
        self.stack = Stack(context)
    
    def push(self, key):
        return self.stack.push(key)

    def pop(self, index=-1):
        return self.stack.pop(index)

    def __call__(self, *args, **kwargs):
        return self.stack(*args, **kwargs)

    def get(self, key, default=""):
        default = getattr(self, 'default', default)
        return self.get_or_attr(key, default)
        #attr = self.get_or_attr(key, default)
        #if hasattr(attr, '__call__'):
        #    return attr()
        #return attr

    def get_or_attr(self, key, default):
        for ctx in reversed(self.stack):
            try:
                return ctx[key]
            except (KeyError, TypeError):
                try:
                    return getattr(ctx, key)
                except AttributeError:
                    pass
        return default

    def __getitem__(self, key):
        return self.get(key)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, tuple(self.stack))

    def __str__(self):
        return str(self.stack)

    def __unicode__(self):
        return unicode(self.stack)

