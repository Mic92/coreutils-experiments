cmake_minimum_required(VERSION 3.7.2)
include(ExternalProject)

find_program(KLEE_BINARY
  NAMES klee
)

find_package(PythonInterp 3.4 REQUIRED)

if (NOT KLEE_BINARY)
  message(STATUS "Failed to find klee binary")
endif()

file(COPY sandbox-src DESTINATION sandbox)
configure_file(testing-env.sh.in testing-env.sh COPYONLY)
configure_file(test-program.py.in test-program @ONLY)

# Find GNU make
find_program(MAKE_BINARY
  NAMES make gmake
)

if (NOT MAKE_BINARY)
  message(STATUS "Failed to find make binary")
endif()

ExternalProject_Add(coreutils-6.10-gcov
  URL https://ftp.gnu.org/gnu/coreutils/coreutils-6.10.tar.gz
  CONFIGURE_COMMAND ${CMAKE_COMMAND} -E env "CFLAGS=-g -fprofile-arcs -ftest-coverage" ${CMAKE_CURRENT_SOURCE_DIR}/coreutils-6.10-gcov/configure --prefix=<INSTALL_DIR> --disable-nls
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/coreutils-6.10-gcov
  BUILD_COMMAND ${MAKE_BINARY})

# Find wllvm
find_program(WLLVM_BINARY
  NAMES wllvm
)

if (NOT WLLVM_BINARY)
  message(STATUS "Failed to find wllvm program (https://github.com/travitch/whole-program-llvm)")
endif()

set(LLVM_COMPILER "clang" CACHE STRING "Compiler used to compile llvm bytecode for coreutils")

find_program(LLVM_COMPILER_BINARY
  NAMES ${LLVM_COMPILER}
)

if (NOT LLVM_COMPILER_BINARY)
  message(STATUS "Failed to find ${LLVM_COMPILER}")
endif()

ExternalProject_Add(coreutils-6.10-llvm
  URL https://ftp.gnu.org/gnu/coreutils/coreutils-6.10.tar.gz
  CONFIGURE_COMMAND ${CMAKE_COMMAND} -E env CFLAGS=-g
  LLVM_COMPILER=${LLVM_COMPILER} CC=wllvm ${CMAKE_CURRENT_SOURCE_DIR}/coreutils-6.10-llvm/configure --prefix=<INSTALL_DIR> --disable-nls
  BUILD_COMMAND ${CMAKE_COMMAND} -E env LLVM_COMPILER=clang CC=${WLLVM_BINARY} ${MAKE_BINARY}
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/coreutils-6.10-llvm
  INSTALL_COMMAND make install)

externalproject_add_step(coreutils-6.10-llvm
  extract-bytecode
  COMMAND find <INSTALL_DIR> -executable -type f | xargs -I '{}' extract-bc '{}' 
  WORKING_DIRECTORY <INSTALL_DIR>/bin
  DEPENDEES install)
