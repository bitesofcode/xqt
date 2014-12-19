import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except IOError:
    README = ''

try:
    REQUIREMENTS = xqt.__depends__
except AttributeError:
    REQUIREMENTS = []

setup(
    name = 'xqt',
    version = '2.0.2',
    author = 'Projex Software',
    author_email = 'team@projexsoftware.com',
    maintainer = 'Projex Software',
    maintainer_email = 'team@projexsoftware.com',
    description = '''''',
    license = 'LGPL',
    keywords = '',
    url = 'http://www.projexsoftware.com',
    include_package_data=True,
    packages = find_packages(),
    install_requires = REQUIREMENTS,
    tests_require = REQUIREMENTS,
    long_description= README,
    classifiers=[],
)