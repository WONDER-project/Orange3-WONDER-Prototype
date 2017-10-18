import numpy as np
import orangecontrib.xrdanalyzer.util.gui.congruence as congruence


def loadxyz(xyzfilename):
   congruence.checkFile(xyzfilename)
   dt = np.dtype([('element', np.unicode_, 32), ('x', np.float32),
                  ('y', np.float32), ('z', np.float32)])
   element, x, y, z = np.loadtxt(xyzfilename, dtype=dt, unpack=True, skiprows=2)
   return element, x, y, z

