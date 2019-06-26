program wrapper_test

use :: icepack_fortran, only: simulation
use :: iso_c_binding, only: c_char
use :: iso_fortran_env, only: real64

implicit none
    real(kind=real64) :: dt

    ! Command-line arguments
    integer :: num_cmdline_args
    character(len=256, kind=c_char) :: cmdline_arg

    ! Simulation object and pointers to field data
    type(simulation) :: s
    integer, dimension(:,:), pointer :: cells
    real(kind=real64), dimension(:,:), pointer :: coordinates, velocity
    real(kind=real64), dimension(:), pointer :: thickness, surface, &
        friction, accumulation, melt

    num_cmdline_args = command_argument_count()
    if (num_cmdline_args /= 1) then
        write(*, *) "Missing command-line argument for path to config file."
        write(*, *) "Config file is at icepack-fortran/test/config.json"
        call exit(1)
    endif
    call get_command_argument(1, cmdline_arg)

    call s%initialize(cmdline_arg)

    call s%get_mesh_cells(cells)
    write(*, *) size(cells, 1), size(cells, 2)
    write(*, *) cells(1, 1), cells(2, 1), cells(3, 1)
    write(*, *) cells(1, 2), cells(2, 2), cells(3, 2)
    write(*, *) cells(1, 3), cells(2, 3), cells(3, 3)

    call s%get_mesh_coordinates(coordinates)
    write(*, *) size(coordinates, 1), size(coordinates, 2)
    write(*, *) coordinates(1, 1), coordinates(2, 1)

    call s%get_velocity(velocity)
    write(*, *) size(velocity, 1), size(velocity, 2)
    write(*, *) velocity(1, 1), velocity(2, 1)

    call s%get_thickness(thickness)
    write(*, *) size(thickness)
    write(*, *) thickness(1)

    call s%get_surface(surface)
    write(*, *) size(surface)
    write(*, *) surface(1)

    call s%get_friction(friction)
    write(*, *) size(friction)
    write(*, *) friction(1)

    call s%diagnostic_solve

    write(*, *) velocity(1, 1), velocity(2, 1)

    call s%get_accumulation_rate(accumulation)
    call s%get_melt_rate(melt)

    write(*, *) accumulation(1), melt(1)

    dt = 1.0/12
    call s%prognostic_solve(dt)

    call s%destroy

end program
