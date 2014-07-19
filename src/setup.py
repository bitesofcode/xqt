import os
try:
    from setuptools import setup
except ImportError:
    try:
        from distutils.core import setup
    except ImportError:
        raise ImportError('Could not find setuptools.')

setup(
    name = 'projex_xqt',
    version = '1.1',
    author = 'Projex Software',
    author_email = 'team@projexsoftware.com',
    maintainer = 'Projex Software',
    maintainer_email = 'team@projexsoftware.com',
    description = '''''',
    license = 'LGPL',
    keywords = '',
    url = '',
    include_package_data=True,
    long_description='''
The xqt library is a simple wrapper system on top of the various bindings
that Qt has for Python.  This provides a way to consolidate the differences
between things like PyQt4, PyQt5, and PySide in a way that will allow Python
developers to build tools and libraries that are able to work with any of the
wrapper systems.
''',
    classifiers=[],
    packages = [r'xqt'],
    package_data = {}
)