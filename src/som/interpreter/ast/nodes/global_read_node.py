from som.interpreter.ast.frame import FRAME_AND_INNER_RCVR_IDX, read_frame
from som.interpreter.send import lookup_and_send_2
from som.vm.globals import nilObject, trueObject, falseObject

from som.interpreter.ast.nodes.expression_node import ExpressionNode


def create_global_node(global_name, universe, source_section):
    glob = global_name.get_embedded_string()
    if glob == "true":
        return _ConstantGlobalReadNode(trueObject, source_section)
    if glob == "false":
        return _ConstantGlobalReadNode(falseObject, source_section)
    if glob == "nil":
        return _ConstantGlobalReadNode(nilObject, source_section)

    assoc = universe.get_globals_association_or_none(global_name)
    if assoc is not None:
        return _CachedGlobalReadNode(assoc, source_section)

    return _UninitializedGlobalReadNode(global_name, universe, source_section)


class _UninitializedGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ["_global_name", "universe"]

    def __init__(self, global_name, universe, source_section=None):
        ExpressionNode.__init__(self, source_section)
        self._global_name = global_name
        self.universe = universe

    def execute(self, frame):
        if self.universe.has_global(self._global_name):
            return self._specialize().execute(frame)
        return lookup_and_send_2(
            read_frame(frame, FRAME_AND_INNER_RCVR_IDX),
            self._global_name,
            "unknownGlobal:",
        )

    def _specialize(self):
        assoc = self.universe.get_globals_association(self._global_name)
        cached = _CachedGlobalReadNode(assoc, self.source_section)
        return self.replace(cached)


class _CachedGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ["_assoc"]

    def __init__(self, assoc, source_section):
        ExpressionNode.__init__(self, source_section)
        self._assoc = assoc

    def execute(self, _frame):
        return self._assoc.value


class _ConstantGlobalReadNode(ExpressionNode):

    _immutable_fields_ = ["_value"]

    def __init__(self, value, source_section):
        ExpressionNode.__init__(self, source_section)
        self._value = value

    def execute(self, _frame):
        return self._value
