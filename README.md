# Coreutils experiment with [Klee](http://klee.github.io/docs/coreutils-experiments/)

This repository uses the latest version of Klee to reproduce the bugs found in coreutils 6.10
as discussed in the [KLEE OSDI’08 paper](http://llvm.org/pubs/2008-12-OSDI-KLEE.html).


Commit log of bug fixes:

- https://github.com/coreutils/coreutils/commit/a0851554bd52038ed47e46ee521ce74a5a09f747
- https://github.com/coreutils/coreutils/commit/72d052896a9092b811961a8f3e6ca5d151a59be5
- https://github.com/coreutils/coreutils/commit/b58a8b4ef588ec8a365b920d12e27fdd71aa48d1
- https://github.com/coreutils/coreutils/commit/eb8fa94f2cf030d625c12ad68bb8883de204c196
- https://github.com/coreutils/coreutils/commit/7cb24684cc4ef96bb25dfc1c819acfc3b98d9442
- https://github.com/coreutils/coreutils/commit/6856089f7bfaca2709b303f01dae001a30930b61


## Build

dependencies see default.nix

```bash
$ mkdir build && cd build
$ cmake -B. -H.. -GNinja -DCMAKE_EXPORT_COMPILE_COMMANDS=1
$ ninja
```
