
import numpy
from scipy.optimize import curve_fit

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface, FitterListener
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import create_one_peak

class FitterScipy(FitterInterface):

    def do_fit(self, fit_global_parameters, current_iteration):
        parameters, boundaries = fit_global_parameters.to_scipy_tuple()
        
        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        current_parameters = parameters
        current_covariance = None

        try:
            current_parameters, current_covariance = self.call_scipy_curve_fit(s_experimental, intensity_experimental, current_parameters, boundaries)
        except ValueError as err:
            if str(err) == "`x0` violates bound constraints.":
                pass
            elif str(err) == "`x0` is infeasible.":
                raise ValueError("Fit cannot start: one ore more fit input parameters violate their boudaries")
            else:
                raise err

        fitted_parameters = current_parameters
        fitted_covariance = current_covariance

        fit_global_parameters_out = self.build_fit_global_parameters_out(fitted_parameters)

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = fit_function(s_experimental, fitted_parameters)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=s_experimental[index]))

        return fitted_pattern, fit_global_parameters_out

    def build_fit_global_parameters_out(self, fitted_parameters):
        fit_global_parameters = FitterListener.Instance().get_registered_fit_global_parameters().duplicate()
        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        crystal_structure.a.value = fitted_parameters[0]
        crystal_structure.b.value = fitted_parameters[1]
        crystal_structure.c.value = fitted_parameters[2]
        crystal_structure.alpha.value = fitted_parameters[3]
        crystal_structure.beta.value = fitted_parameters[4]
        crystal_structure.gamma.value = fitted_parameters[5]

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            crystal_structure.get_reflection(reflection_index).intensity.value = fitted_parameters[6+reflection_index]

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameters.background_parameters is None:
            fit_global_parameters.background_parameters.c0.value = fitted_parameters[last_index + 1]
            fit_global_parameters.background_parameters.c1.value = fitted_parameters[last_index + 2]
            fit_global_parameters.background_parameters.c2.value = fitted_parameters[last_index + 3]
            fit_global_parameters.background_parameters.c3.value = fitted_parameters[last_index + 4]
            fit_global_parameters.background_parameters.c4.value = fitted_parameters[last_index + 5]
            fit_global_parameters.background_parameters.c5.value = fitted_parameters[last_index + 6]

            last_index += fit_global_parameters.background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            fit_global_parameters.instrumental_parameters.U.value = fitted_parameters[last_index + 1]
            fit_global_parameters.instrumental_parameters.V.value = fitted_parameters[last_index + 2]
            fit_global_parameters.instrumental_parameters.W.value = fitted_parameters[last_index + 3]
            fit_global_parameters.instrumental_parameters.a.value = fitted_parameters[last_index + 4]
            fit_global_parameters.instrumental_parameters.b.value = fitted_parameters[last_index + 5]
            fit_global_parameters.instrumental_parameters.c.value = fitted_parameters[last_index + 6]

            last_index += fit_global_parameters.instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            fit_global_parameters.size_parameters.mu.value    = fitted_parameters[last_index + 1]
            fit_global_parameters.size_parameters.sigma.value = fitted_parameters[last_index + 2]

            last_index += fit_global_parameters.size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            fit_global_parameters.strain_parameters.aa.value = fitted_parameters[last_index + 1]
            fit_global_parameters.strain_parameters.bb.value = fitted_parameters[last_index + 2]
            fit_global_parameters.strain_parameters.e1.value = fitted_parameters[last_index + 3] # in realtà è E1 dell'invariante PAH
            fit_global_parameters.strain_parameters.e6.value = fitted_parameters[last_index + 4] # in realtà è E6 dell'invariante PAH

            last_index += fit_global_parameters.strain_parameters.get_parameters_count()

        return fit_global_parameters


    def call_scipy_curve_fit(self,
                             s_experimental,
                             intensity_experimental,
                             parameters,
                             boundaries):
        return curve_fit(f=fit_function,
                         xdata=s_experimental,
                         ydata=intensity_experimental,
                         sigma=numpy.sqrt(intensity_experimental),
                         p0=parameters,
                         bounds=boundaries)

class CommonFittingData():

    def __init__(self, parameters):
        fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
        crystal_structure = fit_global_parameter.fit_initialization.crystal_structure

        self.lattice_parameter = parameters[0]

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameter.background_parameters is None:
            self.c0 = parameters[last_index + 1]
            self.c1 = parameters[last_index + 2]
            self.c2 = parameters[last_index + 3]
            self.c3 = parameters[last_index + 4]
            self.c4 = parameters[last_index + 5]
            self.c5 = parameters[last_index + 6]

            last_index += fit_global_parameter.background_parameters.get_parameters_count()

        if not fit_global_parameter.instrumental_parameters is None:
            self.U = parameters[last_index + 1]
            self.V = parameters[last_index + 2]
            self.W = parameters[last_index + 3]
            self.a = parameters[last_index + 4]
            self.b = parameters[last_index + 5]
            self.c = parameters[last_index + 6]

            last_index += fit_global_parameter.instrumental_parameters.get_parameters_count()

        if not fit_global_parameter.size_parameters is None:
            self.mu    = parameters[last_index + 1]
            self.sigma = parameters[last_index + 2]

            last_index += fit_global_parameter.size_parameters.get_parameters_count()

        if not fit_global_parameter.strain_parameters is None:
            self.aa = parameters[last_index + 1]
            self.bb = parameters[last_index + 2]
            self.A = parameters[last_index + 3] # in realtà è E1 dell'invariante PAH
            self.B = parameters[last_index + 4] # in realtà è E6 dell'invariante PAH

            last_index += fit_global_parameter.strain_parameters.get_parameters_count()

        self.last_index = last_index

    @classmethod
    def get_amplitude(cls, parameters, reflection_index):
        return parameters[6 + reflection_index]


#################################################
#
# SCIPY FIT FUNCTION
#
#################################################

def fit_function(s, *parameters):

    if len(parameters) == 1:
        parameters = parameters[0]

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


