import os
import json
import numpy as np
import firedrake
import icepack, icepack.models
from icepack.grid import arcinfo
from icepack.constants import (ice_density as ρ_I, water_density as ρ_W,
                               gravity as g, glen_flow_law as n)

def init(config_filename):
    path = os.path.dirname(os.path.abspath(config_filename))
    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    print('Config: {}'.format(config), flush=True)

    mesh = firedrake.Mesh(os.path.join(path, config['mesh']))

    Q = firedrake.FunctionSpace(mesh, 'CG', 1)
    V = firedrake.VectorFunctionSpace(mesh, 'CG', 1)

    thickness = arcinfo.read(os.path.join(path, config['thickness']))
    h = icepack.interpolate(thickness, Q)

    T = 254.15
    A = firedrake.interpolate(firedrake.Constant(icepack.rate_factor(T)), Q)

    velocity_x = arcinfo.read(os.path.join(path, config['velocity_x']))
    velocity_y = arcinfo.read(os.path.join(path, config['velocity_y']))
    u = icepack.interpolate((velocity_x, velocity_y), V)

    accumulation = arcinfo.read(os.path.join(path, config['accumulation']))
    melt = arcinfo.read(os.path.join(path, config['melt']))
    a = icepack.interpolate(accumulation, Q)
    m = icepack.interpolate(melt, Q)

    state = {
        'velocity': u,
        'inflow_thickness': h.copy(deepcopy=True),
        'thickness': h,
        'accumulation_rate': a,
        'melt_rate': m,
        'fluidity': A,
        'model': icepack.models.IceShelf(),
        'dirichlet_ids': config['dirichlet_ids'],
        'side_wall_ids': config['side_wall_ids']
    }

    print('Done initializing!')
    return state


def diagnostic_solve(state):
    h, u = state['thickness'], state['velocity']
    A = state['fluidity']

    opts = {
        'dirichlet_ids': state['dirichlet_ids'],
        'side_wall_ids': state['side_wall_ids'],
        'tol': 1e-12
    }

    model = state['model']
    u.assign(model.diagnostic_solve(u0=u, h=h, A=A, **opts))

    print('Diagnostic solve complete!')
    return state


def prognostic_solve(state, dt):
    h, h_inflow = state['thickness'], state['inflow_thickness']
    accumulation, melt = state['accumulation_rate'], state['melt_rate']
    a = accumulation - melt
    u = state['velocity']

    model = state['model']
    h.assign(model.prognostic_solve(dt, h0=h, h_inflow=h_inflow, u=u, a=a))

    print('Prognostic solve complete!')
    return state


def get_mesh_coordinates(fields):
    print('Accessing mesh coordinates!')
    return fields['velocity'].ufl_domain().coordinates.dat.data_ro


def get_velocity(fields):
    print('Accessing velocity data!')
    return fields['velocity'].dat.data_ro


def get_thickness(fields):
    print('Accessing thickness data!')
    return fields['thickness'].dat.data_ro


def get_accumulation_rate(fields):
    print ('Accessing accumulation rate data!')
    return fields['accumulation_rate'].dat.data_ro


def get_melt_rate(fields):
    print('Accessing melt rate data!')
    return fields['melt_rate'].dat.data_ro
