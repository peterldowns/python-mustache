# coding: utf-8
import re
from os.path import split

from context import Context
from loading import load_template
from state import State
from utils import make_unicode, html_escape

def get_match_info(template, match, state):
    """
    Given a template and a regex match within said template, return a
    dictionary of information about the match to be used to help parse the
    template.
    """
    info = match.groupdict()

    # Put special delimiter cases in terms of normal ones
    if info['change']:
        info.update({
            'tag_type' : '=',
            'tag_key' : info['delims'],
        })
    elif info['raw']:
        info.update({
            'tag_type' : '&',
            'tag_key' : info['raw_key'],
        })

    # Rename the important match variables for convenience
    tag_start = match.start()
    tag_end = match.end()
    tag_type = info['tag_type']
    tag_key = info['tag_key']
    lead_wsp = info['lead_wsp']
    end_wsp = info['end_wsp']

    begins_line = (tag_start == 0) or (template[tag_start-1] in state.eol_chars)
    ends_line = (tag_end == len(template) or
                 template[tag_end] in state.eol_chars)
    interpolating = (tag_type in ('', '&'))
    standalone = (not interpolating) and begins_line and ends_line

    if end_wsp:
        tag_end -= len(end_wsp)
    if standalone:
        template_length = len(template)
        # Standalone tags strip exactly one occurence of '\r', '\n', or '\r\n'
        # from the end of the line.
        if tag_end < len(template) and template[tag_end] == '\r':
            tag_end += 1
        if tag_end < len(template) and template[tag_end] == '\n':
            tag_end += 1
    elif lead_wsp:
        tag_start += len(lead_wsp)
        lead_wsp = ''

    info.update({
        'tag_start' : tag_start,
        'tag_end' : tag_end,
        'tag_type' : tag_type,
        'tag_key' : tag_key,
        'lead_wsp' : lead_wsp,
        'end_wsp' : end_wsp,
        'begins_line' : begins_line,
        'ends_line' : ends_line,
        'interpolating' : interpolating,
        'standalone' : standalone,
    })
    return info

def get_tag_context(name, state):
    """
    Given a tag name, return its associated value as defined in the current
    context stack.
    """
    new_contexts = 0
    ctm = None
    while True:
        try:
            ctx_key, name = name.split('.', 1)
            ctm = state.context.get(ctx_key)
        except ValueError:
            break
        if not ctm:
            break
        else:
            state.context.push(ctm)
            new_contexts += 1

    ctm = state.context.get(name)

    return new_contexts, ctm

def section_end_info(template, tag_key, state, index):
    """
    Given the tag key of an opening section tag, find the corresponding closing
    tag (if it exists) and return information about that match.
    """

    state.section.push(tag_key)
    match = None
    matchinfo = None
    search_index = index

    while state.section:
        match = state.tag_re.search(template, search_index)
        if not match:
            raise Exception("Open section %s never closed" % tag_key)

        matchinfo = get_match_info(template, match, state)

        # If we find a new section tag, add it to the stack and keep going
        if matchinfo['tag_type'] in ('#', '^'):
            state.section.push(matchinfo['tag_key'])
        # If we find a closing tag for the current section, 'close' it by
        # popping the stack
        elif matchinfo['tag_type'] == '/':
            if matchinfo['tag_key'] == state.section():
                state.section.pop()
            else:
                raise Exception(
                    'Unexpected section end: received %s, expected {{/%s}}' % (
                        repr(match.group(0)), tag_key))
        search_index = matchinfo['tag_end']

    return matchinfo


def render(template, context, partials={}, state=None):
    """ Renders a given mustache template, with sane defaults. """
    # Create a new state by default
    state = state or State()

    # Add context to the state dict
    if isinstance(context, Context):
        state.context = context
    else:
        state.context = Context(context)

    # Add any partials to the state dict
    if partials:
        state.partials.push(partials)

    # Render the rendered template
    return __render(make_unicode(template), state)

