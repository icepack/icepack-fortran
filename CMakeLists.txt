cmake_minimum_required(VERSION 3.0)
project(icepack_fortran
        VERSION 0.0.1
        LANGUAGES Fortran)

find_package(PythonLibs 3 REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

set(CMAKE_Fortran_MODULE_DIRECTORY ${icepack_fortran_BINARY_DIR}/include)

enable_testing()
add_subdirectory(fortran)
add_subdirectory(python)
