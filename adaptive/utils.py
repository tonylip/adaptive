# -*- coding: utf-8 -*-

import functools
import gzip
import os
import pickle
from contextlib import contextmanager
from itertools import product

from atomicwrites import AtomicWriter


def named_product(**items):
    names = items.keys()
    vals = items.values()
    return [dict(zip(names, res)) for res in product(*vals)]


@contextmanager
def restore(*learners):
    states = [learner.__getstate__() for learner in learners]
    try:
        yield
    finally:
        for state, learner in zip(states, learners):
            learner.__setstate__(state)


def cache_latest(f):
    """Cache the latest return value of the function and add it
    as 'self._cache[f.__name__]'."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        if not hasattr(self, "_cache"):
            self._cache = {}
        self._cache[f.__name__] = f(*args, **kwargs)
        return self._cache[f.__name__]

    return wrapper


def save(fname, data, compress=True):
    fname = os.path.expanduser(fname)
    dirname = os.path.dirname(fname)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    blob = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    if compress:
        blob = gzip.compress(blob)

    with AtomicWriter(fname, "wb", overwrite=True).open() as f:
        f.write(blob)


def load(fname, compress=True):
    fname = os.path.expanduser(fname)
    _open = gzip.open if compress else open
    with _open(fname, "rb") as f:
        return pickle.load(f)


def copy_docstring_from(other):
    def decorator(method):
        return functools.wraps(other)(method)

    return decorator
