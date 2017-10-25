

class FitterInterface:

    def do_fit(self, fit_global_parameters=None):
        FitterListener.register_fit_global_parameters(fit_global_parameters)

        self.do_specific_fit(fit_global_parameters)


    def do_specific_fit(self, fit_global_parameters):
        raise NotImplementedError("Abstract")


class FitterFactory():

    @classmethod
    def create_fitter(cls):
        return FitterPrototype()


import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc

from orangecontrib.xrdanalyzer.controller.fit.fitter_listener import FitterListener
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint

class FitterPrototype(FitterInterface):

    def do_specific_fit(self, fit_global_parameters):
        parameters, boundaries = fit_global_parameters.to_scipy_tuple()
        twotheta_experimental, intensity_experimental, error_experimental,  s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        fitted_parameters, covariance = self.fitterScipyCurveFit(s_experimental, intensity_experimental, parameters, boundaries)

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = fit_function(s_experimental, fitted_parameters)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=s_experimental[index]))

        return fitted_pattern

    def fitterScipyCurveFit(self,
                            s_experimental,
                            intensity_experimental,
                            parameters,
                            boundaries):
        return curve_fit(f=fit_function,
                         xdata=s_experimental,
                         ydata=intensity_experimental,
                         #sigma=numpy.sqrt(intensity_experimental),
                         p0=parameters,
                         bounds=boundaries)



def fit_function(s, *params):
    fit_global_paramter = FitterListener.Instance().get_registered_fit_global_parameters()

    return []




# FUNCTIONS
def sizeFunctionCommonvolume (L, D):
    LfracD = L/D
    return 1 - 1.5*LfracD + 0.5*LfracD**3


def sizeFunctionLognormal(L, sigma, mu):
    #L is supposed always positive
    #L = 10*L

    L = numpy.abs(L)
    lnL = numpy.log(L)
    sqrt2 = numpy.sqrt(2)
    a = 0.5*erfc((lnL - mu -3*sigma**2)/(sigma*sqrt2))
    b = -0.75*L*erfc((lnL - mu -2*sigma**2)/(sigma*sqrt2))\
                *numpy.exp(-mu - 2.5*sigma**2)
    c = 0.25*(L**3)*erfc((lnL - mu)/(sigma*sqrt2)) \
                *numpy.exp(-3*mu - 4.5*sigma**2)

    return  a + b + c

def strainFunction (L, h, k, l, latticepar ,a ,b, A, B):

    shkl = utilities.s_hkl(latticepar, h, k, l)
    H = utilities.Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -2*((numpy.pi*shkl)**2)*C*(a*L + b*L*L)

    return numpy.exp(exponent)
