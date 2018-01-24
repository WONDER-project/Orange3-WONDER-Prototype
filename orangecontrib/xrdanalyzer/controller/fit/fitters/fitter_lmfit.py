
import numpy
import lmfit

from orangecontrib.xrdanalyzer import Singleton, synchronized_method

from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Simmetry, Reflection
from orangecontrib.xrdanalyzer.util.general_functions import fft

from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface, FitterListener
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import create_one_peak

class LmfitFittingMethods:
    LEAST_SQUARES = "least_squares"
    LEVENBERG_MARQUARDT = "leastsq"

    
    '''
    'differential_evolution’: differential evolution
    'brute’: brute force method
    'nelder': Nelder-Mead
    'lbfgsb’: L-BFGS-B
    'powell’: Powell
    'cg’: Conjugate-Gradient
    'newton’: Newton-Congugate-Gradient
    'cobyla’: Cobyla
    'tnc’: Truncate Newton
    'trust-ncg’: Trust Newton-Congugate-Gradient
    'dogleg’: Dogleg
    'slsqp’: Sequential Linear Squares Programming
    '''

    @classmethod
    def tuple(cls):
        return [cls.LEVENBERG_MARQUARDT, cls.LEAST_SQUARES]


class FitterLmfit(FitterInterface):

    def __init__(self, fitting_method=LmfitFittingMethods.LEVENBERG_MARQUARDT):
        super(FitterLmfit, self).__init__()

        self.fitting_method = fitting_method

    def do_fit(self, fit_global_parameters, current_iteration):
        parameters = self.build_lmfit_parameters(fit_global_parameters)

        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        current_parameters = parameters
        current_residual = None
        current_covariance = None

        try:
            result = self.call_lmfit_minimizer(s_experimental, intensity_experimental, current_parameters)

            current_parameters = result.params
            current_residual = result.residual
            current_covariance = None #result.covariance????

        except ValueError as err:
            #TODO: eventuale gestione di errori particolari
            raise err


        fitted_parameters = current_parameters
        fitted_residual = current_residual
        fitted_covariance = current_covariance

        fit_global_parameters_out = self.build_fit_global_parameters_out(fitted_parameters)

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = get_fitted_intensity(fitted_parameters, s_experimental)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=s_experimental[index]))

        return fitted_pattern, fit_global_parameters_out


    def build_lmfit_parameters(self, fit_global_parameters):
        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        lmfit__parameters = lmfit.Parameters()

        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.a, "cp_a")
        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.b, "cp_b")
        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.c, "cp_c")
        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.alpha, "alpha")
        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.beta, "beta")
        self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.gamma, "gamma")

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            self._add_lm_fit_parameter(lmfit__parameters, crystal_structure.get_reflection(reflection_index).intensity, "I{}".format(reflection_index + 1))

        if not fit_global_parameters.background_parameters is None:
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c0, "c0")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c1, "c1")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c2, "c2")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c3, "c3")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c4, "c4")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.background_parameters.c5, "c5")

        if not fit_global_parameters.instrumental_parameters is None:
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.U, "U")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.V, "V")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.W, "W")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.a, "a")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.b, "b")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.instrumental_parameters.c, "c")

        if not fit_global_parameters.size_parameters is None:
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.size_parameters.mu, "mu")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.size_parameters.sigma, "sigma")

        if not fit_global_parameters.strain_parameters is None:
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.strain_parameters.aa, "aa")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.strain_parameters.bb, "bb")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.strain_parameters.e1, "e1")
            self._add_lm_fit_parameter(lmfit__parameters, fit_global_parameters.strain_parameters.e6, "e6")

        return lmfit__parameters

    @classmethod
    def _add_lm_fit_parameter(cls, lmfit__parameters, fit_parameter, fit_parameter_name):
        if fit_parameter.fixed:
            lmfit__parameters.add(name=fit_parameter_name, value=fit_parameter.value,
                                  vary=False)
        else:
            lmfit__parameters.add(name=fit_parameter_name, value=fit_parameter.value,
                                  min=fit_parameter.boundary.min_value,
                                  max=fit_parameter.boundary.max_value)
        



    def build_fit_global_parameters_out(self, fitted_parameters):
        fit_global_parameters = FitterListener.Instance().get_registered_fit_global_parameters().duplicate()
        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        crystal_structure.a.value = fitted_parameters["cp_a"].value
        crystal_structure.b.value = fitted_parameters["cp_b"].value
        crystal_structure.c.value = fitted_parameters["cp_c"].value
        crystal_structure.alpha.value = fitted_parameters["alpha"].value
        crystal_structure.beta.value = fitted_parameters["beta"].value
        crystal_structure.gamma.value = fitted_parameters["gamma"].value

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            crystal_structure.get_reflection(reflection_index).intensity.value = fitted_parameters["I{}".format(reflection_index + 1)].value

        if not fit_global_parameters.background_parameters is None:
            fit_global_parameters.background_parameters.c0.value = fitted_parameters["c0"].value
            fit_global_parameters.background_parameters.c1.value = fitted_parameters["c1"].value
            fit_global_parameters.background_parameters.c2.value = fitted_parameters["c2"].value
            fit_global_parameters.background_parameters.c3.value = fitted_parameters["c3"].value
            fit_global_parameters.background_parameters.c4.value = fitted_parameters["c4"].value
            fit_global_parameters.background_parameters.c5.value = fitted_parameters["c5"].value

        if not fit_global_parameters.instrumental_parameters is None:
            fit_global_parameters.instrumental_parameters.U.value = fitted_parameters["U"].value
            fit_global_parameters.instrumental_parameters.V.value = fitted_parameters["V"].value
            fit_global_parameters.instrumental_parameters.W.value = fitted_parameters["W"].value
            fit_global_parameters.instrumental_parameters.a.value = fitted_parameters["a"].value
            fit_global_parameters.instrumental_parameters.b.value = fitted_parameters["b"].value
            fit_global_parameters.instrumental_parameters.c.value = fitted_parameters["c"].value

        if not fit_global_parameters.size_parameters is None:
            fit_global_parameters.size_parameters.mu.value    = fitted_parameters["mu"].value
            fit_global_parameters.size_parameters.sigma.value = fitted_parameters["sigma"].value

        if not fit_global_parameters.strain_parameters is None:
            fit_global_parameters.strain_parameters.aa.value = fitted_parameters["aa"].value
            fit_global_parameters.strain_parameters.bb.value = fitted_parameters["bb"].value
            fit_global_parameters.strain_parameters.e1.value = fitted_parameters["e1"].value # in realtà è E1 dell'invariante PAH
            fit_global_parameters.strain_parameters.e6.value = fitted_parameters["e6"].value # in realtà è E6 dell'invariante PAH

        return fit_global_parameters


    def call_lmfit_minimizer(self, s_experimental, intensity_experimental, parameters):
        return lmfit.Minimizer(fit_function,
                               nan_policy='omit',
                               params=parameters,
                               fcn_args=(s_experimental, intensity_experimental)).minimize(method=self.fitting_method)


