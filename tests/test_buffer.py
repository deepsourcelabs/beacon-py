#!/usr/bin/env python
# -*- coding: utf-8 -*-
from beacon.buffer import Buffer
import mock
import pytest


@pytest.fixture
def empty_buffer():
    mock_agent = mock.Mock()
    mock_agent.stream_id = 'dummy'
    new_buffer = Buffer(mock_agent, 'f')
    return new_buffer


@pytest.fixture
def sample_buffer(empty_buffer):
    # add some filename-locations
    empty_buffer.add('foo.py', 42)
    empty_buffer.add('foo.py', 42)
    empty_buffer.add('foo.py', 42)
    empty_buffer.add('baz/bar.py', 1)

    return empty_buffer


def test_buffer_add(sample_buffer):
    # verify the counter
    assert sample_buffer.counter[('foo.py', 42)] == 3
    assert sample_buffer.counter[('baz/bar.py', 1)] == 1


def test_buffer_flush_success_should_clear_counter(sample_buffer):
    sample_buffer.flush()
    # the counter should be empty now
    assert len(sample_buffer.counter) == 0
    assert sample_buffer.agent.stub.Transmit.called


def test_buffer_should_not_trasmit_for_empty_counter(empty_buffer):
    empty_buffer.flush()
    assert not empty_buffer.agent.stub.Transmit.called


def test_buffer_should_add_to_unflushed_on_trasmit_failure(sample_buffer):
    # make transmit raise error
    sample_buffer.agent.stub.Transmit.side_effect = mock.Mock(side_effect=Exception())  # noqa
    sample_buffer.flush()
    assert len(sample_buffer.unflushed) == 1


def test_buffer_should_clear_unflushed_if_flush_works(sample_buffer):
    # first make transmit raise error
    sample_buffer.agent.stub.Transmit.side_effect = mock.Mock(side_effect=Exception())  # noqa
    sample_buffer.flush()

    # now, add more stuff to the buffer
    sample_buffer.add('new_file.py', 4)

    # assert that counter and unflushed both have data
    assert len(sample_buffer.counter) > 0
    assert len(sample_buffer.unflushed) > 0

    # now make transmission work again, and flush everything
    sample_buffer.agent.stub.Transmit.side_effect = mock.Mock(side_effect=mock.Mock())  # noqa
    sample_buffer.flush()

    # assert that everything has been flushed
    assert len(sample_buffer.counter) == 0
    assert len(sample_buffer.unflushed) == 0

    # assert that Transmit was called thrice in total: once earlier, and twice this time.  # noqa
    assert sample_buffer.agent.stub.Transmit.call_count == 3
