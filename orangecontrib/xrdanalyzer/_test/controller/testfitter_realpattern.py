import numpy
import matplotlib.pyplot as plt

from orangecontrib.xrdanalyzer._test.controller.fitter import fitterScipyCurveFit, gaussianpeak_analytical, gaussianpeak_experimental

from orangecontrib.xrdanalyzer.controller.fit_parameter import FitParametersList, FitParameter, Boundary
from orangecontrib.xrdanalyzer._test.controller.fitter import Global, functionOfThePeak, isolate_peak, first3
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPatternFactory


#filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.xyz2"
filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"

wavelength = 0.826 # Angstrom
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
                                                          0,0.9)

plt.plot(s_experimental, intensity_experimental)


default_lattice_parameter = 2.873

distances = first3(default_lattice_parameter, "bcc")
for a in distances:
    print (a)


plt.show()



'''
guess_parameters = FitParametersList()
guess_parameters.add_parameter(FitParameter(value=1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value=1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))

guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))
guess_parameters.add_parameter(FitParameter(value = 1, boundary=Boundary(min_value=-100, max_value=1000.0)))


fitparameters, covariance = fitterScipyCurveFit(functionOfThePeak,
                                    s_experimental,
                                    intensity_experimental,
                                    guess_parameters)

intensity_analytical = functionOfThePeak(s_experimental, *fitparameters)
plt.plot(s_experimental, intensity_analytical)
plt.scatter(s_experimental, intensity_experimental, c='r')
plt.show()

print("Valori fittati", fitparameters)

n_fit_parameters = len(guess_parameters.fit_parameters_list)
n_data = len(intensity_experimental)

errfunc = lambda p, x, y: functionOfThePeak(x, *p) - y

if (n_data > n_fit_parameters) and covariance is not None:
    s_sq = (errfunc(fitparameters, s_experimental, intensity_experimental)**2).sum()/(n_data-n_fit_parameters)
    covariance = covariance * s_sq
else:
    covariance = numpy.inf

error = []
for i in range(n_fit_parameters):
    try:
      error.append(numpy.absolute(covariance[i][i])**0.5)
    except:
      error.append( 0.00 )

#print("SS", s_sq)
print("Errors", error)

for j in range (0, len(fitparameters)):
    guess_parameters.fit_parameters_list[j].value = fitparameters[j]

'''