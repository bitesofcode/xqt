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

#------------------------------------------------------------------------------

# define version information (major,minor,maintanence)
__major__   = 2
__minor__   = 0
__revision__ = 0

__version_info__   = (__major__, __minor__, __revision__)
__version__        = '%s.%s' % (__major__, __minor__)

import os
import sys

from . import errors
from .lazyload import lazy_import

QT_WRAPPER = os.environ.get('XQT_WRAPPER', 'PyQt4')

#----------------------------------------------------------------------

from .common import *

#----------------------------------------------------------------------

# ensure the Qt system can be loaded properly
__wrapper__ = 'xqt.wrappers.{0}'.format(QT_WRAPPER.lower())
__import__(__wrapper__)

scope = globals()
sys.modules[__wrapper__].init(scope)

# backwards compatibility
wrapVariant = scope['py2q']
unwrapVariant = scope['q2py']

QtCore = scope['QtCore']

SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT
Signal = QtCore.Signal
Slot = QtCore.Slot
Property = QtCore.Property

# update the modules with the global wrappers
sys.modules['xqt.QtCore'] = scope['QtCore']
sys.modules['xqt.QtGui'] = scope['QtGui']
sys.modules['xqt.QtXml'] = scope['QtXml']
sys.modules['xqt.QtNetwork'] = scope['QtNetwork']
sys.modules['xqt.QtDesigner'] = scope['QtDesigner']
sys.modules['xqt.Qsci'] = scope['Qsci']
sys.modules['xqt.QtWebKit'] = scope['QtWebKit']
