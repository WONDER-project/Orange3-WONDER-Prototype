import numpy
import matplotlib.pyplot as plt

from orangecontrib.xrdanalyzer._test.controller.fitter import fitterScipyCurveFit

# --------------------------------
# FUNCTIONS FOR THE TEST
# --------------------------------
def gaussianpeak_analytical(x, Amplitude, a ,xshift):

    return Amplitude*numpy.exp((x-xshift)*(x-xshift)*a)

def gaussianpeak_experimental (x, parameters):

    gaussianpeakfunction = numpy.zeros(numpy.size(x))

    for p in parameters:
        gaussianpeakfunction += numpy.exp(-x*x*p)

    return gaussianpeakfunction

s_experimental = numpy.sort(numpy.random.uniform(low=-1, high=1,
                                  size=100))

parameters_experimental = [3.5, 13, 15, 150]
intensity_experimental = gaussianpeak_experimental(s_experimental, parameters_experimental)

guess_parameters = [1., 10, 0.5]

fitparameters = fitterScipyCurveFit(gaussianpeak_analytical,
                                    s_experimental,
                                    intensity_experimental,
                                    guess_parameters)[0]


intensity_analytical = gaussianpeak_analytical(s_experimental, *fitparameters)
plt.plot(s_experimental, intensity_analytical)
plt.scatter(s_experimental, intensity_experimental, c='r')
plt.show()






