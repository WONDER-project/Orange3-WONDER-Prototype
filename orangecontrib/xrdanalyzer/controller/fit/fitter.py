

class FitterInterface:

    def do_fit(self, fit_global_parameters=None):
        FitterListener.Instance().register_fit_global_parameters(fit_global_parameters)

        return self.do_specific_fit(fit_global_parameters)


    def do_specific_fit(self, fit_global_parameters):
        raise NotImplementedError("Abstract")


class FitterFactory():

    @classmethod
    def create_fitter(cls):
        return FitterPrototype()
        #return FitterMock()


class FitterMock(FitterInterface):

    def do_specific_fit(self, fit_global_parameters):
        return DiffractionPattern()

import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc

from orangecontrib.xrdanalyzer.controller.fit.fitter_listener import FitterListener
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Simmetry, Reflection

class FitterPrototype(FitterInterface):

    def do_specific_fit(self, fit_global_parameters):
        parameters, boundaries = fit_global_parameters.to_scipy_tuple()
        twotheta_experimental, intensity_experimental, error_experimental,  s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        fitted_parameters, covariance = self.call_scipy_curve_fit(s_experimental, intensity_experimental, parameters, boundaries)

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = fit_function(s_experimental, fitted_parameters)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=s_experimental[index]))

        return fitted_pattern

    def call_scipy_curve_fit(self,
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


def fit_function(s, *parameters):
    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    create_one_peak_data = CreateOnePeakData(parameters)

    if CrystalStructure.is_cube(create_one_peak_data.crystal_structure.simmetry):

        separated_peaks_functions = []

        for reflection_index in range(create_one_peak_data.n_peaks):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, create_one_peak_data, parameters)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        if not fit_global_parameter.background_parameters is None:
            last_index = fit_global_parameter.fit_initialization.crystal_structure.get_parameters_count() - 1 + fit_global_parameter.background_parameters.get_parameters_count()

            background = numpy.array([parameters[last_index + 1]] * len(s_large))
        else:
            background = numpy.zeros(s_large.size)

        return numpy.interp(s, s_large, background + I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")

from orangecontrib.xrdanalyzer.util.general_functions import fft


class CreateOnePeakData():


    def __init__(self, parameters):
        self.fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
        self.Global = FitterListener.Instance().Global() # nome storico, comodo non cambiarlo

        self.crystal_structure = self.fit_global_parameter.fit_initialization.crystal_structure

        self.n_peaks = self.crystal_structure.get_reflections_count()

        self.L = numpy.linspace(self.Global.dL,
                                self.Global.L_max + self.Global.dL,
                                self.fit_global_parameter.fit_initialization.fft_parameters.n_step)

        last_index = self.crystal_structure.get_parameters_count() - 1

        if not self.fit_global_parameter.background_parameters is None:
            last_index += self.fit_global_parameter.background_parameters.get_parameters_count()

        if not self.fit_global_parameter.instrumental_parameters is None:
            last_index += self.fit_global_parameter.instrumental_parameters.get_parameters_count()

        if not self.fit_global_parameter.size_parameters is None:
            self.sigma = parameters[last_index + 1]
            self.mu    = parameters[last_index + 2]

            last_index += self.fit_global_parameter.instrumental_parameters.get_parameters_count()

        if not self.fit_global_parameter.strain_parameters is None:
            self.a = parameters[last_index + 1]
            self.b = parameters[last_index + 2]
            self.A = parameters[last_index + 3] # in realtà è E1 dell'invariante PAH
            self.B = parameters[last_index + 4] # in realtà è E6 dell'invariante PAH

            last_index += self.fit_global_parameter.instrumental_parameters.get_parameters_count()


def create_one_peak(reflection_index, create_one_peak_data, parameters):
    reflection = create_one_peak_data.crystal_structure.get_reflection(reflection_index)

    lattice_parameter = parameters[0]
    amplitude = parameters[6 + create_one_peak_data.n_peaks*reflection_index]

    fourier_amplitudes = None

    if not create_one_peak_data.fit_global_parameter.instrumental_parameters is None:
        fourier_amplitudes = None # TODO: aggiungere funzione strumentale

    if not create_one_peak_data.fit_global_parameter.size_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = size_function_lognormal(create_one_peak_data.L, create_one_peak_data.sigma, create_one_peak_data.mu)
        else:
            fourier_amplitudes *= size_function_lognormal(create_one_peak_data.L, create_one_peak_data.sigma, create_one_peak_data.mu)

    if not create_one_peak_data.fit_global_parameter.strain_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = strain_function(create_one_peak_data.L, reflection.h, reflection.k, reflection.l, lattice_parameter, create_one_peak_data.a, create_one_peak_data.b, create_one_peak_data.A, create_one_peak_data.B)
        else:
            fourier_amplitudes *= strain_function(create_one_peak_data.L, reflection.h, reflection.k, reflection.l, lattice_parameter, create_one_peak_data.a, create_one_peak_data.b, create_one_peak_data.A, create_one_peak_data.B)

    s, I = fft(fourier_amplitudes,
               n_steps=create_one_peak_data.fit_global_parameter.fit_initialization.fft_parameters.n_step,
               dL=create_one_peak_data.Global.dL)

    s += utilities.s_hkl(lattice_parameter, reflection.h, reflection.k, reflection.l)

    return s, amplitude*I








######################################################################
# FUNZIONI VARIE
######################################################################

def size_function_common_volume (L, D):
    LfracD = L/D
    return 1 - 1.5*LfracD + 0.5*LfracD**3

def size_function_lognormal(L, sigma, mu):
    L = numpy.abs(L)
    lnL = numpy.log(L)
    sqrt2 = numpy.sqrt(2)
    a = 0.5*erfc((lnL - mu -3*sigma**2)/(sigma*sqrt2))
    b = -0.75*L*erfc((lnL - mu -2*sigma**2)/(sigma*sqrt2))\
                *numpy.exp(-mu - 2.5*sigma**2)
    c = 0.25*(L**3)*erfc((lnL - mu)/(sigma*sqrt2)) \
                *numpy.exp(-3*mu - 4.5*sigma**2)

    return  a + b + c

def strain_function (L, h, k, l, lattice_parameter, a, b, A, B):

    shkl = utilities.s_hkl(lattice_parameter, h, k, l)
    H = utilities.Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -2*((numpy.pi*shkl)**2)*C*(a*L + b*L*L)

    return numpy.exp(exponent)

class utilities:

    @classmethod
    def Hinvariant(cls, h, k, l):
        numerator = (h * h * k * k + k * k * l * l + l * l * h * h)
        denominator = (h * h + k * k + l * l) ** 2
        return numerator / denominator

    @classmethod
    def s_hkl(cls, a, h, k, l):
        return numpy.sqrt(h * h + k * k + l * l) / a

    @classmethod
    def isolate_peak(cls, s, I, smin, smax):
        data = []
        N = numpy.size(s)
        for i in numpy.arange(0, N):
            if s[i] > smin and s[i] < smax:
                data.append([s[i], I[i]])
        output = numpy.asarray(data)
        return output[:, 0], output[:, 1]

    @classmethod
    def merge_functions(cls, list_of_pairs, s_max, n_steps):
        # x step must be the same for all functions
        super_s = numpy.linspace(0, 4 * s_max, n_steps)
        super_I = numpy.zeros(n_steps)

        for function in list_of_pairs:
            super_I += numpy.interp(super_s, function[0], function[1])

        return super_s, super_I


