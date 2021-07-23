import pytest
from rlib.string_stream import StringStream
from unittest import TestCase

from som.compiler.bc.disassembler import dump_method
from som.compiler.bc.method_generation_context import MethodGenerationContext
from som.compiler.bc.parser import Parser
from som.compiler.class_generation_context import ClassGenerationContext
from som.interp_type import is_ast_interpreter
from som.interpreter.bc.bytecodes import Bytecodes
from som.vm.current import current_universe


@pytest.mark.skipif(is_ast_interpreter(), reason="Tests are specific to bytecode interpreter")
class BytecodeGenerationTest(TestCase):

    def setUp(self):
        self.cgenc = ClassGenerationContext(current_universe)
        self.mgenc = MethodGenerationContext(current_universe)
        self.mgenc.holder = self.cgenc
        self.mgenc.add_argument("self")

    def add_field(self, name):
        self.cgenc.add_instance_field(current_universe.symbol_for(name))

    def parse_to_bytecodes(self, source):
        parser = Parser(StringStream(source), "test", current_universe)

        parser.method(self.mgenc)
        return self.mgenc.get_bytecodes()

    def test_empty_method_returns_self(self):
        bytecodes = self.parse_to_bytecodes("test = ( )")

        self.assertEqual(1, len(bytecodes))
        self.assertEqual(Bytecodes.return_self, bytecodes[0])

    def test_explicit_return_self(self):
        bytecodes = self.parse_to_bytecodes("test = ( ^ self )")

        self.assertEqual(1, len(bytecodes))
        self.assertEqual(Bytecodes.return_self, bytecodes[0])

    def test_dup_pop_argument_pop(self):
        bytecodes = self.parse_to_bytecodes("test: arg = ( arg := 1. ^ self )")
        self.assertEqual(10, len(bytecodes))
        self.assertEqual(Bytecodes.push_1, bytecodes[0])
        self.assertEqual(Bytecodes.dup, bytecodes[1])
        self.assertEqual(Bytecodes.pop_argument, bytecodes[2])
        self.assertEqual(Bytecodes.pop, bytecodes[5])

    def test_dup_pop_local_pop(self):
        bytecodes = self.parse_to_bytecodes("test = ( | local | local := 1. ^ self )")

        self.assertEqual(10, len(bytecodes))
        self.assertEqual(Bytecodes.push_1, bytecodes[0])
        self.assertEqual(Bytecodes.dup, bytecodes[1])
        self.assertEqual(Bytecodes.pop_local, bytecodes[2])
        self.assertEqual(Bytecodes.pop, bytecodes[5])

    def test_dup_pop_field_0_pop(self):
        self.add_field("field")
        bytecodes = self.parse_to_bytecodes("test = ( field := 1. ^ self )")

        dump_method(self.mgenc, "")
        self.assertEqual(8, len(bytecodes))
        self.assertEqual(Bytecodes.push_1, bytecodes[0])
        self.assertEqual(Bytecodes.dup, bytecodes[1])
        self.assertEqual(Bytecodes.pop_field_0, bytecodes[2])
        self.assertEqual(Bytecodes.pop, bytecodes[3])

    def test_dup_pop_field_pop(self):
        self.add_field("a")
        self.add_field("b")
        self.add_field("c")
        self.add_field("d")
        self.add_field("field")
        bytecodes = self.parse_to_bytecodes("test = ( field := 1. ^ self )")

        dump_method(self.mgenc, "")
        self.assertEqual(10, len(bytecodes))
        self.assertEqual(Bytecodes.push_1, bytecodes[0])
        self.assertEqual(Bytecodes.dup, bytecodes[1])
        self.assertEqual(Bytecodes.pop_field, bytecodes[2])
        self.assertEqual(Bytecodes.pop, bytecodes[5])

