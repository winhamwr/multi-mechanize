#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs

if sys.version_info < (2, 6):
    raise Exception("Multi-mechanize requires Python 2.6 or higher.")

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import multi_mechanize as distmeta
sys.modules.pop("multi_mechanize", None)

install_requires = [
    "multiprocessing",
    "mechanize==0.2.5",
    "numpy==1.5.1",
    "jinja2",
    "matplotlib",
]
tests_require = []

long_description = codecs.open("README.rst", "r", "utf-8").read()

console_scripts = [
        'multi_mechanize/bin/multi-mechanize.py',
        'contrib/mm-csv-to-jmeter.py',
]

setup(
    name="multi_mechanize",
    version=distmeta.__version__,
    description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    platforms=["any"],
    license="LGPLv3",
    packages=find_packages(exclude=[]),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Topic :: System :: Benchmark",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    scripts=console_scripts,
    long_description=long_description,
)