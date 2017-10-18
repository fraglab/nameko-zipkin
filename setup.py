#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

__version__ = '0.1.2'

setup(
    name='nameko-zipkin',
    version=__version__,
    author='Maxim Kiyan',
    author_email='maxim.k@fraglab.com',
    url='https://github.com/fraglab/nameko-zipkin',
    description='Zipkin tracing for nameko framework',
    packages=['nameko_zipkin'],
    install_requires=[
        'py_zipkin>=0.7.1',
        'nameko>=2.6.0',
    ],
)
