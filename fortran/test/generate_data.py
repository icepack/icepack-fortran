import os
import sys
import json
import numpy as np
import rasterio
import icepack
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

    transform = rasterio.transform.from_origin(-dx, (m + 1) * dx, dx, dx)

    for name in fields:
        field = data[name]
        filename = os.path.join(directory, name + '.tif')
        with rasterio.open(filename, 'w', driver='GTiff',
                height=m + 3, width=m + 3, count=1, dtype=field.dtype,
                transform=transform) as dataset:
            dataset.write(np.flipud(data[name]), indexes=1)

    config = {'mesh': 'mesh.msh', 'dirichlet_ids': [4], 'side_wall_ids': [1, 3],
              'thickness': 'h.tif', 'accumulation': 'a.tif', 'melt': 'm.tif',
              'velocity_x': 'u.tif', 'velocity_y': 'v.tif'}
    with open(os.path.join(directory, 'config.json'), 'w') as config_file:
        config_file.write(json.dumps(config, indent=4))

if __name__ == "__main__":
    main(sys.argv[1])