def __render(template, state, index=0):
    """
    Given a /template/ string, a parser /state/, and a starting
    offset (/index/), return the rendered version of the template.
    """
    # Find a Match
    match = state.tag_re.search(template, index)
    if not match:
        return template[index:]

    info = get_match_info(template, match, state)
    _pre = template[index : info['tag_start']] # template before the tag
    _tag = template[info['tag_start'] : info['tag_end']] # tag
    _continue = info['tag_end'] # the index at which to continue

    # Comment
    if info['tag_type'] == '!':
        # Comments are removed from output
        repl = ""

    # Delimiter change
    elif info['tag_type'] == '=':
        # Delimiters are changed; the tag is rendered as ""
        delimiters = re.split(r'\s*', info['tag_key'])
        new_tags = state.tags(_copy=True)
        new_tags['otag'], new_tags['ctag'] = map(re.escape, delimiters)
        state.push_tags(new_tags)
        repl = ""

    # Plain tag
    elif info['tag_type'] == '':
        repl = __render_tag(info, state)

    # Raw tag (should not be escaped)
    elif info['tag_type'] == '&':
        state.escape.push(False)
        repl = __render_tag(info, state)
        state.escape.pop()

    # Partial
    elif info['tag_type'] == '>':
        partial_name = info['tag_key']
        partial_template = None
        new_dir = None
        lead_wsp = re.compile(r'^(.)', re.M)
        repl = ''
        try:
            # Cached
            partial_template = state.partials()[partial_name]
        except (KeyError, IndexError):
            try:
                # Load the partial template from a file (if it exists)
                new_dir, filename = split(partial_name)
                if new_dir:
                    state.partials_dir.push(new_dir)

                partial_template = load_template(filename, state.abs_partials_dir, state.extension,
                                                 state.encoding, state.encoding_error)
            except (IOError):
                pass

        if partial_template:
            # Preserve indentation
            if info['standalone']:
                partial_template = lead_wsp.sub(info['lead_wsp']+r'\1', partial_template)

            # Update state
            state.partials.push(state.partials()) # XXX wtf is this shit?
            state.push_tags(state.default_tags)

            # Render the partial
            repl = __render(partial_template, state)

            # Restore state
            state.partials.pop()
            state.pop_tags()
            if new_dir:
                state.partials_dir.pop()

    # Section

    # TODO(peter): add a stop= index to __render so that template_to_inner does
    # not need to be constructed with [:] indexing, which is extremely
    # expensive.
    elif info['tag_type'] in ('#', '^'):
        otag_info = info
        ctag_info = section_end_info(template, info['tag_key'], state, _continue)

        # Don't want to parse beyond the end of the inner section, but
        # must include information on prior contents so that whitespace
        # is preserved correctly and inner tags are not marked as standalone.
        inner_start = otag_info['tag_end']
        inner_end = ctag_info['tag_start']
        _continue = ctag_info['tag_end']

        template_with_inner = template[:inner_end]

        new_contexts, ctm = get_tag_context(otag_info['tag_key'], state)
        truthy = otag_info['tag_type'] == '#'

        #if ctm is not None:
        if ctm:
            # If there's a match and it's callable, feed it the inner template
            if callable(ctm):
                template_to_inner = template[:inner_start]
                inner = template[inner_start:inner_end]
                template_with_inner = template_to_inner + make_unicode(ctm(inner))

            # Make the context list an iterable from the ctm
            if not hasattr(ctm, '__iter__') or isinstance(ctm, dict):
                ctx_list = [ctm]
            else:
                ctx_list = ctm
        # If there's no match, there are no new contexts
        else:
            ctx_list = [False]

        # If there are new contexts and the section is truthy, or if
        # there are no new contexts and the section is falsy, render
        # the contents
        repl_stack = []
        for ctx in ctx_list:
            if (truthy and ctx) or (not truthy and not ctx):
                state.context.push(ctx)
                repl_stack.append(
                    __render(template_with_inner, state, inner_start))

            else:
                break

        repl = ''.join(repl_stack)
        for i in xrange(new_contexts): state.context.pop()
    else:
        raise Exception("found unpaired end of section tag!")

    return u''.join((
        _pre, make_unicode(repl), __render(template, state, _continue)))

def __render_tag(info, state):
    """ Render an individual tag by making the appropriate replacement within
    the current context (if any). """
    new_contexts, context_match = get_tag_context(info['tag_key'], state)
    replacement = ''

    if context_match or context_match == 0:
        replacement = context_match
    elif info['tag_key'] == '.':
        replacement = state.context()
    else:
        replacement = ''

    # Call all callables / methods / lambdas / functions
    if replacement and callable(replacement):
        replacement = make_unicode(replacement())

        state.push_tags(state.default_tags)
        replacement = __render(template=replacement, state=state)
        state.pop_tags()

    for i in xrange(new_contexts): state.context.pop()

    if state.escape():
        return html_escape(replacement)
    return replacement

