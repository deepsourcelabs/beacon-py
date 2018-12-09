#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for Beacon."""
import re
import threading
import time

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse, urlencode


class Timer(object):
    def __init__(self, interval, func, *args, **kwargs):
        self.timer = None
        self.mutex = threading.Lock()
        self.is_started = False
        self.is_stopped = False
        self.interval = interval

        def wrapped():
            start = time.time()
            func(*args, **kwargs)
            with self.mutex:
                if not self.is_stopped:
                    _interval = abs(self.interval - (time.time() - start))
                    self.timer = threading.Timer(_interval, wrapped, ())
                    self.timer.start()
        self.wrapped = wrapped

    def start(self):
        if self.is_started:
            raise Exception("This timer is already running.")

        with self.mutex:
            self.is_started = True
            self.timer = threading.Timer(self.interval, self.wrapped, ())
            self.timer.start()

    def stop(self):
        if self.is_stopped:
            raise Exception("This timer has already been stopped.")

        with self.mutex:
            self.is_stopped = True
            self.timer.cancel()


class DSN(object):
    """
    Validates the DSN string for the following format -
    <scheme>://<api-key>@<beacon-server-hostname>/<repository-id>
    """
    ALLOWED_SCHEMES = ('http', 'https')

    API_KEY_REGEX = re.compile(r'^[a-fA-F0-9]{32}$')
    HOSTNAME_REGEX = re.compile(r'^[a-z0-9]+([-.][a-z0-9]+)*\.[a-z]{2,}(:\d+)?$')
    REPOSITORY_REGEX = re.compile(r'^\/?(\d+)\/?$')

    def __init__(self, dsn):

        self.input_dsn_string = str(dsn)

        if not dsn:
            raise ValueError(self.ERROR_MESSAGE)

        try:
            # Parse the dsn as a url to form
            # scheme:   http/https
            # netloc:   (api-key)@(hostname)
            # path:     /(repository_id)
            self.parsed_dsn = urlparse(self.input_dsn_string)
        except Exception:
            raise ValueError(self.ERROR_MESSAGE)

        self._set_scheme()
        self._set_api_key()
        self._set_host()
        self._set_repository_id()

    def _set_scheme(self):
        """
        Validates the scheme in the DSN string and sets it in `scheme`
        attribute.
        """
        scheme = self.parsed_dsn.scheme
        if self.parsed_dsn.scheme not in self.ALLOWED_SCHEMES:
            raise ValueError(self.ERROR_MESSAGE)

        self.scheme = scheme

    def _set_api_key(self):
        """
        Validates the API key in the DSN string and sets it in `api_key`
        attribute.
        """
        api_key = self.parsed_dsn.netloc.split('@', 1)[0]
        if not api_key or not self.API_KEY_REGEX.match(api_key):
            raise ValueError(self.ERROR_MESSAGE)

        self.api_key = api_key

    def _set_host(self):
        """
        Validates the host in the DSN string and sets it in `host`
        attribute.
        """
        try:
            host = self.parsed_dsn.netloc.split('@', 1)[1]
        except IndexError:
            raise ValueError(self.ERROR_MESSAGE)

        if not host or not self.HOSTNAME_REGEX.match(host):
            raise ValueError(self.ERROR_MESSAGE) 

        self.host = host

    def _set_repository_id(self):
        """
        Validates the Repository ID in the DSN string and sets it in
        `repository_id` attribute.
        """
        path = self.REPOSITORY_REGEX.match(self.parsed_dsn.path)
        if not path:
            raise ValueError(self.ERROR_MESSAGE)

        try:
            repository_id = path.group(1)
        except IndexError:
            raise ValueError(self.ERROR_MESSAGE)

        if not repository_id.isdigit():
            raise ValueError(self.ERROR_MESSAGE)

        self.repository_id = repository_id

    def __str__(self):
        return "{scheme}://{api_key}@{host}/{repository_id}".format(
            scheme=self.scheme,
            api_key=self.api_key,
            host=self.host,
            repository_id=self.repository_id
        )

    @property
    def ERROR_MESSAGE(self):
        return (
            "Invalid DSN string - {}. The required format is "
            "<scheme>://<api-key>@<beacon-server-hostname>/<repository-id>"
            .format(self.input_dsn_string)
        )
