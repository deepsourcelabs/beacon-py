#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The buffer takes the individual events, aggregates them on the basis
of filename and location, and stores them in a batch, which can be flushed
to the server at defined time intervals."""
import threading
import time
from collections import Counter, deque
from copy import deepcopy

from . import beacon_pb2


class Buffer(object):
    def __init__(self, agent, event_type):
        """The Buffer stores the batch of events that can be sent to the
           server periodically.

        :param agent: the agent instance that is using this buffer.

        :param event_type: the type of events that are being stored in
                           this buffer. Should be one of `f` and `e`.

        :return: an instance of Buffer.
        """

        self.agent = agent

        self.event_type = event_type

        # this attribute stores the counter of events; the keys are a
        # two-tuple of filename and location.
        self.counter = Counter()

        # create a mutex for operations on the counter, for thread safety
        self.counter_lock = threading.Lock()

        # initialization time of this buffer
        self.init_time = int(time.time())

        # store the message batches that could not be flushed due to the server
        # due to some reason, hoping we'd be able to flush them later
        self.unflushed = deque()

    def add(self, filename, location):
        """Take the filename and location, and add it to the counter.
        """
        with self.counter_lock:
            self.counter[(filename, location)] += 1

    def flush(self):
        """Send the data in this buffer to the server after serializing it,
        and then clear the buffer.

        If the data transmission fails, the serialized messages are stored
        separately.
        """

        # create a copy of the current counter and clear it
        counter_data = None
        init_time = self.init_time

        with self.counter_lock:
            # create a copy of the counter for further processing
            counter_data = deepcopy(self.counter)

            # clear the counter
            self.counter.clear()

            # reset the init_time
            self.init_time = int(time.time())

        message = self._serialize_batch(counter=counter_data,
                                        timestamp=init_time)

        # TODO: do this in a better way
        if not len(message.events):
            return
        self._transmit(message)

    def _serialize_batch(self, counter, timestamp):
        """Take the counter data and return a serialized batch message that
        can be sent to the server. Additionally, it needs the start_time and
        end_time of capture of this set of events.
        """
        events = deque(maxlen=len(counter))
        for (loc, count) in counter.items():
            event = beacon_pb2.Event(file_path=loc[0], location=loc[1],
                                     count=count)
            events.append(event)

        batch = beacon_pb2.Batch(stream_id=self.agent.stream_id,
                                 event_type=self.event_type,
                                 events=events,
                                 timestamp=timestamp)

        return batch

    def _transmit(self, batch):
        """Take a batch message and transmit it to the server. If transmission
        fails, add the message to the unflushed list of messages.
        """
        try:
            for event in batch.events:
                print("{}:{} {}".format(event.file_path, event.location,
                                        event.count))
            self.agent.stub.Transmit(batch)
            self.agent.logger.info(
                "Transmission successful. "
                "{} events sent.".format(len(batch.events)))
        except Exception as e:
            self.agent.logger.error(
                "Error sending events. Adding the batch to unflushed."
            )
            self.agent.logger.error(e)
            self.unflushed.append(batch)
        else:
            # since the transmission is successful, try to flush pending
            # messages, if any.
            while len(self.unflushed):
                # try to send the leftmost message from unflushed
                message = self.unflushed.popleft()
                try:
                    self.agent.stub.Transmit(message)
                except Exception:
                    # if there is an error sending the message, then append the
                    # message back to the left of unflushed,
                    # and exit this loop.
                    self.unflushed.appendleft(message)
                    break
