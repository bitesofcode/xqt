""" Defines the hook required for the PyInstaller to use xqt with it. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

__all__ = ['hiddenimports', 'datas', 'excludes']

import os
import projex.pyi

hiddenimports, datas = projex.pyi.collect(os.path.dirname(__file__))
excludes = []

# determine which Qt version to include
wrapper = os.environ.get('XQT_WRAPPER', 'PyQt4')

# include PySide Libraries
if wrapper == 'PySide':
    hiddenimports += ['PySide.QtUiTools', 'PySide.QtXml', 'PySide.QtWebKit']
    excludes.append('PyQt4.*')
    
    try:
        hiddenimports.remove('xqt.pyqt4_wrapper')
    except ValueError:
        pass

# include PyQt4 Libraries
elif wrapper == 'PyQt4':
    hiddenimports += ['PyQt4.QtUiTools', 'PyQt4.QtXml', 'PyQt4.QtWebKit']
    excludes.append('PySide.*')
    
    try:
        hiddenimports.remove('xqt.pyside_wrapper')
    except ValueError:
        pass

# include the binaries
from xqt import QtCore
filepath = os.path.dirname(QtCore.__file__)
pluginpath = os.path.join(filepath, 'plugins', 'imageformats')
datas.append((os.path.join(pluginpath, '*.dll'), 'plugins/imageformats'))

