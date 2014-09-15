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