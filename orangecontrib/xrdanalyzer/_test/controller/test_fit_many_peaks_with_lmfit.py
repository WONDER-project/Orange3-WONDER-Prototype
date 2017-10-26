import matplotlib.pyplot as plt
import numpy
import lmfit

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

def get_parameters_method_lmfit(parameters):

    guess_parameters = lmfit.Parameters()

    # latticePar    -  position 0
    guess_parameters.add(name="lattice_parameter", value= parameters[0], vary=False)

    for index in range(Global.n_peaks):
        # Amplitude index+1    -  position index +1
        guess_parameters.add(name="I{}".format(index+1), value=parameters[1+index], min=1, max=100000.0)

    # sigma    -  position 2
    guess_parameters.add(name="sigma", value=parameters[Global.n_peaks +1], min=0.01, max=0.8)
    # mu    -  position 3
    guess_parameters.add(name="mu",value=parameters[Global.n_peaks + 2],  min=0.01, max=10)
    # a    -  position 4
    guess_parameters.add(name="a",value=parameters[Global.n_peaks + 3], min=0.0, max=0.1)
    # b    -  position 5
    guess_parameters.add(value=parameters[Global.n_peaks + 4],name="b", min=0.0, max=0.1)
    # A    -  position 6
    guess_parameters.add(value=parameters[Global.n_peaks + 5], name="A", min=0.0, max=1.0)
    # B    -  position 7
    guess_parameters.add(value=parameters[Global.n_peaks + 6], name="B", min=0.0, max=1.0)

    # U    -  position 8
    guess_parameters.add(value=parameters[Global.n_peaks + 7], name="U", min=0.0)
    # V    -  position 9
    guess_parameters.add(value=parameters[Global.n_peaks + 8], name="V")
    # W    -  position 10
    guess_parameters.add(value=parameters[Global.n_peaks + 9], name="W")
    # aa    -  position 11
    guess_parameters.add(value=parameters[Global.n_peaks + 10], name="aa",min=0.0, max=1.0)
    # bb    -  position 12
    guess_parameters.add(value=parameters[Global.n_peaks + 11], name="bb")
    # cc    -  position 13
    guess_parameters.add(value=parameters[Global.n_peaks + 12], name="cc", vary=False)
    # wavelength    -  position 14
    guess_parameters.add(value=parameters[Global.n_peaks + 13], vary = False, name="wavelength",min=-100, max=100)

    # bkg    -  position 15
    guess_parameters.add(value=parameters[Global.n_peaks + 14], name="bkg",min=200.0, max=1000.0)

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
parameters += [0.5, 4, 1e-4, 1e-6, 1.0, 1.0, 1e-4, 1e-4, 1e-5, 0.2, 1e-4, 0.0, wavelength, 400]
print (len(parameters))
guess_parameters = get_parameters_method_lmfit(parameters)


result = fitter_with_lmfit(functionNPeaks_lmfit,
                        s_exp,
                        intensity_exp,
                        guess_parameters)


from lmfit import minimize, Minimizer, Parameters, Parameter, report_fit

report_fit(result)
#print(result.fit_report())

plt.plot(s_exp, functionNPeaks_lmfit_plot(result.params, s_exp), 'b')
plt.plot(s_exp, result.residual - 1000, 'g')

plt.scatter(s_exp, intensity_exp, c='r', s=2)
plt.show()


