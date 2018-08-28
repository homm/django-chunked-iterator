#!/usr/bin/env python

import io
from os.path import abspath, dirname, join
from setuptools import setup


here = abspath(dirname(__file__))
try:
    with io.open(join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except IOError:
    long_description = None

setup(
    name='django-chunked-iterator',
    version='0.6.1',
    description='Iterates Django querysets by chunks, saving memory and allows to start faster.',
    author='Alexander Karpinsky',
    author_email='homm86@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/homm/django-chunked-iterator',
    py_modules=['django_chunked_iterator'],
)
