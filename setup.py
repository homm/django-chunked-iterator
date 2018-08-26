#!/usr/bin/env python

from setuptools import setup


setup(
    name='django-chunked-iterator',
    version='0.5',
    description='Iterates Django querysets by chunks, saving memory and allows to start faster.',
    author='Alexander Karpinsky',
    author_email='homm86@gmail.com',
    url='https://github.com/homm/django-chunked-iterator',
    py_modules=['django_chunked_iterator'],
)
