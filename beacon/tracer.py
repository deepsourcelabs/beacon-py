#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python tracer for raw data collection."""

import re
import sys


class Tracer(object):
    """Python tracer for Beacon.

    The tracer provides a function that can be passed to `sys.setprofile` for
    the purpose of capturing usage data for Beacon. It contains logic to filter
    out information that Beacon wants to see, and additionally provides
    mechanisms for stopping and cleanup of the tracer.
    """

    def __init__(self, buffer, **options):
        # when the tracer starts, initialize attributes to store some state
        # related information.

        # is the tracer currently stopped?
        self.stopped = True

        # the threading module to use, if any. This needs to be set after the
        # tracer has been initialized.
        self.threading = None

        # store reference to the current thread, if any.
        self.thread = None

        # initialize attributes needed by the tracer
        self.buffer = buffer

        # TODO: ensure project root is never None.
        self.project_root = options.get('project_root')

        # prepare the path matcher
        self.path_matcher = self._prepare_path_matcher(self.project_root)

    def __repr__(self):
        """String representation of this Tracer."""
        return "<Tracer at 0x{}>".format(id(self))

    def _trace(self, frame, event, arg):
        """The trace function which is passed to `sys.setprofile`.

        We only track the `call` event here, since we only need to
        identify the usage of code, and not actually do any profiling. For all
        other events, we exit without doing anything.
        """

        filename, lineno = frame.f_code.co_filename, frame.f_lineno

        if (self.stopped and sys.getprofile() == self._trace):
            sys.setprofile(None)
            return None

        if event == 'call' and self._should_capture(filename):
            self._capture(filename, lineno)

        return self._trace

    def start(self):
        """Start the tracer.

        Return a Python function that can be passed to `sys.setprofile`.
        """
        self.stopped = False
        if self.threading:
            if self.thread is None:
                self.thread = self.threading.currentThread()
            else:
                if self.thread.ident != self.threading.currentThread().ident:
                    return self._trace
        sys.setprofile(self._trace)
        return self._trace

    def stop(self):
        """Stop this tracer.
        """
        self.stopped = True

        if (self.threading and
                self.thread.ident != self.threading.currentThread().ident):
            return

    def _should_capture(self, filename):
        """Take a frame and determine if we should capture it.

        For each filename, we should capture if it satisfies at least one of
        these conditions:
            - it starts with `self.project_root`
        """
        return self.path_matcher.search(filename)

    def _capture(self, filename, lineno):
        """Take the relevant data for this frame and store it in the
        data store.

        `filename` is the absolute path of the file where the execution
            has happened.
        `lineno` is an integer denoting the exact location of the
            function call.
        """
        self.buffer.add(filename, lineno)

    def _prepare_path_matcher(self, project_root):
        pattern = r'^{}(?P<path>.*)'.format(re.escape(project_root))
        return re.compile(pattern)
