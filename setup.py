"""
WhooshAlchemy
-------------

Whoosh extension to SQLAlchemy.
"""

from setuptools import setup
import os

os.rename("README.rst", "README.txt")

setup(
    name='WhooshAlchemy',
    version='0.1.2',
    url='https://github.com/sfermigier/WhooshAlchemy',
    license='BSD',
    author='Stefane Fermigier',
    author_email='sf@fermigier.com',
    description='Whoosh extension to SQLAlchemy',
    long_description=__doc__,
    py_modules=['whooshalchemy'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'whoosh', 'sqlalchemy'
    ],
    classifiers=[
        #'Environment :: Web Environment',
        #'Intended Audience :: Developers',
        #'License :: OSI Approved :: BSD License',
        #'Operating System :: OS Independent',
        #'Programming Language :: Python',
        #'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        #'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite = 'test',
)

os.rename("README.txt", "README.rst")
