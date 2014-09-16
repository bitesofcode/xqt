"""
Sets up the import requirements for the Pyinstaller module.
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

import os
import projex.pyi

basepath = os.path.dirname(__file__)
hiddenimports, datas = projex.pyi.collect(basepath)
excludes = []

# include specific modules
available_wrappers = ['PyQt4', 'PySide']
available_modules = ['QtCore', 'QtGui', 'QtNetwork', 'QtWebKit', 'QtXml', 'QtDesigner', 'Qsci']
chosen_wrapper = os.environ.get('XQT_WRAPPER', 'PyQt4')

for wrapper in available_wrappers:
    for module in available_modules:
        modname = '{0}.{1}'.format(wrapper, module)
        add_to = hiddenimports if wrapper == chosen_wrapper else excludes
        if not modname in add_to:
            add_to.append(modname)

