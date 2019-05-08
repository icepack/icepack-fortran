import os
import sys
import json
import numpy as np
import icepack
import icepack.grid, icepack.grid.arcinfo
from icepack.constants import (ice_density as ρ_I, water_density as ρ_W,
                               gravity as g, glen_flow_law as n)

def main(directory):
    fields = ['u', 'v', 'h', 'a', 'm']

    L = 20e3
    m = 128
    dx = L / m

    origin = (-dx, -dx)
    data = {name: np.zeros((m + 3, m + 3), dtype=np.float32) for name in fields}

    u0 = 100.0
    h0, dh = 500.0, 100.0
    T = 254.15

    def u(x, y):
        ρ = ρ_I * (1 - ρ_I / ρ_W)
        Z = icepack.rate_factor(T) * (ρ * g * h0 / 4)**n
        q = 1 - (1 - (dh/h0) * (x/L))**(n + 1)
        du = Z * q * L * (h0/dh) / (n + 1)
        return u0 + du

    for i in range(m + 3):
        y = origin[1] + i * dx
        for j in range(m + 3):
            x = origin[0] + j * dx
            data['u'][i, j] = u(x, y)
            data['v'][i, j] = 0.0
            data['h'][i, j] = h0 - dh * x / L
            # TODO: Put in sensible values
            data['a'][i, j] = 0.0
            data['m'][i, j] = 0.0

    for name in fields:
        field = icepack.grid.GridData(origin, dx, data[name],
                                      missing_data_value=-2e9)
        filename = os.path.join(directory, name + '.txt')
        icepack.grid.arcinfo.write(filename, field, -2e9)

    config = {'mesh': 'mesh.msh', 'dirichlet_ids': [4], 'side_wall_ids': [1, 3],
              'thickness': 'h.txt', 'accumulation': 'a.txt', 'melt': 'm.txt',
              'velocity_x': 'u.txt', 'velocity_y': 'v.txt'}
    with open(os.path.join(directory, 'config.json'), 'w') as config_file:
        config_file.write(json.dumps(config, indent=4))

if __name__ == "__main__":
    main(sys.argv[1])
