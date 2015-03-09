from setuptools import setup, find_packages

setup(
    name = 'xqt',
    version = '2.0.2',
    author = 'Eric Hulser',
    author_email = 'eric.hulser@gmail.com',
    maintainer = 'Eric Hulser',
    maintainer_email = 'eric.hulser@gmail.com',
    description = 'Wrapper system to handle differences between Python Qt ports.',
    license = 'LGPL',
    keywords = '',
    url = 'https://www.github.com/ProjexSoftware/xqt',
    include_package_data=True,
    packages = find_packages(),
    long_description= 'Wrapper system to handle differences between Python Qt ports.',
    classifiers=[],
)