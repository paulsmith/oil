#!/usr/bin/python
"""
scoped_resource.py
"""
from __future__ import print_function

import os
import sys

from mylib import log
from typing import List, Any


def Error(error):
  # type: (bool) -> None
  if error:
    raise RuntimeError()


class _ErrExit(object):
  """Manages the errexit setting.

  - The user can change it with builtin 'set' at any point in the code.
  - These constructs implicitly disable 'errexit':
    - if / while / until conditions
    - ! (part of pipeline)
    - && ||

  An _ErrExit object prevents these two mechanisms from clobbering each other.
  """

  def __init__(self):
    # type: () -> None
    self.errexit = False  # the setting
    self.stack = []  # type: List[bool]

  def Context(self, *args):
    # type: (*Any) -> _ErrExit__Context
    return _ErrExit__Context(self, *args)

  def Push(self, dummy_arg):
    # type: (str) -> None
    """Temporarily disable errexit."""
    log('Push %r', dummy_arg)
    if self.errexit:
      self.errexit = False
      self.stack.append(True)  # value to restore
    else:
      self.stack.append(False)

  def Pop(self):
    # type: () -> None
    """Restore the previous value."""
    self.errexit = self.stack.pop()


class _ErrExit__Context(object):
  def __init__(self, state, *args):
    # type: (_ErrExit, *Any) -> None
    self.state = state  # underlying stack
    self.args = args

  def __enter__(self):
    # type: () -> None
    self.state.Push(*self.args)

  def __exit__(self, type, value, traceback):
    # type: (Any, Any, Any) -> bool
    self.state.Pop()
    return False  # Allows a traceback to occur


# C++ translation
#
# class _ErrExit__Context;  // forward declaration
# class _ErrExit {
# };
#
# class _ErrExit__Context {
#   _ErrExit__Context(_ErrExit* state) : state_(state) {
#     state->Push();
#   }
#  ~_ErrExit__Context() {
#     state->Pop();
#   }
# };


def DoWork(e, do_raise):
  # type: (_ErrExit, bool) -> None

  # problem
  # with self.mem.ctx_Call(...)
  #  PushCall/PopCall
  # with self.mem.ctx_Temp(...)
  #  PushTemp/PopCall
  # with self.mem.ctx_Source(...)
  #  PushSource/PopSource
  #
  # Scope_Call
  # Scope_Temp

  # PROBLEM: WE LOST TYPE CHECKING!
  #with e.Context('zz') as _:
  with e.Context(42) as _:
    log('  in context errexit %d', e.errexit)
    if do_raise:
      Error(do_raise)


def run_tests():
  # type: () -> None

  # Use cases:
  #
  # Many in cmd_exec.py
  #
  # fd_state.Push(...) and Pop
  # BeginAlias, EndAlias
  # PushSource, PopSource (opens files)
  #   source
  #   eval -- no file opened, but need to change the current file
  # PushTemp, PopTemp for env bindings
  # PushErrExit, PopErrExit
  # loop_level in cmd_exec

  e = _ErrExit()
  e.errexit = True  # initially true

  for do_raise in [False, True]:
    log('')
    log('-> errexit %d', e.errexit)
    try:
      DoWork(e, do_raise)
    except RuntimeError:
      log('exited with exception')
    log('<- errexit %d', e.errexit)

  # C++ translation
  #
  # _Errexit e;
  # e.errexit = true;
  #
  # log("-> errexit %d", e.errexit)
  # {
  #   _ErrExit__Context(e);
  #   log("  errexit %d", e.errexit)
  # }
  # log("<- errexit %d", e.errexit)


def run_benchmarks():
  # type: () -> None
  log('TODO')


if __name__ == '__main__':
  if os.getenv('BENCHMARK'):
    log('Benchmarking...')
    run_benchmarks()
  else:
    run_tests()
