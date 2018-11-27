#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom exception used by Beacon."""

from __future__ import absolute_import


class ConfigurationError(ValueError):
    pass


class InvalidDSN(ConfigurationError):
    pass
