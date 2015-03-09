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
import PySide
import logging
import re
import sys
import xml.parsers.expat

from PySide import QtCore, QtGui, QtUiTools
from xml.etree import ElementTree

from ..lazyload import lazy_import

log = logging.getLogger(__name__)

class XThreadNone(object):
    """
    PySide cannot handle emitting None across threads without crashing.
    This variable can be used in place of None.
    
    :usage      |class A(QtCore.QObject):
                |   valueChanged = QtCore.Signal('QVariant')
                |   def setValue(self, value):
                |       self._value = value
                |       emitter = value if value is not None else QtCore.THREADSAFE_NONE
                |       self.valueChanged.emit(emitter)
                |
                |class B(QtCore.QObject):
                |   def __init__(self, a):
                |       super(B, self).__init__()
                |       a.valueChanged.connect(self.showValue)
                |   def showValue(self, value):
                |       if value == None:
                |           print 'value does equal none'
                |       if value is None:
                |           print 'value unfortunately not IS none'
                |
                |a = A()
                |b = B()
                |t = QtCore.QThread()
                |a.moveToThread(t)
                |t.start()
                |a.setValue(None)   # will crash if not using THREADSAFE_NONE
    """
    def __nonzero__(self):
        return False
    
    def __repr__(self):
        return 'None'
    
    def __str__(self):
        return 'None'
    
    def __eq__(self, other):
        return id(other) == id(self) or other is None

#----------------------------------------------------------------------

SIGNAL_BASE = QtCore.SIGNAL

def SIGNAL(signal):
    match = re.match(r'^(?P<method>\w+)\(?(?P<args>[^\)]*)\)?$', str(signal))
    if not match:
        return SIGNAL_BASE(signal)
    
    method = match.group('method')
    args   = match.group('args')
    args   = re.sub(r'\bPyQt_PyObject\b', 'QVariant', args)
    args   = re.sub(r'\bobject\b', 'QVariant', args)
    
    new_signal = '%s(%s)' % (method, args)
    return SIGNAL_BASE(new_signal)

#----------------------------------------------------------

class UiLoader(QtUiTools.QUiLoader):
    def __init__(self, baseinstance):
        super(UiLoader, self).__init__()
        
        self.dynamicWidgets = {}
        self._baseinstance = baseinstance
    
    def createAction(self, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      parent | <QWidget> || None
                    name   | <str>
        """
        action = super(UiLoader, self).createAction(parent, name)
        if not action.parent():
            action.setParent(self._baseinstance)
        setattr(self._baseinstance, name, action)
        return action
    
    def createActionGroup(self, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      parent | <QWidget> || None
                    name   | <str>
        """
        actionGroup = super(UiLoader, self).createActionGroup(parent, name)
        if not actionGroup.parent():
            actionGroup.setParent(self._baseinstance)
        setattr(self._baseinstance, name, actionGroup)
        return actionGroup
    
    def createLayout(self, className, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      className | <str>
                    parent | <QWidget> || None
                    name   | <str>
        """
        layout = super(UiLoader, self).createLayout(className, parent, name)
        setattr(self._baseinstance, name, layout)
        return layout
    
    def createWidget(self, className, parent=None, name=''):
        """
        Overloads the createWidget method to handle the proper base instance
        information similar to the PyQt4 loading system.
        
        :param      className | <str>
                    parent    | <QWidget> || None
                    name      | <str>
        
        :return     <QWidget>
        """
        className = str(className)
        
        # create a widget off one of our dynamic classes
        if className in self.dynamicWidgets:
            widget = self.dynamicWidgets[className](parent)
            if parent:
                widget.setPalette(parent.palette())
            widget.setObjectName(name)
            
            # hack fix on a QWebView (will crash app otherwise)
            # forces a URL to the QWebView before it finishes
            if className == 'QWebView':
                widget.setUrl(QtCore.QUrl('http://www.google.com'))
        
        # create a widget from the default system
        else:
            widget = super(UiLoader, self).createWidget(className, parent, name)
            if parent:
                widget.setPalette(parent.palette())
        
        if parent is None:
            return self._baseinstance
        else:
            setattr(self._baseinstance, name, widget)
            return widget

#----------------------------------------------------------

class Uic(object):
    def compileUi(self, filename, file):
        import pysideuic
        pysideuic.compileUi(filename, file)
        
    def loadUi(self, filename, baseinstance=None):
        """
        Generate a loader to load the filename.
        
        :param      filename | <str>
                    baseinstance | <QWidget>
        
        :return     <QWidget> || None
        """
        try:
            xui = ElementTree.parse(filename)
        except xml.parsers.expat.ExpatError:
            log.exception('Could not load file: %s' % filename)
            return None
        
        loader = UiLoader(baseinstance)
        
        # pre-load custom widgets
        xcustomwidgets = xui.find('customwidgets')
        if xcustomwidgets is not None:
            for xcustom in xcustomwidgets:
                header = xcustom.find('header').text
                clsname = xcustom.find('class').text
                
                if not header:
                    continue
                
                if clsname in loader.dynamicWidgets:
                    continue
                
                # modify the C++ headers to use the Python wrapping
                if '/' in header:
                    header = 'xqt.' + '.'.join(header.split('/')[:-1])
                
                # try to use the custom widgets
                try:
                    __import__(header)
                    module = sys.modules[header]
                    cls = getattr(module, clsname)
                except (ImportError, KeyError, AttributeError):
                    log.error('Could not load %s.%s' % (header, clsname))
                    continue
                
                loader.dynamicWidgets[clsname] = cls
                loader.registerCustomWidget(cls)
        
        # load the options
        ui = loader.load(filename)
        QtCore.QMetaObject.connectSlotsByName(ui)
        return ui

class QDialog(QtGui.QDialog):
    def __init__(self, *args):
        super(QDialog, self).__init__(*args)

        self._centered = False

    def showEvent(self, event):
        """
        Displays this dialog, centering on its parent.

        :param      event | <QtCore.QShowEvent>
        """
        super(QDialog, self).showEvent(event)

        if not self._centered:
            self._centered = True
            try:
                window = self.parent().window()
                center = window.geometry().center()
            except AttributeError:
                return
            else:
                self.move(center.x() - self.width() / 2, center.y() - self.height() / 2)

#----------------------------------------------------------------------

def init(scope):
    """
    Initialize the xqt system with the PySide wrapper for the Qt system.
    
    :param      scope | <dict>
    """
    # define wrapper compatibility symbols
    QtCore.THREADSAFE_NONE = XThreadNone()
    QtGui.QDialog = QDialog
    
    # define the importable symbols
    scope['QtCore'] = QtCore
    scope['QtGui'] = QtGui
    scope['QtWebKit'] = lazy_import('PySide.QtWebKit')
    scope['QtNetwork'] = lazy_import('PySide.QtNetwork')
    scope['QtXml'] = lazy_import('PySide.QtXml')
    
    scope['uic'] = Uic()
    scope['rcc_exe'] = 'pyside-rcc'
    
    # map overrides
    #QtCore.SIGNAL = SIGNAL
    
    # map shared core properties
    QtCore.QDate.toPyDate = lambda x: x.toPython()
    QtCore.QDateTime.toPyDateTime = lambda x: x.toPython()
    QtCore.QTime.toPyTime = lambda x: x.toPython()
    QtCore.QStringList = list
    QtCore.QString = unicode