class CommonFittingData():

    def __init__(self, parameters):
        fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()

        self.lattice_parameter = parameters["cp_a"].value

        if not fit_global_parameter.background_parameters is None:
            self.c0 = parameters["c0"].value
            self.c1 = parameters["c1"].value
            self.c2 = parameters["c2"].value
            self.c3 = parameters["c3"].value
            self.c4 = parameters["c4"].value
            self.c5 = parameters["c5"].value

        if not fit_global_parameter.instrumental_parameters is None:
            self.U = parameters["U"].value
            self.V = parameters["V"].value
            self.W = parameters["W"].value
            self.a = parameters["a"].value
            self.b = parameters["b"].value
            self.c = parameters["c"].value

        if not fit_global_parameter.size_parameters is None:
            self.mu    = parameters["mu"].value
            self.sigma = parameters["sigma"].value

        if not fit_global_parameter.strain_parameters is None:
            self.aa = parameters["aa"].value
            self.bb = parameters["bb"].value
            self.A = parameters["e1"].value # in realtà è E1 dell'invariante PAH
            self.B = parameters["e6"].value # in realtà è E6 dell'invariante PAH


    @classmethod
    def get_amplitude(cls, parameters, reflection_index):
        return parameters["I{}".format(reflection_index+1)].value



#################################################
#
# SCIPY FIT FUNCTION
#
#################################################

def fit_function(parameters, s, I):

    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    common_fitting_data = CommonFittingData(parameters)

    if CrystalStructure.is_cube(fit_global_parameter.fit_initialization.crystal_structure.simmetry):
        separated_peaks_functions = []

        for reflection_index in range(fit_global_parameter.fit_initialization.crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, parameters, common_fitting_data)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = Utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        # TEMPORARY BACKGROUND - to be replaced with proper Chebyshev
        if not fit_global_parameter.background_parameters is None:
            background = numpy.array([common_fitting_data.c0] * len(s_large))
        else:
            background = numpy.zeros(s_large.size)

        return I - numpy.interp(s, s_large, background + I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")

def get_fitted_intensity(parameters, s):

    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    common_fitting_data = CommonFittingData(parameters)

    if CrystalStructure.is_cube(fit_global_parameter.fit_initialization.crystal_structure.simmetry):
        separated_peaks_functions = []

        for reflection_index in range(fit_global_parameter.fit_initialization.crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, parameters, common_fitting_data)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = Utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        # TEMPORARY BACKGROUND - to be replaced with proper Chebyshev
        if not fit_global_parameter.background_parameters is None:
            background = numpy.array([common_fitting_data.c0] * len(s_large))
        else:
            background = numpy.zeros(s_large.size)

        return numpy.interp(s, s_large, background + I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")