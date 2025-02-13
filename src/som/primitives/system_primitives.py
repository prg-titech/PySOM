import time

from rlib import rgc, jit
from rlib.streamio import open_file_as_stream, readall_from_stream

from som.primitives.primitives import Primitives
from som.vm.current import current_universe
from som.vmobjects.integer import Integer
from som.vmobjects.double import Double
from som.vm.globals import nilObject, trueObject, falseObject
from som.vm.universe import std_print, std_println, error_print, error_println
from som.vmobjects.primitive import UnaryPrimitive, BinaryPrimitive, TernaryPrimitive


def _load(_rcvr, arg):
    result = current_universe.load_class(arg)
    return result if result else nilObject


def _exit(_rcvr, error):
    return current_universe.exit(error.get_embedded_integer())


def _global(_rcvr, argument):
    result = current_universe.get_global(argument)
    return result if result else nilObject


def _has_global(_rcvr, arg):
    if current_universe.has_global(arg):
        return trueObject
    return falseObject


def _global_put(_rcvr, argument, value):
    current_universe.set_global(argument, value)
    return value


def _print_string(rcvr, argument):
    std_print(argument.get_embedded_string())
    return rcvr


def _print_newline(rcvr):
    std_println()
    return rcvr


def _error_print(rcvr, string):
    error_print(string.get_embedded_string())
    return rcvr


def _error_println(rcvr, string):
    error_println(string.get_embedded_string())
    return rcvr


def _time(_rcvr):
    from som.vmobjects.integer import Integer

    since_start = time.time() - current_universe.start_time
    return Integer(int(since_start * 1000))


def _ticks(_rcvr):
    from som.vmobjects.integer import Integer

    since_start = time.time() - current_universe.start_time
    return Integer(int(since_start * 1000000))


def _clock_monotonic(_rcvr):
    from som.vmobjects.integer import Integer
    from rtime_ext import clock_monotonic

    return Integer(int(clock_monotonic() * 1000000))


@jit.dont_look_inside
def _load_file(_rcvr, file_name):
    try:
        input_file = open_file_as_stream(file_name.get_embedded_string(), "r")
        try:
            result = readall_from_stream(input_file)
            from som.vmobjects.string import String

            return String(result)
        finally:
            input_file.close()
    except (OSError, IOError):
        pass
    return nilObject


@jit.dont_look_inside
def _full_gc(_rcvr):
    rgc.collect()
    return trueObject


# Krun features

try:
    from rkrun import rkrun

    def _krun_init(_rcvr):
        rkrun.krun_init()

    def _krun_done(_rcvr):
        rkrun.krun_done()

    def _krun_measure(_rcvr, arg):
        assert isinstance(arg, Integer)
        rkrun.krun_measure(arg.get_embedded_integer())

    def _krun_get_wall_clock(_rcvr, arg):
        assert isinstance(arg, Integer)
        result = rkrun.krun_get_wall_clock(arg.get_embedded_integer())
        return Double(result)

    def _krun_get_core_cycles_double(_rcvr, arg1, arg2):
        assert isinstance(arg1, Integer)
        assert isinstance(arg2, Integer)
        result = rkrun.krun_get_core_cycles_double(arg1.get_embedded_integer(), arg2.get_embedded_integer())
        return Double(result)

except ImportError:
    pass


class SystemPrimitivesBase(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(BinaryPrimitive("load:", self.universe, _load))
        self._install_instance_primitive(BinaryPrimitive("exit:", self.universe, _exit))
        self._install_instance_primitive(
            BinaryPrimitive("hasGlobal:", self.universe, _has_global)
        )
        self._install_instance_primitive(
            BinaryPrimitive("global:", self.universe, _global)
        )
        self._install_instance_primitive(
            TernaryPrimitive("global:put:", self.universe, _global_put)
        )
        self._install_instance_primitive(
            BinaryPrimitive("printString:", self.universe, _print_string)
        )
        self._install_instance_primitive(
            UnaryPrimitive("printNewline", self.universe, _print_newline)
        )
        self._install_instance_primitive(
            BinaryPrimitive("errorPrint:", self.universe, _error_print)
        )
        self._install_instance_primitive(
            BinaryPrimitive("errorPrintln:", self.universe, _error_println)
        )

        self._install_instance_primitive(UnaryPrimitive("time", self.universe, _time))
        self._install_instance_primitive(UnaryPrimitive("ticks", self.universe, _ticks))
        self._install_instance_primitive(
            UnaryPrimitive("clock_monotonic", self.universe, _clock_monotonic)
        )
        self._install_instance_primitive(
            UnaryPrimitive("fullGC", self.universe, _full_gc)
        )

        self._install_instance_primitive(
            BinaryPrimitive("loadFile:", self.universe, _load_file)
        )

        try:
            from rkrun import rkrun

            self._install_instance_primitive(
                UnaryPrimitive("krunInit", self.universe, _krun_init)
            )
            self._install_instance_primitive(
                UnaryPrimitive("krunDone", self.universe, _krun_done)
            )
            self._install_instance_primitive(
                BinaryPrimitive("krunMeasure", self.universe, _krun_measure)
            )
            self._install_instance_primitive(
                BinaryPrimitive("krunGetWallclock", self.universe, _krun_get_wall_clock)
            )
            self._install_instance_primitive(
                TernaryPrimitive(
                    "krunGetCoreCyclesDouble",
                    self.universe,
                    _krun_get_core_cycles_double,
                )
            )
        except ImportError:
            pass
