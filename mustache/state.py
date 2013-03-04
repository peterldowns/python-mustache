# coding: utf-8
import re
from os.path import (join, abspath)

from copy import (copy)
from stack import (Stack)
from context import (Context)

class State(object):
    """ An object to keep track of the parser's state as it works its way 
    through a string to be parsed. Uses sane defaults (that comply with the
    mustache spec), but allows for customization.  """

    def __init__(self, partials_dir='.', extension='mustache', encoding='utf-8',
                 encoding_error='xmlcharrefreplace'):
        # Partials
        self.partials_dir = Stack(partials_dir)
        self.extension = extension
        
        # Encoding
        self.encoding = encoding
        self.encoding_error = encoding_error
        
        # State
        self.partials = Stack({})
        self.section = Stack()
        self.escape = Stack(True)
        self.context = Context()

        # Parsing
        self.tags = Stack({
            'otag' : re.escape('{{'),    # tag opening
            'ctag' : re.escape('}}'),    # tag closing
            'types' : '|'.join(('#', '/', '^', '&', '!', '>')) # tag modifiers
        })
        self.default_tags = copy(self.tags())
        self.eol_chars = ('\r', '\n')
        self.raw_tag_re = r"""
            (?P<lead_wsp>[\ \t]*) # leading whitespace
            %(otag)s \s*
            (?:
                (?P<change>=) \s* (?P<delims>.+?)   \s* = |             # change delimiters OR 
                (?P<raw>{)    \s* (?P<raw_key>.+?) \s* } |                # raw format (no escaping) OR
                (?P<tag_type>[%(types)s]?)  \s* (?P<tag_key>[\s\S]+?)    # other tag types
            )
            \s* %(ctag)s (?P<end_wsp>[\ \t]*)"""
        self.re_flags = re.MULTILINE|re.VERBOSE|re.DOTALL|re.UNICODE
        self.tag_re = None # replaced by update_tag_re
        self.update_tag_re()

    
    def compile_tag_re(self, tags):
        """
        Return the regex used to look for Mustache tags compiled
        to work with specific opening tags, close tags, and tag
        types.
        """
        return re.compile(self.raw_tag_re % tags, self.re_flags)

    def update_tag_re(self):
        """
        Update the compiled tag regex to use the tags on the top
        of the tag stack. This should be called any time the tag
        stack is changed.
        """
        self.tag_re = self.compile_tag_re(self.tags())

    def push_tags(self, tags):
        """
        Pushes the new tags to the top of the tag state and updates
        the compiled tag regex.
        """
        self.tags.push(tags)
        self.update_tag_re()

    def pop_tags(self):
        """
        Pops the current tags from the top of the tag state and
        updates the compiled tag regex.
        """
        self.tags.pop()
        self.update_tag_re()
    
    @property
    def abs_partials_dir(self):
        """
        Returns the absolute path to the current partials directory
        based on the current stack of relative partial directories.
        """
        return abspath(join(*self.partials_dir))
