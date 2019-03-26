<p align="center">
  <img src="https://deepsource.io/images/logo-wordmark-dark.svg" />
</p>

<p align="center">
  <a href="https://deepsource.io/docs">Documentation</a> |
  <a href="https://deepsource.io/signup">Get Started</a> |
  <a href="https://gitter.im/deepsourcelabs/lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link">Developer Chat</a>
</p>

<p align="center">
  DeepSource helps you ship good quality code.
</p>

</p>

---

# Beacon Python client library - beacon-py

[![Build Status](https://travis-ci.org/deepsourcelabs/beacon-py.svg?branch=master)](https://travis-ci.org/deepsourcelabs/beacon-py)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beacon.svg)

**DeepSource Dashboard** - [https://deepsource.io/gh/deepsourcelabs/beacon-py/](https://deepsource.io/gh/deepsourcelabs/beacon-py/)

```
NOTE: beacon-py is currently in a pre-release phase, so we do not recommend using it at the moment.
```

Beacon runs inside your Python applications and collects metrics around how the code behaves in runtime &mdash; usage of modules, volume of exceptions, to name a few. Python versions 2.7 & 3.4-3.7 are officially supported.

Beacon is open-source, and we are actively looking for contributors for the project. If you want to lend a hand, pick up [an issue](https://github.com/deepsourcelabs/beacon-py/issues) or join the chatter on IRC at **#deepsourcelabs**.

## Installation

To install beacon-py, use pipenv (or pip):

```bash
$ pipenv install beacon
```

## Running tests

```bash
$ make test
```

## Generating gRPC client stubs

```bash
$ make generate_grpc_client
```

**NOTE:** Apparently, the stub generator generates `beacon/beacon_pb2_grpc.py` with a bad import of `beacon_pb2`. After generating the stubs, the import has to be changed manually.

Find the line:
```python
import beacon_pb2 as beacon__pb2  # existing bad import, which should be removed
```

And replace it with:
```python
from . import beacon_pb2 as beacon__pb2  # new import that should be added
```
