cmake_minimum_required(VERSION 3.12)
project(icepack_fortran
        VERSION 0.0.1
        LANGUAGES Fortran)

find_package(Python COMPONENTS Interpreter Development REQUIRED)

set(CMAKE_Fortran_MODULE_DIRECTORY ${icepack_fortran_BINARY_DIR}/include)
INSTALL(DIRECTORY ${CMAKE_Fortran_MODULE_DIRECTORY}/ DESTINATION include)

enable_testing()
add_subdirectory(fortran)
add_subdirectory(python)
