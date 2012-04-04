"""
WhooshAlchemy
-------------

Whoosh extension to SQLAlchemy.
"""

from setuptools import setup

long_description = open('README.rst').read()

setup(
    name='WhooshAlchemy',
    version='0.1.3',
    url='https://github.com/sfermigier/WhooshAlchemy',
    license='BSD',
    author='Stefane Fermigier',
    author_email='sf@fermigier.com',
    description='Whoosh extension to SQLAlchemy',
    long_description=long_description,
    py_modules=['whooshalchemy'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'whoosh', 'sqlalchemy'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite = 'test',
)
