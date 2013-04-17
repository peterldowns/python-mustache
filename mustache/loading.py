# coding: utf-8
from os.path import split, splitext, extsep, join, abspath, exists
from utils import make_unicode

DEFAULT_EXTENSION = 'html'
DEFAULT_DIRECTORY = 'static/templates'
DEFAULT_ENCODING = 'utf-8'
DEFAULT_ERRORS = 'xmlcharrefreplace'

def read(path):
    """ Return the contents of a file as a byte string. """
    with open(path, 'rb') as f:
        return f.read()

def read_unicode(path, encoding, encoding_errors):
    """ Return the contents of a file as a unicode string. """
    with open(path, 'rb') as f:
        return make_unicode(f.read(), encoding, encoding_errors)

def get_abs_template_path(template_name, directory, extension):
    """ Given a template name, a directory, and an extension, return the
    absolute path to the template. """
    # Get the relative path
    relative_path = join(directory, template_name)
    file_with_ext = template_name

    if extension:
        # If there is a default extension, but no file extension, then add it
        file_name, file_ext = splitext(file_with_ext)
        if not file_ext:
            file_with_ext = extsep.join(
                (file_name, extension.replace(extsep, '')))
            # Rebuild the relative path
            relative_path = join(directory, file_with_ext)

    return abspath(relative_path)

def load_file(path, encoding, encoding_errors):
    """ Given an existing path, attempt to load it as a unicode string. """
    abs_path = abspath(path)
    if exists(abs_path):
        return read_unicode(abs_path, encoding, encoding_errors)
    raise IOError("File {0} does not exist".format(abs_path))

def load_template(name, directory, extension, encoding, encoding_errors):
    """ Load a template and return its contents as a unicode string. """
    abs_path = get_abs_template_path(name, directory, extension)
    return load_file(abs_path, encoding, encoding_errors)

