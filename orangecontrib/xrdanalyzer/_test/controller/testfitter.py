import matplotlib.pyplot as plt
import numpy
from orangecontrib.xrdanalyzer.controller.fit_parameter import FitParametersList, FitParameter, Boundary

from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import fitterScipyCurveFit, \
    gaussianpeak_experimental
from orangecontrib.xrdanalyzer._test.controller.vecchi_test.fitterCESSO import functionOfThePeak

s_experimental = numpy.sort(numpy.random.uniform(low=-5, high=5,
                                  size=500))

parameters_experimental = [3.5, 13, 5, 2]

intensity_experimental = gaussianpeak_experimental(s_experimental, parameters_experimental)
'''
guess_parameters = FitParametersList()
guess_parameters.add_parameter(FitParameter(value=3.0, boundary=Boundary(min_value=0.0, max_value=100.0)))
guess_parameters.add_parameter(FitParameter(value=10.0, boundary=Boundary(min_value=0.0, max_value=10.0)))
guess_parameters.add_parameter(FitParameter(value=0.5, boundary=Boundary(min_value=-5.0, max_value=5.0)))

fitparameters = fitterScipyCurveFit(gaussianpeak_analytical,
                                    s_experimental,
                                    intensity_experimental,
                                    guess_parameters)[0]


print(fitparameters)

intensity_analytical = gaussianpeak_analytical(s_experimental, *fitparameters)
plt.plot(s_experimental, intensity_analytical)
plt.scatter(s_experimental, intensity_experimental, c='r')
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

for i in range(0, 5):
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

    print("SS", s_sq)
    print("Errors", error)

    for j in range (0, len(fitparameters)):
        guess_parameters.fit_parameters_list[j].value = fitparameters[j]