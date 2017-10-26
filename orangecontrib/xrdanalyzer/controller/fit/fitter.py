
import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc

from orangecontrib.xrdanalyzer import Singleton, synchronized_method

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Simmetry, Reflection
from orangecontrib.xrdanalyzer.util.general_functions import fft

@Singleton
class FitterListener():
    registered_fit_global_parameters = None
    space_parameters = None
    specific_fitter_data = None

    @synchronized_method
    def register_fit_global_parameters(self, fit_global_parameters = None):
        self.registered_fit_global_parameters = fit_global_parameters
        self.space_parameters = fit_global_parameters.space_parameters()

    @synchronized_method
    def register_specific_fitter_data(self, specific_fitter_data=None):
        self.specific_fitter_data = specific_fitter_data
    
    def get_registered_fit_global_parameters(self):
        return self.registered_fit_global_parameters

    def get_registered_space_parameters(self):
        return self.space_parameters
    
    def get_registered_specific_fitter_data(self):
        return self.specific_fitter_data


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


class FitterPrototype(FitterInterface):

    def do_specific_fit(self, fit_global_parameters):
        parameters, boundaries = fit_global_parameters.to_scipy_tuple()
        
        FitterListener.Instance().register_specific_fitter_data(CommonFittingData(parameters))
        
        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

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
                         bounds=boundaries,
                         method="dogbox")

