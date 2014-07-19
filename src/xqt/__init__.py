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

#----------------------------------------------------------------------

__all__ = [# helpers
           'rcc_exe',
           'uic',
           'wrapVariant',
           'unwrapVariant',
           'PyObject',
           'QT_WRAPPER',
            
           # modules
           'QtCore',
           'QtGui',
           'QtXml',
           'Qsci',
           'QtWebKit',
           'QtDesigner',
           'QtNetwork',
           
           # variables
           'Signal',
           'Slot',
           'Property',
           'QStringList']

import logging
import os
import sys

rcc_exe = None
log = logging.getLogger(__name__)

# define the globals we're going to use
glbls = globals()
for name in __all__:
    glbls[name] = None

QT_WRAPPER = os.environ.get('XQT_WRAPPER', 'PyQt4')

# load the specific wrapper from the environment
package = 'xqt.%s_wrapper' % QT_WRAPPER.lower()
__import__(package)

#----------------------------------------------------------

# define global methods
def wrapVariant(variant):
    if hasattr(QtCore, 'QVariant'):
        return QtCore.QVariant(variant)
    return variant

def unwrapVariant(variant, default=None):
    if type(variant).__name__ == 'QVariant':
        if not variant.isNull():
            return variant.toPyObject()
        return default
    
    if variant is None:
        return default
    return variant

def wrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    return value

def unwrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    return value

# setup the globals that are going to be wrapped
if package:
    sys.modules[package].createMap(globals())
    
    # define the modules for importing
    sys.modules['xqt.QtCore']     = QtCore
    sys.modules['xqt.QtDesigner'] = QtDesigner
    sys.modules['xqt.QtGui']      = QtGui
    sys.modules['xqt.Qsci']       = Qsci
    sys.modules['xqt.QtWebKit']   = QtWebKit
    sys.modules['xqt.QtNetwork']  = QtNetwork
    sys.modules['xqt.QtXml']      = QtXml
    
    # update the base threading class for additional tracking and control
    # options
    class XQThread(QtCore.QThread):
        ThreadCount = 0
        ThreadingEnabled = True
        
        def __init__(self, *args):
            super(XQThread, self).__init__(*args)
            
            XQThread.ThreadCount += 1
        
        def __del__(self):
            XQThread.ThreadCount -= 1

        def start(self):
            if XQThread.ThreadingEnabled:
                super(XQThread, self).start()
            else:
                log.warning('Threading blocked.')

    class ThreadNone(object):
        def __nonzero__(self):
            return False
        
        def __eq__(self, other):
            return id(other) == id(self) or other is None

    QtCore.QThread = XQThread
    QtCore.THREADSAFE_NONE = ThreadNone()

