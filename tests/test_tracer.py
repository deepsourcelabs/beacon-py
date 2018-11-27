#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import mock
import pytest
from beacon.tracer import Tracer


@pytest.fixture
def tracer():
    return Tracer(buffer=mock.Mock(), project_root='/dummy/root')


def test_tracer_install_on_start(tracer):
    # initialize and start the tracer, and verify that it installs a
    # profiler
    tracer.start()

    assert sys.getprofile() == tracer._trace
    assert str(sys.getprofile()) == str(tracer._trace)


def test_tracer_should_remove_on_stop(tracer):
    # first start the tracer
    tracer.start()

    # then stop the tracer and assert that the profiler has been removed
    tracer.stop()
    assert sys.getprofile() is None


def test_trace_function_behavior(tracer):
    # create a dummy frame first, with filename under the project path
    mocked_frame = mock.Mock(spec=sys._getframe(1))
    mocked_frame.f_code.co_filename = '/dummy/root/foo.py'
    mocked_frame.f_lineno = 42

    tracer.start()
    # pass it to the trace function, and assert it has been captured
    tracer._trace(mocked_frame, 'call', None)

    # the add method should have been called on the buffer
    assert tracer.buffer.add.called
