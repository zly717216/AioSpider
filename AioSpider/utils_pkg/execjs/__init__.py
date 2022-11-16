#!/usr/bin/env python3
# -*- coding: ascii -*-
'''r
Run JavaScript code from Python.

PyExecJS is a porting of ExecJS from Ruby.
PyExecJS automatically picks the best runtime available to evaluate your JavaScript program,
then returns the result to you as a Python object.

A short example:

>>> import execjs
>>> execjs.eval("'red yellow blue'.split(' ')")
['red', 'yellow', 'blue']
>>> ctx = execjs.compile("""
...     function add(x, y) {
...         return x + y;
...     }
... """)
>>> ctx.call("add", 1, 2)
3
'''
from __future__ import unicode_literals, division, with_statement

from AioSpider.utils_pkg.execjs._exceptions import (
    Error,
    RuntimeError,
    ProgramError,
    RuntimeUnavailableError,
)

from AioSpider.utils_pkg.execjs import _runtimes
from AioSpider.utils_pkg.execjs._external_runtime import ExternalRuntime
from AioSpider.utils_pkg.execjs._abstract_runtime import AbstractRuntime


__all__ = """
    get register runtimes get_from_environment exec_ eval compile
    ExternalRuntime
    Error RuntimeError ProgramError RuntimeUnavailableError
""".split()


register = _runtimes.register
get = _runtimes.get
runtimes = _runtimes.runtimes
get_from_environment = _runtimes.get_from_environment


def eval(source, cwd=None):
    return get().eval(source, cwd)
eval.__doc__ = AbstractRuntime.eval.__doc__


def exec_(source, cwd=None):
    return get().exec_(source, cwd)
exec_.__doc__ = AbstractRuntime.exec_.__doc__


def compile(source, cwd=None):
    return get().compile(source, cwd)
compile.__doc__ = AbstractRuntime.compile.__doc__
