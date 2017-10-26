import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc
import lmfit

import matplotlib.pyplot as plt


from orangecontrib.xrdanalyzer._test.controller.utility_methods import utilities
from orangecontrib.xrdanalyzer._test.controller.fftparameters import *


######################################################################

def fitterScipyCurveFit(function_to_fit,
                        s_experimental,
                        intensity_experimental,
                        listparameters):

    parameters, boundaries = listparameters.to_scipy_tuple()

    print(parameters)

    popt, pcov = curve_fit(f=function_to_fit,
                           xdata=s_experimental,
                           ydata=intensity_experimental,
                           sigma=1/numpy.sqrt(intensity_experimental),
                           p0=parameters,
                           method= 'trf',
                           bounds=boundaries)
    return popt, pcov

from lmfit import minimize, Minimizer, Parameters, Parameter, report_fit

def fitter_with_lmfit(function_to_fit, s_experimental, intensity_experimental, listparameters):

    minimizer = Minimizer(function_to_fit, nan_policy='omit', params=listparameters, fcn_args=(s_experimental, intensity_experimental),)

    return minimizer.minimize()
    #return minimizer.minimize(method='least_squares')

    #gmodel = lmfit.Model(function_to_fit)

    #return gmodel.fit(data=intensity_experimental, params= listparameters, s=s_experimental  )




######################################################################

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

def instrumental_function (L, lattice_parameter, h, k, l, wavelength, U,V,W, a, b, c):
    ln2 = numpy.log(2)

    theta = utilities.theta_hkl(lattice_parameter, h,k,l,wavelength)

    eta = a + b * theta + c * theta**2
    hwhm = 0.5 * numpy.sqrt(numpy.abs(U * (numpy.tan(theta))**2
                            + V * numpy.tan(theta) + W))

    k = (1 + (1 - eta)/(eta * numpy.sqrt(numpy.pi*ln2)))**(-1)

    sigma = hwhm*numpy.cos(theta/wavelength)



    exponent_1 = -((numpy.pi*sigma*L)**2)/ ln2
    exponent_2 = -2*numpy.pi*sigma*L

    return (1-k)*numpy.exp(exponent_1) + k*numpy.exp(exponent_2)

######################################################################
# Peaks Creation
######################################################################

def createonepeak(params, h, k, l):
    lattice_parameter = params[0]
    Amplitude = params[1]
    sigma = params[2]
    mu = params[3]
    a = params[4]
    b = params[5]
    A = params[6]
    B = params[7]


    L = numpy.linspace(Global.dL, Global.Lmax + Global.dL, Global.n_steps)

    #function_in_L = sizeFunctionCommonvolume(L,D)
    lognormal_function = sizeFunctionLognormal(L, sigma, mu)
    strain_function = strainFunction(L, h, k, l, lattice_parameter, a, b, A, B)


    s, I = fft(lognormal_function*strain_function)
    #s, I = fft(strainfunction)
    #s, I = fft(lognormalfunction)

    return s, Amplitude*I

def createonepeak_with_instrumental(params, h, k, l):
    lattice_parameter = params[0]
    Amplitude = params[1]
    sigma = params[2]
    mu = params[3]
    a = params[4]
    b = params[5]
    A = params[6]
    B = params[7]

    U = params[8]
    V = params[9]
    W = params[10]
    aa = params[11]
    bb = params[12]
    cc = params[13]
    wavelength = params[14]

    L = numpy.linspace(Global.dL, Global.Lmax + Global.dL, Global.n_steps)

    #function_in_L = sizeFunctionCommonvolume(L,D)
    lognormal_function = sizeFunctionLognormal(L, sigma, mu)
    strain_function = strainFunction(L, h, k, l, lattice_parameter, a, b, A, B)
    instrumental = instrumental_function(L, lattice_parameter, h, k, l, wavelength, U,V,W, aa, bb, cc)

    s, I = fft(lognormal_function*strain_function*instrumental)
    #s, I = fft(strainfunction)
    #s, I = fft(lognormalfunction)

    return s, Amplitude*I


def functionOfThePeak(s, *params):
    h, k, l = 1,1,0

    bkg = params[8]
    print('+',end= '')
    swrong, Iwrong = createonepeak(params, h, k, l)

    return numpy.interp(s, swrong + utilities.s_hkl(params[0], h, k, l), bkg + Iwrong)


