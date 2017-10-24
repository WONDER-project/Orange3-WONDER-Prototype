import numpy
import matplotlib.pyplot as plt

from orangecontrib.xrdanalyzer._test.controller.fitter import fitterScipyCurveFit

from orangecontrib.xrdanalyzer.controller.fit_parameter import FitParametersList, FitParameter, Boundary

# --------------------------------
# FUNCTIONS FOR THE TEST
# --------------------------------
def gaussianpeak_analytical(x, Amplitude, a ,xshift):

    return Amplitude*numpy.exp(-a*(x-xshift)**2)

def gaussianpeak_experimental (x, parameters):

    gaussianpeakfunction = numpy.zeros(numpy.size(x))

    for p in parameters:
        gaussianpeakfunction += numpy.exp(-x*x*p)

    return gaussianpeakfunction

s_experimental = numpy.sort(numpy.random.uniform(low=-1, high=1,
                                  size=100))

parameters_experimental = [3.5, 13, 15, 150]

intensity_experimental = gaussianpeak_experimental(s_experimental, parameters_experimental)

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






