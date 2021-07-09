from __future__ import absolute_import

from rlib import jit
from rlib.debug import make_sure_not_resized
from rtruffle.node import Node
from som.interpreter.ast.frame import (
    create_frame_args,
    create_frame_3,
    create_frame_2,
    create_frame_1,
)

from som.vmobjects.method import AbstractMethod


def get_printable_location_1(node):
    assert isinstance(node, AstMethod)
    return node.source_section.identifier  # pylint: disable=protected-access


def get_printable_location_2(node):
    assert isinstance(node, AstMethod)
    return node.source_section.identifier  # pylint: disable=protected-access


def get_printable_location_3(node):
    assert isinstance(node, AstMethod)
    return node.source_section.identifier  # pylint: disable=protected-access


def get_printable_location_args(node):
    assert isinstance(node, AstMethod)
    return node.source_section.identifier  # pylint: disable=protected-access


jitdriver_1 = jit.JitDriver(
    greens=["node"],
    get_printable_location=get_printable_location_1,
    reds=["rcvr"],
    is_recursive=True,
    # the next line is a workaround around a likely bug in RPython
    # for some reason, the inlining heuristics default to "never inline" when
    # two different jit drivers are involved (in our case, the primitive
    # driver, and this one).
    # the next line says that calls involving this jitdriver should always be
    # inlined once (which means that things like Integer>>< will be inlined
    # into a while loop again, when enabling this driver).
    should_unroll_one_iteration=lambda self: True,
)

jitdriver_2 = jit.JitDriver(
    greens=["node"],
    get_printable_location=get_printable_location_2,
    reds=["rcvr", "arg"],
    is_recursive=True,
    should_unroll_one_iteration=lambda self: True,
)

jitdriver_3 = jit.JitDriver(
    greens=["node"],
    get_printable_location=get_printable_location_3,
    reds=["rcvr", "arg1", "arg2"],
    is_recursive=True,
    should_unroll_one_iteration=lambda self: True,
)

jitdriver_args = jit.JitDriver(
    greens=["node"],
    get_printable_location=get_printable_location_args,
    reds=["rcvr", "args"],
    is_recursive=True,
    should_unroll_one_iteration=lambda self: True,
)


class _Invokable(Node):
    """
    Only needed to work around RPython type system.
    Otherwise the parent field would point to a non-Node type (AstMethod)
    """

    _immutable_fields_ = ["_expr_or_sequence?"]
    _child_nodes_ = ["expr_or_sequence"]

    def __init__(self, expr_or_sequence):
        Node.__init__(self)
        self.expr_or_sequence = self.adopt_child(expr_or_sequence)


class AstMethod(AbstractMethod):

    _immutable_fields_ = [
        "invokable",
        "_arg_inner_access[*]",
        "_size_frame",
        "_size_inner",
        "_embedded_block_methods",
        "source_section",
    ]

    def __init__(
        self,
        signature,
        expr_or_sequence,
        arg_inner_access,
        size_frame,
        size_inner,
        embedded_block_methods,
        source_section,
    ):
        AbstractMethod.__init__(self, signature)

        assert isinstance(arg_inner_access, list)
        make_sure_not_resized(arg_inner_access)

        self._arg_inner_access = arg_inner_access
        self._size_frame = size_frame
        self._size_inner = size_inner

        self._embedded_block_methods = embedded_block_methods
        self.source_section = source_section

        self.invokable = _Invokable(expr_or_sequence)

    def set_holder(self, value):
        self._holder = value
        for method in self._embedded_block_methods:
            method.set_holder(value)

    @jit.elidable_promote("all")
    def get_number_of_arguments(self):
        return self.get_signature().get_number_of_signature_arguments()

    def invoke_1(node, rcvr):  # pylint: disable=no-self-argument
        jitdriver_1.jit_merge_point(node=node, rcvr=rcvr)
        frame = create_frame_1(
            rcvr,
            node._size_frame,
            node._size_inner,
        )
        return node.invokable.expr_or_sequence.execute(frame)

    def invoke_2(node, rcvr, arg):  # pylint: disable=no-self-argument
        jitdriver_2.jit_merge_point(node=node, rcvr=rcvr, arg=arg)
        frame = create_frame_2(
            rcvr,
            arg,
            node._arg_inner_access[0],
            node._size_frame,
            node._size_inner,
        )
        return node.invokable.expr_or_sequence.execute(frame)

    def invoke_3(node, rcvr, arg1, arg2):  # pylint: disable=no-self-argument
        jitdriver_3.jit_merge_point(node=node, rcvr=rcvr, arg1=arg1, arg2=arg2)
        frame = create_frame_3(
            rcvr,
            arg1,
            arg2,
            node._arg_inner_access,
            node._size_frame,
            node._size_inner,
        )
        return node.invokable.expr_or_sequence.execute(frame)

    def invoke_args(node, rcvr, args):  # pylint: disable=no-self-argument
        assert args is not None
        make_sure_not_resized(args)

        jitdriver_args.jit_merge_point(node=node, rcvr=rcvr, args=args)
        frame = create_frame_args(
            rcvr,
            args,
            node._arg_inner_access,
            node._size_frame,
            node._size_inner,
        )
        return node.invokable.expr_or_sequence.execute(frame)
