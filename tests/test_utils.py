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


def test_dsn_validator_with_valid_dsn():

    valid_dsn_list = [
        "http://43f62c942790426c8b41220aade4a0d8@domain.com/33",
        "http://43f62c942790426c8b41220aade4a0d8@stagin.domain.com/33",
        "https://43f62c942790426c8b41220aade4a0d8@domain.io/33",
        "https://43f62c942790426c8b41220aade4a0d8@domain.io:80/33",
        "https://43f62c942790426c8b41220aade4a0d8@domain.com/33/"
    ]

    # No exceptions should be raised as all dsns are valid
    for dsn_input_string in valid_dsn_list:
        dsn = utils.DSN(dsn_input_string)
        assert str(dsn) in dsn_input_string


def test_dsn_validator_with_invalid_dsn():

    invalid_dsn_list = [
        "",
        "foobar"
        "43f62c942790426c8b41220aade4a0d8@domain.com/",
        "domain.com",
        None,
        {},
        0,
        [],
    ]

    for dsn in invalid_dsn_list:
        
        with pytest.raises(ValueError) as exc:
            utils.DSN(dsn)
            assert str(exc.value) == utils.DSN.ERROR_MESSAGE


def test_dsn_validator_with_invalid_scheme():

    valid_dsn_list = [
        "ftp://43f62c942790426c8b41220aade4a0d8@domain.com/33",
        "amqp://43f62c942790426c8b41220aade4a0d8@domain.com/33"
    ]

    # Should raise value error as only http/https schemes are allowed
    for dsn in valid_dsn_list:

        with pytest.raises(ValueError) as exc:
            utils.DSN(dsn)
            assert str(exc.value) == utils.DSN.ERROR_MESSAGE


def test_dsn_validator_with_invalid_api_key():

    invalid_dsn_list = [
        "https://43q62c942790426s8b41220aade4a0d8@domain.com/33",
        "https://43f62c942790426c8b41220aade4@domain.com/33"
        "https://aff7912c-e170-47cb-ba92-42011c35cbc3@domain.com/33"
    ]

    # Should raise value error as api keys are valid uuid4 hex strings
    for dsn in invalid_dsn_list:

        with pytest.raises(ValueError) as exc:
            utils.DSN(dsn)
            assert str(exc.value) == utils.DSN.ERROR_MESSAGE


def test_dsn_validator_with_invalid_hostname():

    invalid_dsn_list = [
        "https://43f62c942790426c8b41220aade4a0d8@do#main.com/33",
        "https://43f62c942790426c8b41220aade4a0d8@domain.c/33"
        "https://43f62c942790426c8b41220aade4a0d8@domain.com:foo/33"
    ]

    # Should raise value error as provided hostnames are not valid
    for dsn in invalid_dsn_list:

        with pytest.raises(ValueError) as exc:
            utils.DSN(dsn)
            assert str(exc.value) == utils.DSN.ERROR_MESSAGE


def test_dsn_validator_with_invalid_repository_id():

    invalid_dsn_list = [
        "https://43f62c942790426c8b41220aade4a0d8@domain.com/33a",
        "https://43f62c942790426c8b41220aade4a0d8@domain.com/33/foo/bar"
        "https://43f62c942790426c8b41220aade4a0d8@domain.com/"
    ]

    # Should raise value error as provided repository_ids are not valid
    for dsn in invalid_dsn_list:

        with pytest.raises(ValueError) as exc:
            utils.DSN(dsn)
            assert str(exc.value) == utils.DSN.ERROR_MESSAGE

