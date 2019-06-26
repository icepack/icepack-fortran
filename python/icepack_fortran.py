import os
import json
import numpy as np
import rasterio
import firedrake
import icepack, icepack.models
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

    thickness = rasterio.open(os.path.join(path, config['thickness']), 'r')
    h = icepack.interpolate(thickness, Q)

    bed = rasterio.open(os.path.join(path, config['bed']), 'r')
    b = icepack.interpolate(bed, Q)

    model = icepack.models.IceStream()
    s = model.compute_surface(h=h, b=b)

    T = 254.15
    A = firedrake.interpolate(firedrake.Constant(icepack.rate_factor(T)), Q)
    C = firedrake.interpolate(firedrake.Constant(0), Q)

    velocity_x = rasterio.open(os.path.join(path, config['velocity_x']), 'r')
    velocity_y = rasterio.open(os.path.join(path, config['velocity_y']), 'r')
    u = icepack.interpolate((velocity_x, velocity_y), V)

    accumulation = rasterio.open(os.path.join(path, config['accumulation']), 'r')
    melt = rasterio.open(os.path.join(path, config['melt']), 'r')
    a = icepack.interpolate(accumulation, Q)
    m = icepack.interpolate(melt, Q)

    state = {
        'velocity': u,
        'inflow_thickness': h.copy(deepcopy=True),
        'thickness': h,
        'surface': s,
        'bed': b,
        'accumulation_rate': a,
        'melt_rate': m,
        'fluidity': A,
        'friction': C,
        'model': model,
        'dirichlet_ids': config['dirichlet_ids'],
        'side_wall_ids': config['side_wall_ids']
    }

    print('Done initializing!')
    return state


def diagnostic_solve(state):
    h = state['thickness']
    s = state['surface']
    b = state['bed']
    u = state['velocity']
    A = state['fluidity']
    C = state['friction']

    opts = {
        'dirichlet_ids': state['dirichlet_ids'],
        'side_wall_ids': state['side_wall_ids'],
        'tol': 1e-12
    }

    model = state['model']
    u.assign(model.diagnostic_solve(u0=u, h=h, s=s, A=A, C=C, **opts))

    print('Diagnostic solve complete!')
    return state


def prognostic_solve(state, dt):
    h, h_inflow = state['thickness'], state['inflow_thickness']
    accumulation, melt = state['accumulation_rate'], state['melt_rate']
    a = accumulation - melt
    u = state['velocity']

    model = state['model']
    h.assign(model.prognostic_solve(dt, h0=h, h_inflow=h_inflow, u=u, a=a))

    b = state['bed']
    s = state['surface']
    s.assign(model.compute_surface(h=h, b=b))

    print('Prognostic solve complete!')
    return state


def get_mesh_coordinates(state):
    print('Accessing mesh coordinates!')
    return state['velocity'].ufl_domain().coordinates.dat.data_ro


def get_mesh_cells(state):
    print('Accessing mesh cells!')
    return state['velocity'].ufl_domain().coordinates.cell_node_map().values


def get_velocity(state):
    print('Accessing velocity data!')
    return state['velocity'].dat.data_ro


def get_thickness(state):
    print('Accessing thickness data!')
    return state['thickness'].dat.data_ro


def get_surface(state):
    print('Accessing surface data!')
    return state['surface'].dat.data_ro


def get_friction(state):
    print('Accessing friction data!')
    return state['friction'].dat.data_ro


def get_accumulation_rate(state):
    print ('Accessing accumulation rate data!')
    return state['accumulation_rate'].dat.data_ro


def get_melt_rate(state):
    print('Accessing melt rate data!')
    return state['melt_rate'].dat.data_ro
