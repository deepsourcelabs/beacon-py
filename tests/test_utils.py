#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import mock
import pytest
from beacon import utils


def test_timer_should_call_passed_function():
    # create a dummy function
    dummy_function = mock.Mock()

    # create a timer with interval 0.1 sec
    timer = utils.Timer(0.1, dummy_function, 'foo', 'bar', baz=True)

    # start the timer, wait for 1.1 sec, stop the timer and assert if
    # dummy_function was called properly
    timer.start()
    # assert that the function shouldn't have been called yet.
    assert not dummy_function.called
    time.sleep(1.1)
    timer.stop()

    # the function shouldn't have been called 10 times by now.
    assert len(dummy_function.mock_calls) == 10

    # assert that the function has been called with the correct args and kwargs
    dummy_function.assert_has_calls([mock.call('foo', 'bar', baz=True)])


def test_timer_should_raise_proper_exceptions():
    timer = utils.Timer(1, mock.Mock())

    # start the timer
    timer.start()

    # it should raise an exception if the timer is started again
    with pytest.raises(Exception) as exc:
        timer.start()
    timer.stop()
    assert str(exc.value) == "This timer is already running."

    # since the timer is now stopped, trying to stop it should raise
    # an exception
    with pytest.raises(Exception) as exc:
        timer.stop()
    assert str(exc.value) == "This timer has already been stopped."