def functionOfManyPeaks(s, *params):
    params_peak1 = [params[0],params[1],
                    params[4],params[5],
                    params[6],params[7],
                    params[8],params[9]]

    params_peak2 = [params[0], params[2],
                    params[4], params[5],
                    params[6], params[7],
                    params[8], params[9]]

    params_peak3 = [params[0], params[3],
                    params[4], params[5],
                    params[6], params[7],
                    params[8], params[9]]

    bkg = params[10]

    unpacked_params = [params_peak1, params_peak2,
                       params_peak3]

    separated_peaks_functions = []

    distances = utilities.firstpeaks(params[0], "bcc", 3)

    for i in range(0, len(distances)):
        h = int(distances[i][0].split()[0])
        k = int(distances[i][0].split()[1])
        l = int(distances[i][0].split()[2])
        sanalitycal, Ianalitycal = createonepeak(unpacked_params[i], h, k, l)
        sanalitycal += distances[i][1]

        separated_peaks_functions.append([sanalitycal, Ianalitycal])

    s_large, I_large = utilities.mergefunctions(separated_peaks_functions)

    return numpy.interp(s, s_large, bkg + I_large)



def functionNPeaks(s, *params):
    params_for_each_peak = []
    n_peaks = Global.n_peaks
    latticeparam = params[0]
    for index in range(n_peaks):
        params_for_each_peak.append(
            [params[0], params[index+1],
             params[n_peaks + 1], params[n_peaks + 2],
             params[n_peaks + 3], params[n_peaks + 4],
             params[n_peaks + 5], params[n_peaks + 6],
             params[n_peaks + 7], params[n_peaks + 8],
             params[n_peaks + 9], params[n_peaks + 10],
             params[n_peaks + 11], params[n_peaks + 12],
             params[n_peaks + 13]]
        )

    bkg = params[Global.n_peaks + 7]

    separated_peaks_functions = []

    for index in range(n_peaks):
        h, k, l = Global.hkl_list[index]

        sanalitycal, Ianalitycal = createonepeak_with_instrumental(params_for_each_peak[index], h, k, l)
        sanalitycal += utilities.s_hkl(latticeparam, h, k, l)

        separated_peaks_functions.append([sanalitycal, Ianalitycal])


    s_large, I_large = utilities.mergefunctions(separated_peaks_functions)

    return numpy.interp(s, s_large, bkg + I_large)

def functionNPeaks_lmfit_plot(params, s):
    params_for_each_peak = []
    n_peaks = Global.n_peaks
    latticeparam = params["lattice_parameter"]
    for index in range(n_peaks):
        params_for_each_peak.append(
            [params["lattice_parameter"], params["I{}".format(index+1)],
             params["sigma"], params["mu"],
             params["a"], params["b"],
             params["A"], params["B"],
             params["U"], params["V"],
             params["W"], params["aa"],
             params["bb"], params["cc"],
             params["wavelength"]]
        )

    bkg = params["bkg"]

    separated_peaks_functions = []

    for index in range(n_peaks):
        h, k, l = Global.hkl_list[index]

        sanalitycal, Ianalitycal = createonepeak_with_instrumental(params_for_each_peak[index], h, k, l)
        sanalitycal += utilities.s_hkl(latticeparam, h, k, l)

        separated_peaks_functions.append([sanalitycal, Ianalitycal])

    s_large, I_large = utilities.mergefunctions(separated_peaks_functions)

    return numpy.interp(s, s_large, bkg + I_large)

def functionNPeaks_lmfit(params, s, I):
    params_for_each_peak = []
    n_peaks = Global.n_peaks
    latticeparam = params["lattice_parameter"]
    for index in range(n_peaks):
        params_for_each_peak.append(
            [params["lattice_parameter"], params["I{}".format(index+1)],
             params["sigma"], params["mu"],
             params["a"], params["b"],
             params["A"], params["B"],
             params["U"], params["V"],
             params["W"], params["aa"],
             params["bb"], params["cc"],
             params["wavelength"]]
        )

    bkg = params["bkg"]

    separated_peaks_functions = []

    for index in range(n_peaks):
        h, k, l = Global.hkl_list[index]

        sanalitycal, Ianalitycal = createonepeak_with_instrumental(params_for_each_peak[index], h, k, l)
        sanalitycal += utilities.s_hkl(latticeparam, h, k, l)

        separated_peaks_functions.append([sanalitycal, Ianalitycal])

    s_large, I_large = utilities.mergefunctions(separated_peaks_functions)

    return I - numpy.interp(s, s_large, bkg + I_large)