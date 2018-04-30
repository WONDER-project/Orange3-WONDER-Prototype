
import numpy
from scipy.optimize import curve_fit

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface, FitterListener, fit_function
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAH, WarrenModel

class FitterScipy(FitterInterface):

    def init_fitter(self, fit_global_parameters):
        self.fit_global_parameters = fit_global_parameters
        self.fit_global_parameters.evaluate_functions()

        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = self.fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        self.twotheta_experimental = twotheta_experimental
        self.intensity_experimental = intensity_experimental
        self.error_experimental = error_experimental
        self.s_experimental = s_experimental

    def do_fit(self, current_fit_global_parameters, current_iteration):
        self.fit_global_parameters = current_fit_global_parameters.duplicate()

        parameters, boundaries = self.fit_global_parameters.tuple()

        current_parameters = parameters
        current_covariance = None

        try:
            FitterListener.register_fit_global_parameters(self.fit_global_parameters)

            current_parameters, current_covariance = self.call_scipy_curve_fit(self.s_experimental,
                                                                               self.intensity_experimental,
                                                                               current_parameters,
                                                                               boundaries)

            self.fit_global_parameters = build_fit_global_parameters_out(self.fit_global_parameters, current_parameters)
            self.fit_global_parameters.evaluate_functions()
        except ValueError as err:
            if str(err) == "`x0` violates bound constraints.":
                pass
            elif str(err) == "`x0` is infeasible.":
                raise ValueError("Fit cannot start: one ore more fit input parameters violate their boudaries")
            else:
                raise err

        fitted_parameters = current_parameters
        fitted_covariance = current_covariance

        self.fit_global_parameters = build_fit_global_parameters_out(self.fit_global_parameters, fitted_parameters)
        self.fit_global_parameters.evaluate_functions()

        fit_global_parameters_out = self.fit_global_parameters

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = self.fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = fit_function(self.s_experimental, fit_global_parameters_out)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=self.twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=self.s_experimental[index]))

        return fitted_pattern, fit_global_parameters_out, None


    def call_scipy_curve_fit(self,
                             s_experimental,
                             intensity_experimental,
                             parameters,
                             boundaries):
        #TODO: da aggiustare
        return curve_fit(f=fit_function_tuple,
                         xdata=s_experimental,
                         ydata=intensity_experimental,
                         sigma=numpy.sqrt(intensity_experimental),
                         p0=parameters,
                         bounds=boundaries)


def build_fit_global_parameters_out(fit_global_parameters, fitted_parameters):
    crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

    crystal_structure.a.set_value(fitted_parameters[0])
    crystal_structure.b.set_value(fitted_parameters[1])
    crystal_structure.c.set_value(fitted_parameters[2])
    crystal_structure.alpha.set_value(fitted_parameters[3])
    crystal_structure.beta.set_value(fitted_parameters[4])
    crystal_structure.gamma.set_value(fitted_parameters[5])

    for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
        crystal_structure.get_reflection(reflection_index).intensity.set_value(fitted_parameters[6+reflection_index])

    last_index = crystal_structure.get_parameters_count() - 1

    if not fit_global_parameters.background_parameters is None:
        fit_global_parameters.background_parameters.c0.set_value(fitted_parameters[last_index + 1])
        fit_global_parameters.background_parameters.c1.set_value(fitted_parameters[last_index + 2])
        fit_global_parameters.background_parameters.c2.set_value(fitted_parameters[last_index + 3])
        fit_global_parameters.background_parameters.c3.set_value(fitted_parameters[last_index + 4])
        fit_global_parameters.background_parameters.c4.set_value(fitted_parameters[last_index + 5])
        fit_global_parameters.background_parameters.c5.set_value(fitted_parameters[last_index + 6])

        last_index += fit_global_parameters.background_parameters.get_parameters_count()

    if not fit_global_parameters.instrumental_parameters is None:
        fit_global_parameters.instrumental_parameters.U.set_value(fitted_parameters[last_index + 1])
        fit_global_parameters.instrumental_parameters.V.set_value(fitted_parameters[last_index + 2])
        fit_global_parameters.instrumental_parameters.W.set_value(fitted_parameters[last_index + 3])
        fit_global_parameters.instrumental_parameters.a.set_value(fitted_parameters[last_index + 4])
        fit_global_parameters.instrumental_parameters.b.set_value(fitted_parameters[last_index + 5])
        fit_global_parameters.instrumental_parameters.c.set_value(fitted_parameters[last_index + 6])

        last_index += fit_global_parameters.instrumental_parameters.get_parameters_count()

    if not fit_global_parameters.lab6_tan_correction is None:
        fit_global_parameters.lab6_tan_correction.ax.set_value(fitted_parameters[last_index + 1])
        fit_global_parameters.lab6_tan_correction.bx.set_value(fitted_parameters[last_index + 2])
        fit_global_parameters.lab6_tan_correction.cx.set_value(fitted_parameters[last_index + 3])
        fit_global_parameters.lab6_tan_correction.dx.set_value(fitted_parameters[last_index + 4])
        fit_global_parameters.lab6_tan_correction.ex.set_value(fitted_parameters[last_index + 5])

        last_index += fit_global_parameters.lab6_tan_correction.get_parameters_count()

    if not fit_global_parameters.size_parameters is None:
        fit_global_parameters.size_parameters.mu.set_value(fitted_parameters[last_index + 1])
        fit_global_parameters.size_parameters.sigma.set_value(fitted_parameters[last_index + 2])

        last_index += fit_global_parameters.size_parameters.get_parameters_count()

    if not fit_global_parameters.strain_parameters is None:
        if isinstance(fit_global_parameters.strain_parameters, InvariantPAH):
            fit_global_parameters.strain_parameters.aa.set_value(fitted_parameters[last_index + 1])
            fit_global_parameters.strain_parameters.bb.set_value(fitted_parameters[last_index + 2])
            fit_global_parameters.strain_parameters.e1.set_value(fitted_parameters[last_index + 3]) # in realtà è E1 dell'invariante PAH
            fit_global_parameters.strain_parameters.e6.set_value(fitted_parameters[last_index + 4]) # in realtà è E6 dell'invariante PAH
        elif isinstance(fit_global_parameters.strain_parameters, WarrenModel):
            fit_global_parameters.strain_parameters.average_cell_parameter.set_value(fitted_parameters[last_index + 1])

        last_index += fit_global_parameters.strain_parameters.get_parameters_count()

    if fit_global_parameters.has_functions(): fit_global_parameters.evaluate_functions()

    return fit_global_parameters

def fit_function_tuple(s, parameters):
    fit_global_parameters = build_fit_global_parameters_out(FitterListener.get_registered_fit_global_parameters(), parameters)
    return fit_function(s, fit_global_parameters)
