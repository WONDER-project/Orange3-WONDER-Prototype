from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterListener

# -----------------------------------
# FOURIER FUNCTIONS
# -----------------------------------


class FourierTransformRealOnly:

    @classmethod
    def real_absolute_fourier(cls, y):
        return numpy.fft.fftshift(numpy.abs(numpy.real(numpy.fft.fft(y))))

    @classmethod
    def fft_normalized(cls, y_fft, n_steps, dL):
        s = numpy.fft.fftfreq(n_steps, dL)
        s = numpy.fft.fftshift(s)

        integral = numpy.trapz(y_fft, s)

        return s, y_fft / integral

    @classmethod
    def fft(cls, f, n_steps, dL):
        return cls.fft_normalized(cls.real_absolute_fourier(f), n_steps, dL)

from scipy.integrate import simps

class FourierTransformFull:
    @classmethod
    def fourier(cls, y):
        return numpy.fft.fftshift(numpy.fft.fft(y))

    @classmethod
    def fft_shifted(cls, y_fft, n_steps, dL):
        s = numpy.fft.fftfreq(n_steps, dL)
        s = numpy.fft.fftshift(s)

        y_fft -= y_fft[0]

        return s, y_fft

    @classmethod
    def fft_real(cls, f, n_steps, dL):
        return cls.fft_shifted(numpy.real(cls.fourier(f)), n_steps, dL)

    @classmethod
    def fft_imag(cls, f, n_steps, dL):
        return cls.fft_shifted(numpy.imag(cls.fourier(f)), n_steps, dL)

    @classmethod
    def normalize(cls, s, i):
        return s, i/simps(i, s)

#########################################################################
# MAIN FUNCTION

from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAH, WarrenModel

def create_one_peak(reflection_index, fit_global_parameter):
    fit_space_parameters = fit_global_parameter.space_parameters()
    crystal_structure = fit_global_parameter.fit_initialization.crystal_structure
    reflection = crystal_structure.get_reflection(reflection_index)
    amplitude = reflection.intensity.value

    fourier_amplitudes = None

    if not fit_global_parameter.instrumental_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = instrumental_function(fit_space_parameters.L,
                                                       reflection.h,
                                                       reflection.k,
                                                       reflection.l,
                                                       crystal_structure.a.value,
                                                       fit_global_parameter.fit_initialization.diffraction_pattern.wavelength,
                                                       fit_global_parameter.instrumental_parameters.U.value,
                                                       fit_global_parameter.instrumental_parameters.V.value,
                                                       fit_global_parameter.instrumental_parameters.W.value,
                                                       fit_global_parameter.instrumental_parameters.a.value,
                                                       fit_global_parameter.instrumental_parameters.b.value,
                                                       fit_global_parameter.instrumental_parameters.c.value)
        else:
            fourier_amplitudes *= instrumental_function(fit_space_parameters.L,
                                                        reflection.h,
                                                        reflection.k,
                                                        reflection.l,
                                                        crystal_structure.a.value,
                                                        fit_global_parameter.fit_initialization.diffraction_pattern.wavelength,
                                                        fit_global_parameter.instrumental_parameters.U.value,
                                                        fit_global_parameter.instrumental_parameters.V.value,
                                                        fit_global_parameter.instrumental_parameters.W.value,
                                                        fit_global_parameter.instrumental_parameters.a.value,
                                                        fit_global_parameter.instrumental_parameters.b.value,
                                                        fit_global_parameter.instrumental_parameters.c.value)


    if not fit_global_parameter.size_parameters is None:
        if fourier_amplitudes is None:
            fourier_amplitudes = size_function_lognormal(fit_space_parameters.L,
                                                         fit_global_parameter.size_parameters.sigma.value,
                                                         fit_global_parameter.size_parameters.mu.value)
        else:
            fourier_amplitudes *= size_function_lognormal(fit_space_parameters.L,
                                                          fit_global_parameter.size_parameters.sigma.value,
                                                          fit_global_parameter.size_parameters.mu.value)

    if not fit_global_parameter.strain_parameters is None:
        if isinstance(fit_global_parameter.strain_parameters, InvariantPAH):
            if fourier_amplitudes is None:
                fourier_amplitudes = strain_invariant_function(fit_space_parameters.L,
                                                               reflection.h,
                                                               reflection.k,
                                                               reflection.l,
                                                               crystal_structure.a.value,
                                                               fit_global_parameter.strain_parameters.aa.value,
                                                               fit_global_parameter.strain_parameters.bb.value,
                                                               fit_global_parameter.strain_parameters.e1.value,
                                                               fit_global_parameter.strain_parameters.e6.value)
            else:
                fourier_amplitudes *= strain_invariant_function(fit_space_parameters.L,
                                                                reflection.h,
                                                                reflection.k,
                                                                reflection.l,
                                                                crystal_structure.a.value,
                                                                fit_global_parameter.strain_parameters.aa.value,
                                                                fit_global_parameter.strain_parameters.bb.value,
                                                                fit_global_parameter.strain_parameters.e1.value,
                                                                fit_global_parameter.strain_parameters.e6.value)

        elif isinstance(fit_global_parameter.strain_parameters, WarrenModel):
            fourier_amplitudes_re, fourier_amplitudes_im = strain_warren_function(fit_space_parameters.L,
                                                                                  reflection.h,
                                                                                  reflection.k,
                                                                                  reflection.l,
                                                                                  crystal_structure.a.value,
                                                                                  fit_global_parameter.strain_parameters.average_cell_parameter.value)

            if fourier_amplitudes is None:
                fourier_amplitudes = fourier_amplitudes_re + 1j*fourier_amplitudes_im
            else:
                fourier_amplitudes = (fourier_amplitudes*fourier_amplitudes_re) + 1j*(fourier_amplitudes*fourier_amplitudes_im)

    is_old = False

    if not is_old:
        sr, fft_real = FourierTransformFull.fft_real(numpy.real(fourier_amplitudes),
                                            n_steps=fit_global_parameter.fit_initialization.fft_parameters.n_step,
                                            dL=fit_space_parameters.dL)

        si, fft_imag = FourierTransformFull.fft_imag(numpy.imag(fourier_amplitudes),
                                            n_steps=fit_global_parameter.fit_initialization.fft_parameters.n_step,
                                            dL=fit_space_parameters.dL)

        s, I = FourierTransformFull.normalize(sr, fft_real - fft_imag)
    else:
        s, I = FourierTransformRealOnly.fft(fourier_amplitudes,
                                            n_steps=fit_global_parameter.fit_initialization.fft_parameters.n_step,
                                            dL=fit_space_parameters.dL)

    s += Utilities.s_hkl(crystal_structure.a.value, reflection.h, reflection.k, reflection.l)


    return s, amplitude*I


