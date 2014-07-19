orb
======================

The xqt library is a wrapper system on top of the various Python Qt frameworks.
This project will try to bridge the gap between some of the differences between
the frameworks so that developers can easily write code that will work for
any Qt implementation.

Right now, the supported wrappers are:

* PyQt4
* PySide

_Note, while this project is licensed under LGPL, you will be subject to the
license agreement of your underlying Qt framework.  PySide is LGPL.  PyQt4
however is GPL unless purchased, thus rendering this project GPL if used with PyQt4._

Installation
-----------------------

If you would like to use the latest build that has been tested and published,
you can use the Python `setuptools` to install it to your computer or virtual
environment:

    $ easy_install projex_xqt

If you would like to use the latest code base, you can clone the repository
and reference your `PYTHONPATH` to the checkout location, or make a build
of the code by using the `projex.xbuild` system:

    $ cd /path/to/git/xqt
    $ python /path/to/projex/scripts/xbuild.py ./xqt.xbuild

Documentation
-----------------------

Usage is very simple, all you have to do is specify your Qt wrapper
as an environment variable before importing the xqt library.

This will handle mapping differences in naming conventions, variable handlers,
etc.

_Use with PyQt4_

```python
>>> import os
>>> os.environ['XQT_WRAPPER'] = 'PyQt4'

>>> from xqt import QtCore, QtGui
>>> print QtCore
<module 'PyQt4.QtCore' from 'PyQt4.QtCore.pyd'>
>>> print QtCore.Signal
<type 'PyQt4.QtCore.pyqtSignal'>
```

_Use with PySide_

```python
>>> import os
>>> os.environ['XQT_WRAPPER'] = 'PySide'

>>> from xqt import QtCore, QtGui
>>> print QtCore
<module 'PySide.QtCore' from 'PySide\QtCore.pyd'>
>>> print QtCore.Signal
<type 'PySide.QtCore.Signal'>
```

The `projexui` library is written on top of this architecture, so it can
be used with either PyQt4, or PySide.  For more examples on usage, you can
refer to the widgets and plugins defined there.

