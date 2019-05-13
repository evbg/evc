#!/usr/bin/python

import os
from setuptools import setup

DESCRIPTION = "Simple client for the EVE Python REST API Framework"

README = os.path.join(os.path.dirname(__file__), 'README.rst')

try:
    with open(README) as README_file:
        long_description = README_file.read()
except EnvironmentError:
    long_description = ''

setup(
    name="evc",
    version="0.4.1",
    description=DESCRIPTION,
    long_description=long_description,
    license="MIT License",
    author="Evgeny V. Bogodukhov",
    author_email="b@evbg.ru",
    url="https://github.com/evbg/evc",
    platforms=["any"],
    packages=[
        "evc",
    ],
    data_files=[
        ('', ['README.rst', 'LICENSE']),
    ],
    include_package_data=True,
    provides=["evc"],
    install_requires=["requests", "simplejson"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
