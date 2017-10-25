import matplotlib.pyplot as plt
import numpy

from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import isolate_peak
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPatternFactory
from orangecontrib.xrdanalyzer._test.controller.fitter import *

def load_and_crop_pattern(filename, wavelength, smin, smax):


    diffraction_pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file(filename, wavelength)
    diffraction_pattern.set_wavelength(wavelength)

    s_experimental = []
    intensity_experimental= []
    for index in range(0, diffraction_pattern.diffraction_points_count()):
        s_experimental.append(diffraction_pattern.get_diffraction_point(index).s)
        intensity_experimental.append(diffraction_pattern.get_diffraction_point(index).intensity)

    s_experimental = numpy.array(s_experimental)
    intensity_experimental = numpy.array(intensity_experimental)

    s_experimental, intensity_experimental = isolate_peak(s_experimental,
                                                              intensity_experimental,
                                                              smin, smax)

    return s_experimental, intensity_experimental

#filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.xyz2"
filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"
wavelength = 0.0826# nm

s_exp, intensity_exp = load_and_crop_pattern(filename, wavelength, 0., 6)

plt.plot(s_exp, intensity_exp)
plt.show()

#           latticepar Amplitude  sigma   mu          others
parameters = [2.873e-1, 15000, 0.353, 2.1711, 0., 0., 0., 0.]
parameters = [2.873e-1, 15000, 0.5, 2, 0., 0., 0., 0.]

h, k, l = 1, 1, 0

s_an, intensity_an = createonepeak(parameters, h, k, l)

plt.plot(s_an, intensity_an)
plt.show()