######################################################################
# FUNZIONI WPPM
######################################################################

import numpy
from scipy.special import erfc
from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities

######################################################################
# SIZE
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

######################################################################
# STRAIN
######################################################################

def strain_invariant_function (L, h, k, l, lattice_parameter, a, b, A, B):
    shkl = Utilities.s_hkl(lattice_parameter, h, k, l)
    H = Utilities.Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -2*((numpy.pi*shkl)**2)*C*(a*L + b*L*L)

    return numpy.exp(exponent)

import os
from Orange.canvas import resources

def load_warren_files():
    delta_l_dict = {}
    delta_l2_dict = {}

    path = os.path.join(resources.package_dirname("orangecontrib.xrdanalyzer.controller.fit"), "data")
    path = os.path.join(path, "delta_l_files")

    filenames = os.listdir(path)

    for filename in filenames:
        if filename.endswith('FTinfo'):
            hkl = filename[0:3]
            name =  os.path.join(path, filename)
            data = numpy.loadtxt(name)
            L = data[:,0]

            delta_l_dict[hkl] = [L, data[:, 1]] # deltal_fun
            delta_l2_dict[hkl] = [L, data[:,2]] # deltal2_fun

    return delta_l_dict, delta_l2_dict

delta_l_dict, delta_l2_dict = load_warren_files()

def modify_delta_l(l, delta_l, lattice_parameter, average_lattice_parameter):
    return delta_l - (average_lattice_parameter/lattice_parameter -1)*l

def modify_delta_l2(l, delta_l, delta_l2, lattice_parameter, average_lattice_parameter):
    return delta_l2 - 2*delta_l*(average_lattice_parameter/lattice_parameter -1)*l \
               + ((average_lattice_parameter/lattice_parameter -1)*l)**2

def re_warren_strain(s_hkl, delta_l2):
    return numpy.exp(-0.5*((s_hkl*2*numpy.pi)**2)*delta_l2)

def im_warren_strain(s_hkl, delta_l):
    return (s_hkl*2*numpy.pi)*delta_l

def strain_warren_function(L, h, k, l, lattice_parameter, average_lattice_parameter):
    hkl = str(h) + str(k) + str(l)
    
    if hkl not in delta_l_dict.keys():
        return numpy.ones(len(L)), numpy.zeros(len(L))
    
    delta_l_entry = delta_l_dict[hkl]
    delta_l2_entry = delta_l2_dict[hkl]

    l_local  = delta_l_entry[0]
    delta_l  = delta_l_entry[1]
    delta_l2 = delta_l2_entry[1]

    new_delta_l  = modify_delta_l(l_local, delta_l, lattice_parameter, average_lattice_parameter)
    new_delta_l2 = modify_delta_l2(l_local, delta_l, delta_l2, lattice_parameter, average_lattice_parameter)

    new_delta_l  = numpy.interp(L, l_local, new_delta_l)
    new_delta_l2 = numpy.interp(L, l_local, new_delta_l2)

    s_hkl = Utilities.s_hkl(average_lattice_parameter, h, k, l)

    return re_warren_strain(s_hkl, new_delta_l2), im_warren_strain(s_hkl, new_delta_l)

######################################################################
# INSTRUMENTAL
######################################################################

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