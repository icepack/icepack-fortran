import sys
import numpy as np
import icepack
import icepack.grid, icepack.grid.arcinfo
from icepack.constants import (rho_ice as ρ_I, rho_water as ρ_W,
                               gravity as g, glen_flow_law as n)

def main(u_filename, v_filename, h_filename, a_filename, m_filename):
    L = 20e3
    m = 128
    dx = L / m

    origin = (-dx, -dx)
    u_data = np.zeros((m + 3, m + 3), dtype=np.float32)
    v_data = np.zeros((m + 3, m + 3), dtype=np.float32)
    h_data = np.zeros((m + 3, m + 3), dtype=np.float32)
    a_data = np.zeros((m + 3, m + 3), dtype=np.float32)
    m_data = np.zeros((m + 3, m + 3), dtype=np.float32)

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
            u_data[i, j] = u(x, y)
            v_data[i, j] = 0.0
            h_data[i, j] = h0 - dh * x / L
            # TODO: Put in sensible values
            a_data[i, j] = 0.0
            m_data[i, j] = 0.0

    u = icepack.grid.GridData(origin, dx, u_data, missing_data_value=-2e9)
    v = icepack.grid.GridData(origin, dx, v_data, missing_data_value=-2e9)
    h = icepack.grid.GridData(origin, dx, h_data, missing_data_value=-2e9)
    a = icepack.grid.GridData(origin, dx, a_data, missing_data_value=-2e9)
    m = icepack.grid.GridData(origin, dx, m_data, missing_data_value=-2e9)

    icepack.grid.arcinfo.write(u_filename, u, -2e9)
    icepack.grid.arcinfo.write(v_filename, v, -2e9)
    icepack.grid.arcinfo.write(h_filename, h, -2e9)
    icepack.grid.arcinfo.write(a_filename, a, -2e9)
    icepack.grid.arcinfo.write(m_filename, m, -2e9)

if __name__ == "__main__":
    main(*sys.argv[1:])
