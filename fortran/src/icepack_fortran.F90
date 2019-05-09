
#define check_error(ierror) if (ierror /= 0) then; call err_print; call exit(1); endif

module icepack_fortran

use :: forpy_mod
use :: iso_c_binding, only: c_char
use :: iso_fortran_env, only: real64

implicit none

public :: simulation

type :: simulation
    type(module_py) :: python_module
    type(object) :: state
contains
    procedure :: initialize => simulation_init
    procedure :: destroy => simulation_destroy
    procedure :: get_mesh_coordinates => simulation_get_mesh_coordinates
    procedure :: get_mesh_cells => simulation_get_mesh_cells
    procedure :: get_velocity => simulation_get_velocity
    procedure :: get_thickness => simulation_get_thickness
    procedure :: get_accumulation_rate => simulation_get_accumulation_rate
    procedure :: get_melt_rate => simulation_get_melt_rate
    procedure :: diagnostic_solve => simulation_diagnostic_solve
    procedure :: prognostic_solve => simulation_prognostic_solve
end type


contains


subroutine set_argv
    integer :: ierror
    type(module_py) :: sys
    type(list) :: empty_list

    check_error(import_py(sys, "sys"))
    check_error(list_create(empty_list))
    check_error(sys%setattr("argv", empty_list))

    call empty_list%destroy
    call sys%destroy
end subroutine


subroutine simulation_init(self, config_filename)
    ! Arguments
    class(simulation), intent(inout) :: self
    character(len=*, kind=c_char) :: config_filename

    ! Local variables
    type(str) :: config_filename_str
    type(tuple) :: args

    ! Initialize the Fortran <-> Python interface
    check_error(forpy_initialize())

    ! Set `sys.argv` to be empty so that firedrake won't seg fault when it goes
    ! looking for this attribute
    call set_argv

    ! Import the Python wrapper module
    check_error(import_py(self%python_module, "icepack_fortran"))

    ! Pass the pathname of the config file to Python, from which it will
    ! initialize the simulation state
    check_error(tuple_create(args, 1))
    check_error(str_create(config_filename_str, trim(config_filename)))
    check_error(args%setitem(0, config_filename_str))
    check_error(call_py(self%state, self%python_module, "init", args))

    call args%destroy
    call config_filename_str%destroy
end subroutine


subroutine simulation_destroy(self)
    class(simulation), intent(inout) :: self

    call self%state%destroy
    call self%python_module%destroy

    call forpy_finalize
end subroutine


subroutine get_scalar_field(self, field_name, field)
    ! Arguments
    class(simulation), intent(in) :: self
    character(len=*), intent(in) :: field_name
    real(kind=real64), dimension(:), pointer, intent(out) :: field

    ! Local variables
    type(tuple) :: args
    type(object) :: obj
    type(ndarray) :: array

    check_error(tuple_create(args, 1))
    check_error(args%setitem(0, self%state))
    check_error(call_py(obj, self%python_module, "get_" // field_name, args))
    check_error(cast(array, obj))
    check_error(array%get_data(field, 'C'))

    call args%destroy
    call obj%destroy
end subroutine


subroutine get_vector_field(self, field_name, field)
    ! Arguments
    class(simulation), intent(in) :: self
    character(len=*), intent(in) :: field_name
    real(kind=real64), dimension(:,:), pointer, intent(out) :: field

    ! Local variables
    type(tuple) :: args
    type(object) :: obj
    type(ndarray) :: array

    check_error(tuple_create(args, 1))
    check_error(args%setitem(0, self%state))
    check_error(call_py(obj, self%python_module, "get_" // field_name, args))
    check_error(cast(array, obj))
    check_error(array%get_data(field, 'C'))

    call args%destroy
    call obj%destroy
end subroutine


subroutine simulation_get_mesh_coordinates(self, coordinates)
    ! Arguments
    class(simulation), intent(in) :: self
    real(kind=real64), dimension(:,:), pointer, intent(out) :: coordinates

    call get_vector_field(self, "mesh_coordinates", coordinates)
end subroutine


subroutine simulation_get_mesh_cells(self, cells)
    ! Arguments
    class(simulation), intent(in) :: self
    integer, dimension(:,:), pointer, intent(out) :: cells

    ! Local variables
    type(tuple) :: args
    type(object) :: obj
    type(ndarray) :: array

    check_error(tuple_create(args, 1))
    check_error(args%setitem(0, self%state))
    check_error(call_py(obj, self%python_module, "get_mesh_cells", args))
    check_error(cast(array, obj))
    check_error(array%get_data(cells, 'C'))

    call args%destroy
    call obj%destroy
end subroutine


subroutine simulation_get_velocity(self, velocity)
    ! Arguments
    class(simulation), intent(in) :: self
    real(kind=real64), dimension(:,:), pointer, intent(out) :: velocity

    call get_vector_field(self, "velocity", velocity)
end subroutine


subroutine simulation_get_thickness(self, thickness)
    ! Arguments
    class(simulation), intent(in) :: self
    real(kind=real64), dimension(:), pointer, intent(out) :: thickness

    call get_scalar_field(self, "thickness", thickness)
end subroutine


subroutine simulation_get_accumulation_rate(self, accumulation_rate)
    ! Arguments
    class(simulation), intent(in) :: self
    real(kind=real64), dimension(:), pointer, intent(out) :: accumulation_rate

    call get_scalar_field(self, "accumulation_rate", accumulation_rate)
end subroutine


subroutine simulation_get_melt_rate(self, melt_rate)
    ! Arguments
    class(simulation), intent(in) :: self
    real(kind=real64), dimension(:), pointer, intent(out) :: melt_rate

    call get_scalar_field(self, "melt_rate", melt_rate)
end subroutine


subroutine simulation_diagnostic_solve(self)
    ! Arguments
    class(simulation), intent(inout) :: self

    ! Local variables
    type(tuple) :: args

    associate(state => self%state, python_module => self%python_module)
        check_error(tuple_create(args, 1))
        check_error(args%setitem(0, state))
        check_error(call_py(state, python_module, "diagnostic_solve", args))
    end associate

    call args%destroy
end subroutine


subroutine simulation_prognostic_solve(self, dt)
    ! Arguments
    class(simulation), intent(inout) :: self
    real(kind=real64), intent(in) :: dt

    ! Local variables
    type(tuple) :: args

    associate(state => self%state, python_module => self%python_module)
        check_error(tuple_create(args, 2))
        check_error(args%setitem(0, state))
        check_error(args%setitem(1, dt))
        check_error(call_py(state, python_module, "prognostic_solve", args))
    end associate

    call args%destroy
end subroutine


end module
