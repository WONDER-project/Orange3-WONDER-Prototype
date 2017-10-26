import matplotlib.pyplot as plt
import numpy

from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import isolate_peak
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPatternFactory
from orangecontrib.xrdanalyzer._test.controller.fftparameters import *
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

    for index in range(Global.n_peaks):
        # Amplitude index+1    -  position index +1
        guess_parameters.add_parameter(
            FitParameter(value=parameters[1+index], parameter_name="I{}".format(index+1), boundary=Boundary(min_value=0.0, max_value=100000.0)))

    # sigma    -  position 2
    guess_parameters.add_parameter(
        FitParameter(value=parameters[Global.n_peaks + 1], parameter_name="sigma", boundary=Boundary(min_value=0.01, max_value=0.8)))
    # mu    -  position 3
    guess_parameters.add_parameter(
        FitParameter(value=parameters[Global.n_peaks + 2], parameter_name="mu", boundary=Boundary(min_value=0.01, max_value=10)))
    # a    -  position 4
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 3],parameter_name="a", boundary=Boundary(min_value=0.0, max_value=0.1)))
    # b    -  position 5
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 4],parameter_name="b", boundary=Boundary(min_value=0.0, max_value=0.1)))
    # A    -  position 6
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 5], parameter_name="A", boundary=Boundary(min_value=0.0, max_value=1.0)))
    # B    -  position 7
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 6], parameter_name="B", boundary=Boundary(min_value=0.0, max_value=1.0)))

    # U    -  position 8
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 7], parameter_name="U",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # V    -  position 9
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 8], parameter_name="V",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # W    -  position 10
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 9], parameter_name="W",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # aa    -  position 11
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 10], parameter_name="aa",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # bb    -  position 12
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 11], parameter_name="bb",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # cc    -  position 13
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 12], parameter_name="cc",
                                                boundary=Boundary(min_value=0, max_value=10)))
    # wavelength    -  position 14
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 13], fixed=True, parameter_name="wavelength",
                                                boundary=Boundary(min_value=-100, max_value=100)))

    # bkg    -  position 15
    guess_parameters.add_parameter(FitParameter(value=parameters[Global.n_peaks + 14], parameter_name="bkg",boundary=Boundary(min_value=200.0, max_value=1000.0)))

    return guess_parameters


#filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.xyz2"
filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"
wavelength = 0.0826# nm

s_exp, intensity_exp = load_and_crop_pattern(filename, wavelength, 0., 11.5)


Ihkl = [1000] * Global.n_peaks
parameters = []
parameters.append(2.873e-1) #lattice param
print("n peaks", Global.n_peaks)
for index in range(Global.n_peaks):
    parameters.append(Ihkl[index])
parameters += [0.353, 2.1711, 1e-4, 1e-6, 0.0, 0.0, 1e-4,1e-4,1e-4,1e-4,1e-4,1e-4,wavelength, 400]
print (len(parameters))
guess_parameters = get_parameters_method(parameters)

fitparameters, covariance = fitterScipyCurveFit(functionNPeaks,
                                    s_exp,
                                    intensity_exp,
                                    guess_parameters)

intensity_an = functionNPeaks(s_exp, *fitparameters)

plt.plot(s_exp, intensity_an)
plt.scatter(s_exp, intensity_exp, c='r', s=2)
plt.show()

print("Valori fittati", fitparameters)

