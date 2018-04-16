from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterListener
from orangecontrib.xrdanalyzer.util.general_functions import fft

def create_one_peak(reflection_index, parameters, common_fitting_data):
    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    fit_space_parameters = FitterListener.Instance().get_registered_space_parameters()

    crystal_structure = fit_global_parameter.fit_initialization.crystal_structure

    reflection = crystal_structure.get_reflection(reflection_index)

    amplitude = common_fitting_data.get_amplitude(parameters, reflection_index)

    fourier_amplitudes = None

    if not fit_global_parameter.instrumental_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = instrumental_function(fit_space_parameters.L,
                                                       reflection.h,
                                                       reflection.k,
                                                       reflection.l,
                                                       common_fitting_data.lattice_parameter,
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
                                                        common_fitting_data.lattice_parameter,
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
                                                 common_fitting_data.lattice_parameter,
                                                 common_fitting_data.aa,
                                                 common_fitting_data.bb,
                                                 common_fitting_data.A,
                                                 common_fitting_data.B)
        else:
            fourier_amplitudes *= strain_function(fit_space_parameters.L,
                                                  reflection.h,
                                                  reflection.k,
                                                  reflection.l,
                                                  common_fitting_data.lattice_parameter,
                                                  common_fitting_data.aa,
                                                  common_fitting_data.bb,
                                                  common_fitting_data.A,
                                                  common_fitting_data.B)

    s, I = fft(fourier_amplitudes,
               n_steps=fit_global_parameter.fit_initialization.fft_parameters.n_step,
               dL=fit_space_parameters.dL)

    s += Utilities.s_hkl(common_fitting_data.lattice_parameter, reflection.h, reflection.k, reflection.l)

    return s, amplitude*I


######################################################################
# FUNZIONI WPPM
######################################################################

import numpy
from scipy.special import erfc
from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities

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
    shkl = Utilities.s_hkl(lattice_parameter, h, k, l)
    H = Utilities.Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -2*((numpy.pi*shkl)**2)*C*(a*L + b*L*L)

    return numpy.exp(exponent)

def instrumental_function (L, h, k, l, lattice_parameter, wavelength, U, V, W, a, b, c):
    theta = Utilities.theta_hkl(lattice_parameter, h,k,l,wavelength)

    eta = a + b * theta + c * theta**2
    hwhm = 0.5 * numpy.sqrt(U * (numpy.tan(theta))**2
                            + V * numpy.tan(theta) + W)

    k = (1 + (1 - eta)/(eta * numpy.sqrt(numpy.pi*numpy.log(2))))**(-1)

    sigma = hwhm*numpy.cos(theta/wavelength)

    exponent_1 = -((numpy.pi*sigma*L)**2)/numpy.log(2)
    exponent_2 = -2*numpy.pi*sigma*L

    return (1-k)*numpy.exp(exponent_1) + k*numpy.exp(exponent_2)

######################################################################
# BACKGROUND
######################################################################

def add_chebyshev_background(s, I, parameters=[0, 0, 0, 0, 0, 0]):
    T = numpy.zeros(len(parameters))
    for i in range(0, len(s)):
        for j in range(0, len(parameters)):
            if j==0:
                T[j] = 1
            elif j==1:
                T[j] = s[i]
            else:
                T[j] = 2*s[i]*T[j-1] - T[j-2]

            I[i] += parameters[j]*T[j]

def add_polynomial_background(s, I, parameters=[0, 0, 0, 0, 0, 0]):
    for i in range(0, len(s)):
        for j in range(0, len(parameters)):
            I[i] += parameters[j]*numpy.pow(s[i], j)

def add_polynomial_N_background(s, I, parameters=[0, 0, 0, 0, 0, 0]):
    for i in range(0, len(s)):
        for j in range(1, len(parameters)/2, step=2):
            p = parameters[j]
            q = parameters[j+1]

            I[i] += p*numpy.pow(s[i], q)

def add_polynomial_0N_background(s, I, parameters=[0, 0, 0, 0, 0, 0]):
    n = len(parameters)

    for i in range(0, len(s)):
        for j in range(1, n/2, step=2):
            p = parameters[j]
            q = parameters[j+1]

            I[i] += p*numpy.pow((s[i]-parameters[0]), q)

def add_expdecay_background(s, I, parameters=[0, 0, 0, 0, 0, 0]):
    for i in range(0, len(s)):
        for j in range(1, 2*(len(parameters)-2), step=2):
            p = parameters[j]
            q = parameters[j+1]

            I[i] += p*numpy.exp(-numpy.abs(s[i]-parameters[0])*q)