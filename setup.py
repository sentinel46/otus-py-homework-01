#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import io
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="log_analyzer",
    version="0.1.0",
    license="GPL3",
    description="OTUS-PY Homework 01",
    # long_description="",
    author="Aleksei Dovgal",
    author_email="altdaedroth@gmail.com",
    # url="",
    packages=find_packages("log_analyzer"),
    package_dir={"": "log_analyzer"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    # classifiers=[
    #
    # ],
    # keywords=[],
    # install_requires=[],
    entry_points={
        "console_scripts": [
            "log_analyzer = log_analyzer.cli:main",
        ]
    },
)
