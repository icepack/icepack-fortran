add_executable(wrapper_test wrapper_test.f90)
target_link_libraries(wrapper_test icepack_fortran)
add_test(wrapper_test wrapper_test ${icepack_fortran_SOURCE_DIR}/fortran/test/config.json)
set_tests_properties(wrapper_test PROPERTIES ENVIRONMENT
                     "PYTHONPATH=${icepack_fortran_SOURCE_DIR}/python/")
