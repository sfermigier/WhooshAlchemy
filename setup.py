"""
WhooshAlchemy
-------------

Whoosh extension to SQLAlchemy.
"""

from __future__ import absolute_import, print_function, unicode_literals

from setuptools import setup

VERSION = '0.3.1'
DEPS = [
    'whoosh',
    'sqlalchemy',
    'six',
]
DESCRIPTION = "Whoosh extension to SQLAlchemy"

long_description = open('README.rst').read()

setup(
    name='WhooshAlchemy',
    version=VERSION,
    url='https://github.com/sfermigier/WhooshAlchemy',
    license='BSD',
    author='Stefane Fermigier',
    author_email='sf@fermigier.com',
    description=DESCRIPTION,
    long_description=long_description,
    py_modules=['whooshalchemy'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=DEPS,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],)
