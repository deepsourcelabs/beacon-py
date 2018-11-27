#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .__version__ import __version__
from .agent import Agent

__agent__ = None

VERSION = __version__


def init(**kwargs):
    global __agent__

    if not __agent__:
        __agent__ = Agent(**kwargs)

    __agent__.start()

    return __agent__
