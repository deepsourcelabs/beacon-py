#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Primary agent which orchestrates everything that Beacon does."""
from __future__ import absolute_import
import atexit
import os
import grpc
import logging
from .__version__ import __version__
from .buffer import Buffer
from .tracer import Tracer
from .utils import Timer, DSN
from . import beacon_pb2_grpc as pb2_grpc
from . import defaults


# setup logging
def _get_logger():
    logger = logging.getLogger('beacon')
    handler = logging.FileHandler('/tmp/beacon.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


beacon_logger = _get_logger()


class Agent(object):
    """
    The Beacon agent.
    """

    VERSION = __version__

    PLATFORM_NAME = 'python'

    FLUSH_INTERVAL = 10

    def __init__(self, dsn=None, **options):

        o = options

        # set the DSN for this agent; this will throw an error if a valid
        # DSN could not be found.
        self._set_dsn(dsn or os.environ.get('BEACON_DSN', None))

        # set project root that would be used by beacon to filter events
        self._set_project_root(o.get('project_root') or
                               os.environ.get('BEACON_PROJECT_ROOT'))

        # set the application's version, which will be used by beacon to
        # correlate events
        self._set_source_version(o.get('source_version') or
                                 os.environ.get('BEACON_SOURCE_VERSION'))

        # set other additional options

        # list of paths that should be excluded from tracking,
        # relative to the project root
        self.exclude_paths = set(o.get('exclude_paths') or [])

        # name of this agent; defaults to the hostname of this machine
        self.name = (o.get('name') or os.environ.get('BEACON_NAME') or
                     defaults.NAME)

        # arbitrary site name to identify this application
        self.site = o.get('site')

        # denote the environment the application is running in
        self.environment = o.get('environment')

        # create buffers to track functions and exceptions
        self.buffers = {
            'function': Buffer(self, 'f'),
            'exception': Buffer(self, 'e')
        }

        # create a container to hold timers
        self.timers = {}

        # create a tracer for this agent
        self.tracer = Tracer(buffer=self.buffers['function'], **options)

        # create a stub for this agent
        channel = grpc.insecure_channel(self.dsn.host)
        self.stub = pb2_grpc.BeaconStub(channel)

        # set the logger
        self.logger = beacon_logger

        # some state maintenance
        self.is_started = False
        self.is_stopped = False

    def start(self):
        """Start this agent."""

        if self.is_started:
            return

        # start the tracer
        self.tracer.start()

        # schedule a flush every 5 seconds
        self.timers['function_flush'] = Timer(self.FLUSH_INTERVAL,
                                              self.buffers['function'].flush)
        self.timers['function_flush'].start()

        # register exit handlers
        atexit.register(self.stop)

        # mark this agent as started
        self.is_started = True

        self.logger.info(
            "Beacon agent started. "
            "DSN: {}, Project Root: {}".format(self.dsn, self.project_root)
        )

    def stop(self):
        """Tear down this agent and cleanup everything."""

        if self.is_stopped:
            return

        # stop the tracer
        self.tracer.stop()

        # clear all timers
        for _, timer in self.timers.items():
            timer.stop()

        # mark this agent as stopped
        self.is_stopped = True

    def _set_dsn(self, dsn):
        dsn = str(dsn).lower()
        self.dsn = DSN(dsn)

    def _set_project_root(self, project_root):
        # TODO: sanitize project root with defaults
        self.project_root = project_root

    def _set_source_version(self, source_version):
        self.source_version = source_version
