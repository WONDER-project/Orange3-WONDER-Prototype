import numpy as np
import orangecontrib.xrdanalyzer.util.congruence as congruence

#data logic methods

def loadxyz_numpy(xyzfilename):
   dt = np.dtype([('element', np.unicode_, 32), ('x', np.float32),
                  ('y', np.float32), ('z', np.float32)])

   element, x, y, z = np.loadtxt(xyzfilename, dtype=dt, unpack=True, skiprows=2)

   return element, x, y, z

def loadxyz_multiple_arrays(xyzfilename):
    with open(xyzfilename, 'r') as xyzfile:
        lines = xyzfile.readlines()
    N = int(lines[0])
    element = []
    x = np.zeros(N)
    y = np.zeros(N)
    z = np.zeros(N)
    for i in np.arange(2, N+2):
        line = lines[i].split()
        element.append(line[0])
        x[i-2] = float(line[1])
        y[i - 2] = float(line[2])
        z[i - 2] = float(line[3])
    return element, x, y, z




