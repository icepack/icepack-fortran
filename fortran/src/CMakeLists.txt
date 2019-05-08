add_library(icepack_fortran forpy/forpy_mod.F90 icepack_fortran.F90)
target_link_libraries(icepack_fortran ${PYTHON_LIBRARIES})
install(TARGETS icepack_fortran
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib
	INCLUDES DESTINATION include)
