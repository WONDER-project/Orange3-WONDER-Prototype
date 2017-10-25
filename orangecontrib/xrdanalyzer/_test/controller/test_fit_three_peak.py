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

def get_parameters_method(parameters):
    guess_parameters = FitParametersList()

    # latticePar    -  position 0
    guess_parameters.add_parameter(
        FitParameter(value=parameters[0], fixed=True, boundary=Boundary(min_value=-100, max_value=1000.0)))

    # Amplitude 1    -  position 1
    guess_parameters.add_parameter(
        FitParameter(value=parameters[1], parameter_name="I1", boundary=Boundary(min_value=0.0, max_value=100000.0)))
    # Amplitude 2    -  position 2
    guess_parameters.add_parameter(
        FitParameter(value=parameters[2], parameter_name="I2", boundary=Boundary(min_value=0.0, max_value=100000.0)))
    # Amplitude 3    -  position 3
    guess_parameters.add_parameter(
        FitParameter(value=parameters[3], parameter_name="I3", boundary=Boundary(min_value=0.0, max_value=100000.0)))

     # sigma    -  position 2
    guess_parameters.add_parameter(
        FitParameter(value=parameters[4], parameter_name="sigma", boundary=Boundary(min_value=0.01, max_value=0.8)))
    # mu    -  position 3
    guess_parameters.add_parameter(
        FitParameter(value=parameters[5], parameter_name="mu", boundary=Boundary(min_value=0.01, max_value=10)))
    # a    -  position 4
    guess_parameters.add_parameter(FitParameter(value=parameters[6], boundary=Boundary(min_value=0.0, max_value=0.1)))
    # b    -  position 5
    guess_parameters.add_parameter(FitParameter(value=parameters[7], boundary=Boundary(min_value=0.0, max_value=0.1)))
    # A    -  position 6
    guess_parameters.add_parameter(FitParameter(value=parameters[8], boundary=Boundary(min_value=0.0, max_value=1.0)))
    # B    -  position 7
    guess_parameters.add_parameter(FitParameter(value=parameters[9], boundary=Boundary(min_value=0.0, max_value=1.0)))

    # bkg    -  position 8
    guess_parameters.add_parameter(FitParameter(value=parameters[10], boundary=Boundary(min_value=200.0, max_value=400.0)))

    return guess_parameters

#filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.xyz2"
filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"
wavelength = 0.0826# nm

s_exp, intensity_exp = load_and_crop_pattern(filename, wavelength, 0., 9)

#plt.plot(s_exp, intensity_exp)
#plt.show()

#           latticepar Amplitude  sigma   mu          others
parameters = [2.873e-1, 15000, 2000, 4000, 0.353, 2.1711, 1e-4, 1e-6, 0.0, 0.0, 300]

guess_parameters = get_parameters_method(parameters)

fitparameters, covariance = fitterScipyCurveFit(functionOfManyPeaks,
                                    s_exp,
                                    intensity_exp,
                                    guess_parameters)

intensity_an = functionOfManyPeaks(s_exp, *fitparameters)

plt.plot(s_exp, intensity_an)
plt.scatter(s_exp, intensity_exp, c='r', s=2)
plt.show()

print("Valori fittati", fitparameters)