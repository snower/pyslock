# -*- coding: utf-8 -*-
# 14-8-8
# create by: snower

import os
from setuptools import find_packages, setup

if os.path.exists("README.md"):
    with open("README.md") as fp:
        long_description = fp.read()
else:
    long_description = 'https://github.com/snower/syncany'

setup(
    name='pyslock',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[],
    author='snower',
    author_email='sujian199@gmail.com',
    url='https://github.com/snower/pyslock',
    license='MIT',
    keywords=[
        "shared lock", "slock"
    ],
    package_data={
        '': ['README.md'],
    },
    description='High-performance distributed shared lock service client driver',
    long_description=long_description,
    long_description_content_type='text/markdown',
    zip_safe=False,
)
