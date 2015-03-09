"""
The xqt library is a simple wrapper system on top of the various bindings
that Qt has for Python.  This provides a way to consolidate the differences
between things like PyQt4, PyQt5, and PySide in a way that will allow Python
developers to build tools and libraries that are able to work with any of the
wrapper systems.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

class XQtError(StandardError):
    """ Base class for all XQt based errors """
    pass

# W
#----------------------------------------------------------------------

class WrapperNotFound(XQtError):
    """ Raised when the wrapper system is unable to load the wrapper object """
    def __init__(self, wrapper):
        msg = 'Wrapper not found: {0}'.format(wrapper)
        super(WrapperNotFound, self).__init__(msg)


