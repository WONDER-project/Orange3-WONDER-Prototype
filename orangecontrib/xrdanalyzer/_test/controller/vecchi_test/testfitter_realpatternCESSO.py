import matplotlib.pyplot as plt
import numpy

from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import isolate_peak
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPatternFactory

#filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/xyzFileTests.xyz2"
filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"

wavelength = 0.0826 # nm
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
                                                          0, 9.5)
#
#plt.plot(s_experimental, intensity_experimental)
#plt.show()




guess_parameters = FitParametersList()

#latticePar    -  position 0
guess_parameters.add_parameter(FitParameter(value = 2.873e-1, fixed=True, boundary=Boundary(min_value=-100, max_value=1000.0)))


#Amplitude 1    -  position 1
guess_parameters.add_parameter(FitParameter(value = 150, parameter_name="I1", boundary=Boundary(min_value=-100, max_value=100000.0)))
#Amplitude 2    -  position 2
guess_parameters.add_parameter(FitParameter(value = 20, parameter_name="I2", boundary=Boundary(min_value=-100, max_value=100000.0)))
#Amplitude 3    -  position 3
guess_parameters.add_parameter(FitParameter(value = 40, parameter_name="I3", boundary=Boundary(min_value=-100, max_value=100000.0)))

#sigma    -  position 4
guess_parameters.add_parameter(FitParameter(value = 0.35, parameter_name="sigma", boundary=Boundary(min_value=-100, max_value=1000.0)))
#mu    -  position 5
guess_parameters.add_parameter(FitParameter(value = 2.2, parameter_name="mu", boundary=Boundary(min_value=-100, max_value=1000.0)))
#a    -  position 6
guess_parameters.add_parameter(FitParameter(value = 0.005, boundary=Boundary(min_value=-100, max_value=1000.0)))
#b    -  position 7
guess_parameters.add_parameter(FitParameter(value = 0.005, boundary=Boundary(min_value=-100, max_value=1000.0)))
#A    -  position 8
guess_parameters.add_parameter(FitParameter(value = 0.00001, boundary=Boundary(min_value=-100, max_value=1000.0)))
#B    -  position 8
guess_parameters.add_parameter(FitParameter(value = 0.00001, boundary=Boundary(min_value=-100, max_value=1000.0)))

#offset    -  position 10
guess_parameters.add_parameter(FitParameter(value = 0.0, parameter_name="A0", boundary=Boundary(min_value=-100, max_value=1000.0)))



parameters, boundaries = guess_parameters.to_scipy_tuple()



# PLOT ONLY 1 Peak with PM2K parameters.

temporayparams =  [2.873e-1, 150, 0.353, 2.1711, 0., 0., 0., 0.]

from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import createonepeak

sfake, ifake = createonepeak(temporayparams, 2,1,1 )

plt.plot(sfake, ifake)

plt.show()





'''
s = numpy.linspace(0., Global.Smax, Global.n_steps)

y = functionOfManyPeaks(s, *parameters)
#plt.xlim(0,1.5)
plt.plot(s,y)
plt.scatter(s_experimental, intensity_experimental/100, c='r', s=2)
plt.show()

'''
'''

fitparameters, covariance = fitterScipyCurveFit(functionOfManyPeaks,
                                    s_experimental,
                                    intensity_experimental,
                                    guess_parameters)


intensity_analytical = functionOfManyPeaks(s_experimental, *fitparameters)

plt.plot(s_experimental, intensity_analytical)
plt.scatter(s_experimental, intensity_experimental, c='r')
plt.show()

print("Valori fittati", fitparameters)

'''
'''
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