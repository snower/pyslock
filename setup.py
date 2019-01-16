# -*- coding: utf-8 -*-
# 14-8-8
# create by: snower

from setuptools import setup


setup(
    name='pyslock',
    version='0.0.1',
    packages=['pyslock', 'pyslock.protocol', 'pyslock.asyncio'],
    install_requires=[],
    author='snower',
    author_email='sujian199@gmail.com',
    url='https://github.com/snower/pyslock',
    license='MIT',
    keywords=[
        "shared lock", "slock"
    ],
    description='High-performance distributed shared lock service client driver',
    long_description=open("README.rst").read(),
    zip_safe=False,
)
