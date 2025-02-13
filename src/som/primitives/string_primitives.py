from rlib.objectmodel import compute_hash
from som.compiler.symbol import Symbol
from som.primitives.primitives import Primitives
from som.vm.current import current_universe

from som.vm.globals import trueObject, falseObject
from som.vmobjects.integer import Integer
from som.vmobjects.primitive import UnaryPrimitive, BinaryPrimitive, TernaryPrimitive
from som.vmobjects.string import String


def _concat(rcvr, argument):
    return String(rcvr.get_embedded_string() + argument.get_embedded_string())


def _as_symbol(rcvr):
    return current_universe.symbol_for(rcvr.get_embedded_string())


def _length(rcvr):
    return Integer(len(rcvr.get_embedded_string()))


def _equals(op1, op2):
    if isinstance(op1, String):
        if isinstance(op1, Symbol) and isinstance(op2, Symbol):
            if op1 is op2:
                return trueObject
            return falseObject
        if isinstance(op2, String):
            if op1.get_embedded_string() == op2.get_embedded_string():
                return trueObject
    return falseObject


def _substring(rcvr, start, end):
    s = start.get_embedded_integer() - 1
    e = end.get_embedded_integer()
    string = rcvr.get_embedded_string()

    if s < 0 or s >= len(string) or e > len(string) or e < s:
        return String("Error - index out of bounds")
    return String(string[s:e])


def _hashcode(rcvr):
    return Integer(compute_hash(rcvr.get_embedded_string()))


def _is_whitespace(self):
    string = self.get_embedded_string()

    for char in string:
        if not char.isspace():
            return falseObject

    if len(string) > 0:
        return trueObject
    return falseObject


def _is_letters(self):
    string = self.get_embedded_string()

    for char in string:
        if not char.isalpha():
            return falseObject

    if len(string) > 0:
        return trueObject
    return falseObject


def _is_digits(self):
    string = self.get_embedded_string()

    for char in string:
        if not char.isdigit():
            return falseObject

    if len(string) > 0:
        return trueObject
    return falseObject


class StringPrimitivesBase(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(
            BinaryPrimitive("concatenate:", self.universe, _concat)
        )
        self._install_instance_primitive(
            UnaryPrimitive("asSymbol", self.universe, _as_symbol)
        )
        self._install_instance_primitive(
            UnaryPrimitive("length", self.universe, _length)
        )
        self._install_instance_primitive(BinaryPrimitive("=", self.universe, _equals))
        self._install_instance_primitive(
            TernaryPrimitive("primSubstringFrom:to:", self.universe, _substring)
        )
        self._install_instance_primitive(
            UnaryPrimitive("hashcode", self.universe, _hashcode)
        )

        self._install_instance_primitive(
            UnaryPrimitive("isWhiteSpace", self.universe, _is_whitespace)
        )
        self._install_instance_primitive(
            UnaryPrimitive("isLetters", self.universe, _is_letters)
        )
        self._install_instance_primitive(
            UnaryPrimitive("isDigits", self.universe, _is_digits)
        )
