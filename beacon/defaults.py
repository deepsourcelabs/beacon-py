#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Default configuration settings for the Beacon agent."""
import socket

NAME = socket.gethostname() if hasattr(socket, 'gethostname') else None
