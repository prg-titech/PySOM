PySOM - The Simple Object Machine Smalltalk
===========================================

Threaded Code Generation
------------

[Threaded code][1] is a code style that essentially consists of a call instruction to each handler.
So, **threaded code generation** is a technique to produce threaded code-style code with RPython.
This customized PySOM implementation demonstrates how threaded code generation is implemented and how it works.

To compile the threaded code PySOM, you should prepare a customized PyPy implementation.

    hg clone https://foss.heptapod.net/pypy/pypy -r threaded-code-generation

Then, you need to type the following command to build the threaded code PySOM:

    make som-bc-jit SOM_TIER=1

`SOM_TIER` is an environmental variable to specify the starting level of compilation.

- Starting from threaded code generation: `make som-bc-jit SOM_TIER=1`
    - Producing `som-bc-jit-tier1`
- Starting from tracing JIT: `make som-bc-jit SOM_TIER=2`
    - Producing `som-bc-jit-tier2`
- Enable hybrid compilation, starting from threaded code generation and then shifting to tracing compilation: `make som-bc-jit SOM_TIER=3`
    - Producing `som-bc-jit-tier3`

[1]: https://www.complang.tuwien.ac.at/forth/threaded-code.html

Building Threaded Code Generation
------------

You need to add [`rtime_ext`](https://github.com/prg-titech/rtime_ext) and [`rkrun`](https://github.com/3tty0n/rkrun) to `PYTHONPATH` build this version of PySOM.
Both libraries are needed to measure benchmarking data.

```shell
export PYTHONPATH=/path/to/rtime_ext:/path/to/rkrun:$PYTHONPATH
```

Benchmarking
------------

To remove noises, we recommend add `isolcpus=1-3` for example to `GRUB_CMDLINE_LINUX_DEFAULT`.

For benchmarking, the prerequisite is [ReBench][2] and our [SOM][3] repository.

ReBench, which is developed by Dr. Stefan Marr, a benchmarking tool written in Python.
ReBench is supported in Python 3. To install ReBench:

    pip3 install rebench

Also, you need to install SOM standard library.  To install our customized SOM:

    # you are currently in PySOM repository
    cd ..
    git clone https://github.com/prg-titech/SOM.git

[2]: https://github.com/smarr/ReBench
[3]: https://github.com/prg-titech/SOM

Introduction
------------

SOM is a minimal Smalltalk dialect that was used to teach at the [Hasso
Plattner Institute][SOM] and before that at the University of Århus
(Denmark) where it was used for teaching and as the foundation for [Resilient
Smalltalk][RS].

In addition to PySOM, other implementations exist for Java (SOM, TruffleSOM),
C (CSOM), C++ (SOM++), Python (PySOM), and Squeak/Pharo Smalltalk (AweSOM).

A simple Hello World looks like:

```Smalltalk
Hello = (
  run = (
    'Hello World!' println.
  )
)
```

This repository contains a Python-base implementation of SOM, including
SOM's standard library, and a number of benchmarks. The [main project
page][SOMst] has links to other SOM VM implementations.

PySOM implementation use either an abstract-syntax-tree or a
bytecode-based interpreter. One can choose between them with the `SOM_INTERP` environment variable.

 - AST-based interpreter: `SOM_INTERP=AST`
 - bytecode-based interpreter: `SOM_INTERP=BC`

To check out the code, run:

    git clone --recurse-submodules https://github.com/SOM-st/PySOM.git

Note the `--recurse-submodules` option. It makes sure that the core library,
i.e., the Smalltalk code is downloaded.

PySOM's tests can be executed with:

    SOM_INTERP=AST ./som.sh -cp Smalltalk TestSuite/TestHarness.som

A simple Hello World program can be started with:

    SOM_INTERP=AST ./som.sh -cp Smalltalk Examples/Hello.som

To compile PySOM, a recent PyPy is recommended and the RPython source
code is required. The source distribution of PyPy 7.3 can be used like this:

    wget https://downloads.python.org/pypy/pypy2.7-v7.3.1-src.tar.bz2
    tar xvf pypy2.7-v7.3.1-src.tar.bz2
    export PYPY_DIR=`pwd`/pypy2.7-v7.3.1-src/

Information on previous authors are included in the AUTHORS file. This code is
distributed under the MIT License. Please see the LICENSE file for details.


History
-------

In 2013, the implementations of PySOM, RPySOM, and RTruffleSOM where split
over multiple repositories. Since end of 2020, they are reunited here and PySOM
can be used with Python 2.7, Python 3.8, as well as compiled with RPython.
Thus, https://github.com/SOM-st/PySOM is again the only and the canonical
repository.


Build Status
------------

Thanks to GitHub Actions, all pull requests of this repository are automatically tested.
The current build status is: [![Build Status](https://github.com/SOM-st/PySOM/actions/workflows/ci.yml/badge.svg)](https://github.com/SOM-st/PySOM/actions)

 [SOM]: http://www.hpi.uni-potsdam.de/hirschfeld/projects/som/
 [SOMst]: https://travis-ci.org/SOM-st/
 [RS]:  http://dx.doi.org/10.1016/j.cl.2005.02.003
