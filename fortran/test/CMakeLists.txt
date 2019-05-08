# Create the input mesh for the test by calling gmsh
find_program(GMSH "gmsh" REQUIRED)

set(GEO_FILE "${CMAKE_CURRENT_SOURCE_DIR}/mesh.geo")
set(MESH_FILE "${CMAKE_CURRENT_BINARY_DIR}/mesh.msh")
add_custom_command(OUTPUT ${MESH_FILE}
                   COMMAND ${GMSH} -2 ${GEO_FILE} -o ${MESH_FILE}
                   DEPENDS ${GEO_FILE})

add_custom_target(mesh ALL DEPENDS ${MESH_FILE})


# Create the configuration file for the test
find_program(PYTHON "python" REQUIRED)

set(SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/generate_data.py")
set(CONFIG_FILE "${CMAKE_CURRENT_BINARY_DIR}/config.json")

add_custom_command(OUTPUT ${CONFIG_FILE}
                   COMMAND ${PYTHON} ${SCRIPT} ${CMAKE_CURRENT_BINARY_DIR}
                   DEPENDS ${SCRIPT})

add_custom_target(config_file ALL DEPENDS ${CONFIG_FILE})


# Build the test and make it depend on the mesh and config file
add_executable(wrapper_test wrapper_test.f90)
target_link_libraries(wrapper_test icepack_fortran)
add_test(NAME wrapper_test
         COMMAND wrapper_test ${CONFIG_FILE})
set_tests_properties(wrapper_test PROPERTIES ENVIRONMENT
                     "PYTHONPATH=${icepack_fortran_SOURCE_DIR}/python/")
