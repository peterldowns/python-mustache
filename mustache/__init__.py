# coding: utf-8
"""
TODO: add a docstring.
"""

import os.path
from copy import (copy)

from state import (State)
from context import (Context)
from rendering import (render)
from loading import (load_file, load_template)
from utils import (make_unicode, html_escape)

__version__ = '0.1.1'
__all__ = ['render', 'State', 'Context',
           'load_file', 'load_template',
           'make_unicode', 'html_escape',
           'template', ]

template_globals = {}

def template(relative_path, *args, **kwargs):
    """ A decorator for easily rendering templates.
    Use as follows:

    main.py: 
        from mustache import (template)

        @template('../tests/static/say_hello.html')
        def index():
            context = {'name' : 'world'}
            partials = {}
            return context, partials

        if __name__=="__main__":
            print index()
    
    static/say_hello.html:

        <h1> Hello, {{name}}! </h1>

    from the command line:
        
        > python main.py
        <h1> Hello, world! </h1>
    """
    directory, filename = os.path.split(relative_path)
    
    partials_dir = os.path.abspath(directory)
    name, ext = os.path.splitext(filename)

    state = State(partials_dir=directory, extension=ext, *args, **kwargs)
    template = load_template(name, directory, ext, state.encoding, state.encoding_error)

    def wrapper(fn):
        def render_template(*args, **kwargs):
            res = fn(*args, **kwargs)
            if isinstance(res, tuple):
                if len(res) == 2:
                    (new_context, partials) = res
                elif len(res) == 1:
                    (new_context, partials) = (res[0], {})
            elif isinstance(res, dict):
                (new_context, partials) = (res, {})
            else:
                (new_context, partials) = ({}, {})
            context = copy(template_globals)
            context.update(new_context)
            return render(template, context, partials, state)
        return render_template
    return wrapper