def fit_function(s, *parameters):

    if len(parameters) == 1:
        parameters = parameters[0]

    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()

    if CrystalStructure.is_cube(fit_global_parameter.fit_initialization.crystal_structure.simmetry):
        separated_peaks_functions = []

        for reflection_index in range(fit_global_parameter.fit_initialization.crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, parameters)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        if not fit_global_parameter.background_parameters is None:
            # TEMPORARY
            last_index = fit_global_parameter.fit_initialization.crystal_structure.get_parameters_count() - 1 + fit_global_parameter.background_parameters.get_parameters_count()

            background = numpy.array([parameters[last_index + 1]] * len(s_large))
        else:
            background = numpy.zeros(s_large.size)

        return numpy.interp(s, s_large, background + I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")


class CommonFittingData():

    def __init__(self, parameters):
        fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
        crystal_structure = fit_global_parameter.fit_initialization.crystal_structure

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameter.background_parameters is None:
            self.a0 = parameters[last_index + 1]
            self.a1 = parameters[last_index + 2]
            self.a2 = parameters[last_index + 3]
            self.a3 = parameters[last_index + 4]
            self.a4 = parameters[last_index + 5]
            self.a5 = parameters[last_index + 6]

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

import matplotlib.pyplot as plt

def create_one_peak(reflection_index, parameters):
    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    fit_space_parameters = FitterListener.Instance().get_registered_space_parameters()
    common_fitting_data = FitterListener.Instance().get_registered_specific_fitter_data()

    crystal_structure = fit_global_parameter.fit_initialization.crystal_structure

    reflection = crystal_structure.get_reflection(reflection_index)

    lattice_parameter = parameters[0]
    amplitude = parameters[6 + reflection_index]

    fourier_amplitudes = None

    if not fit_global_parameter.instrumental_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = instrumental_function(fit_space_parameters.L,
                                                       reflection.h,
                                                       reflection.k,
                                                       reflection.l,
                                                       lattice_parameter,
                                                       fit_global_parameter.fit_initialization.diffraction_pattern.wavelength,
                                                       common_fitting_data.U,
                                                       common_fitting_data.V,
                                                       common_fitting_data.W,
                                                       common_fitting_data.a,
                                                       common_fitting_data.b,
                                                       common_fitting_data.c)
        else:
            fourier_amplitudes *= instrumental_function(fit_space_parameters.L,
                                                        reflection.h,
                                                        reflection.k,
                                                        reflection.l,
                                                        lattice_parameter,
                                                        fit_global_parameter.fit_initialization.diffraction_pattern.wavelength,
                                                        common_fitting_data.U,
                                                        common_fitting_data.V,
                                                        common_fitting_data.W,
                                                        common_fitting_data.a,
                                                        common_fitting_data.b,
                                                        common_fitting_data.c)


    if not fit_global_parameter.size_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = size_function_lognormal(fit_space_parameters.L,
                                                         common_fitting_data.sigma,
                                                         common_fitting_data.mu)
        else:
            fourier_amplitudes *= size_function_lognormal(fit_space_parameters.L,
                                                          common_fitting_data.sigma,
                                                          common_fitting_data.mu)

    if not fit_global_parameter.strain_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = strain_function(fit_space_parameters.L,
                                                 reflection.h,
                                                 reflection.k,
                                                 reflection.l,
                                                 lattice_parameter,
                                                 common_fitting_data.aa,
                                                 common_fitting_data.bb,
                                                 common_fitting_data.A,
                                                 common_fitting_data.B)
        else:
            fourier_amplitudes *= strain_function(fit_space_parameters.L,
                                                  reflection.h,
                                                  reflection.k,
                                                  reflection.l,
                                                  lattice_parameter,
                                                  common_fitting_data.aa,
                                                  common_fitting_data.bb,
                                                  common_fitting_data.A,
                                                  common_fitting_data.B)

    s, I = fft(fourier_amplitudes,
               n_steps=fit_global_parameter.fit_initialization.fft_parameters.n_step,
               dL=fit_space_parameters.dL)

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

def instrumental_function (L, h, k, l, lattice_parameter, wavelength, U, V, W, a, b, c):
    ln2 = numpy.log(2)

    theta = utilities.theta_hkl(lattice_parameter, h,k,l,wavelength)

    eta = a + b * theta + c * theta**2
    hwhm = 0.5 * numpy.sqrt(U * (numpy.tan(theta))**2
                            + V * numpy.tan(theta) + W)

    k = (1 + (1 - eta)/(eta * numpy.sqrt(numpy.pi*ln2)))**(-1)

    sigma = hwhm*numpy.cos(theta/wavelength)

    exponent_1 = -((numpy.pi*sigma*L)**2)/ ln2
    exponent_2 = -2*numpy.pi*sigma*L

    return (1-k)*numpy.exp(exponent_1) + k*numpy.exp(exponent_2)


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
    def get_twotheta_from_s(cls, s, wavelength):
        if s is None: return None

        return numpy.degrees(2 * numpy.arcsin(s * wavelength / 2))

    @classmethod
    def theta_hkl (cls, a, h, k, l , wavelength):
        return cls.get_twotheta_from_s(cls.s_hkl(a, h, k, l), wavelength)


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


from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternLimits, DiffractionPatternFactory

if __name__=="__main__":
    filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/FeMo_Batch4_GiaraA_1_HQ.xye"
    #filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"
    wavelength = 0.0826# nm

    crystal_structure = CrystalStructure.init_cube(a=FitParameter(parameter_name="a0", value=0.2873, fixed=True), simmetry=Simmetry.BCC)
    crystal_structure.add_reflection(Reflection(1, 1, 0, intensity=FitParameter(value=1000.0, boundary=Boundary(min_value=100, max_value=20000.0))))

    fit_initialization = FitInitialization(diffraction_pattern=DiffractionPatternFactory.create_diffraction_pattern_from_file(file_name=filename,
                                                                                                                              wavelength=wavelength,
                                                                                                                              limits=DiffractionPatternLimits(twotheta_min=20,
                                                                                                                                                              twotheta_max=27)),
                                           crystal_structure=crystal_structure,
                                           fft_parameters=FFTInitParameters(s_max=9.0, n_step=8192))

    size_parameters = SizeParameters(shape=Shape.SPHERE,
                                     distribution=Distribution.LOGNORMAL,
                                     mu=FitParameter(value=2.1711, boundary=Boundary(min_value=0.01, max_value=10.0)),
                                     sigma=FitParameter(value=0.353, boundary=Boundary(min_value=0.01, max_value=0.8)))

    fit_global_parameters = FitGlobalParameters(fit_initialization=fit_initialization,
                                                size_parameters=size_parameters)

    fitter = FitterFactory.create_fitter()

    fit = fitter.do_fit(fit_global_parameters)

    tt, I, e, s = fit.tuples()

    plt.plot(tt, I)
    plt.show()
