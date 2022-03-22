#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 09:53:56 2017

@author: musset
"""

from setuptools import find_packages, setup

setup(name="solar",
      version="0.0.2",
      description="Solar Zooniverse Processor for the jet zooniverse project. This will request and create data to populate the zooniverse project, and aggregate the results.",
      author="Charlie Kapsiak, Sophie Musset ",
      author_email='musset.sophie@gmail.com',
      platforms=["any"],  # or more specific, e.g. "win32", "cygwin", "osx"
      url="https://github.com/CharKap/Solar_Zooniverse_Processor",
      packages=find_packages(),
      install_requires=["numpy>=1.11.0", "matplotlib>=1.5.3"]
      )
