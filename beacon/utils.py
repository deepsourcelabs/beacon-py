#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for Beacon."""
import threading
import time


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
