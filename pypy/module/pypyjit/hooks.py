
from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters

from pypy.interpreter.error import OperationError
from pypy.module.pypyjit.interp_resop import (Cache, wrap_greenkey,
    WrappedOp, W_JitLoopInfo, wrap_oplist)

class PyPyJitIface(JitHookInterface):
    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        space = self.space
        cache = space.fromcache(Cache)
        if cache.in_recursion:
            return
        if space.is_true(cache.w_abort_hook):
            cache.in_recursion = True
            oplist_w = wrap_oplist(space, logops, operations)
            try:
                try:
                    space.call_function(cache.w_abort_hook,
                        space.wrap(jitdriver.name),
                        wrap_greenkey(space, jitdriver, greenkey, greenkey_repr),
                        space.wrap(Counters.counter_names[reason]),
                        space.newlist(oplist_w)
                    )
                except OperationError, e:
                    e.write_unraisable(space, "jit hook ", cache.w_abort_hook)
            finally:
                cache.in_recursion = False

    def on_trace_too_long(self, jitdriver, greenkey, greenkey_repr):
        space = self.space
        cache = space.fromcache(Cache)
        if cache.in_recursion:
            return
        if space.is_true(cache.w_trace_too_long_hook):
            cache.in_recursion = True
            try:
                try:
                    space.call_function(cache.w_trace_too_long_hook,
                        space.wrap(jitdriver.name),
                        wrap_greenkey(space, jitdriver, greenkey, greenkey_repr))
                except OperationError, e:
                    e.write_unraisable(space, "jit hook", cache.w_trace_too_long_hook)
            finally:
                cache.in_recursion = False

    def after_compile(self, debug_info):
        self._compile_hook(debug_info, is_bridge=False)

    def after_compile_bridge(self, debug_info):
        self._compile_hook(debug_info, is_bridge=True)

    def before_compile(self, debug_info):
        pass

    def before_compile_bridge(self, debug_info):
        pass

    def _compile_hook(self, debug_info, is_bridge):
        space = self.space
        cache = space.fromcache(Cache)
        if cache.in_recursion:
            return
        if space.is_true(cache.w_compile_hook):
            w_debug_info = W_JitLoopInfo(space, debug_info, is_bridge,
                                         cache.compile_hook_with_ops)
            cache.in_recursion = True
            try:
                try:
                    space.call_function(cache.w_compile_hook,
                                        space.wrap(w_debug_info))
                except OperationError, e:
                    e.write_unraisable(space, "jit hook ", cache.w_compile_hook)
            finally:
                cache.in_recursion = False

pypy_hooks = PyPyJitIface()
