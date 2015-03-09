""" Sets up the Qt environment to work with various Python Qt wrappers """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

# requires at least the QtCore module
import os
import re
import sip

SIP_VERSION = os.environ.get('XQT_SIP_VERSION', '2')

# use strings as Python variables vs. QString
if SIP_VERSION == '2':
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QUrl', 2)

from PyQt4 import QtCore
from ..lazyload import lazy_import

# define wrappers
def py2q(py_object):
    if SIP_VERSION != '2' and QtCore.QT_VERSION < 264198:
        return QtCore.QVariant(py_object)
    else:
        return py_object

def q2py(q_variant, default=None):
    if SIP_VERSION == '2' or not isinstance(q_variant, QtCore.QVariant):
        return q_variant
    elif QtCore.QT_VERSION < 264198:
        return q_variant.toPyObject() if not q_variant.isNull() else default
    else:
        return q_variant.toPyObject()

SIGNAL_BASE = QtCore.SIGNAL

def SIGNAL(signal):
    match = re.match(r'^(?P<method>\w+)\(?(?P<args>[^\)]*)\)?$', str(signal))
    if not match:
        return SIGNAL_BASE(signal)
    
    method = match.group('method')
    args   = match.group('args')
    args   = re.sub(r'\bobject\b', 'PyQt_PyObject', args)
    
    new_signal = '%s(%s)' % (method, args)
    return SIGNAL_BASE(new_signal)

#----------------------------------------------------------------------

class Signal(type):
    ARGCACHE = {}
    
    def __new__(cls, *args):
        sig = QtCore.pyqtSignal(*args)
        
        arg_info = []
        for arg in args:
            try:
                arg_info.append(arg.__name__)
            except:
                arg_info.append(str(arg))
        Signal.ARGCACHE[sig] = '({0})'.format(', '.join(arg_info))
        return sig
    
    @staticmethod
    def docs(sig):
        return str(sig).split(' ')[2].strip('>') + Signal.ARGCACHE.get(sig, '(...)')

#----------------------------------------------------------------------

class Slot(type):
    ARGCACHE = {}
    
    def __new__(cls, *args):
        slot = QtCore.pyqtSlot(*args)
        
        arg_info = []
        for arg in args:
            try:
                arg_info.append(arg.__name__)
            except:
                arg_info.append(str(arg))
        Slot.ARGCACHE[slot] = '({0})'.format(', '.join(arg_info))
        return slot
    
    @staticmethod
    def docs(slot):
        return str(slot).split(' ')[2].strip('>') + Slot.ARGCACHE.get(slot, '(...)')

#----------------------------------------------------------------------

def init(scope):
    """
    Initialize the xqt system with the PyQt4 wrapper for the Qt system.
    
    :param      scope | <dict>
    """
    # update globals
    scope['py2q'] = py2q
    scope['q2py'] = q2py
    
    # define wrapper compatibility symbols
    QtCore.THREADSAFE_NONE = None
    
    # define the importable symbols
    scope['QtCore'] = QtCore
    scope['QtGui'] = lazy_import('PyQt4.QtGui')
    scope['QtWebKit'] = lazy_import('PyQt4.QtWebKit')
    scope['QtNetwork'] = lazy_import('PyQt4.QtNetwork')
    scope['QtXml'] = lazy_import('PyQt4.QtXml')
    
    # PyQt4 specific modules
    scope['QtDesigner'] = lazy_import('PyQt4.QtDesigner')
    scope['Qsci'] = lazy_import('PyQt4.Qsci')
    
    scope['uic'] = lazy_import('PyQt4.uic')
    scope['rcc_exe'] = 'pyrcc4'
    
    # map shared core properties
    QtCore.QDate.toPython = lambda x: x.toPyDate()
    QtCore.QDateTime.toPython = lambda x: x.toPyDateTime()
    QtCore.QTime.toPython = lambda x: x.toPyTime()
    
    QtCore.Signal = Signal
    QtCore.Slot = Slot
    QtCore.Property = QtCore.pyqtProperty
    QtCore.SIGNAL = SIGNAL
    QtCore.__version__ = QtCore.QT_VERSION_STR

    if SIP_VERSION == '2':
        QtCore.QStringList = list
        QtCore.QString = unicode

