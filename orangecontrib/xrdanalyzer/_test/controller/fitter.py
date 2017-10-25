import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc

import matplotlib.pyplot as plt


from orangecontrib.xrdanalyzer._test.controller.utility_methods import utilities
from orangecontrib.xrdanalyzer._test.controller.fftparameters import *


######################################################################

def fitterScipyCurveFit(function_to_fit,
                        s_experimental,
                        intensity_experimental,
                        listparameters):

    parameters, boundaries = listparameters.to_scipy_tuple()

    popt, pcov = curve_fit(f=function_to_fit,
                           xdata=s_experimental,
                           ydata=intensity_experimental,
                           #sigma=numpy.sqrt(intensity_experimental),
                           p0=parameters,
                           bounds=boundaries)
    return popt, pcov

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

######################################################################
# Peaks Creation
######################################################################

def createonepeak(params, h, k, l):
    latticepar = params[0]
    Amplitude = params[1]
    sigma = params[2]
    mu = params[3]
    a = params[4]
    b = params[5]
    A = params[6]
    B = params[7]

    L = numpy.linspace(Global.dL, Global.Lmax + Global.dL, Global.n_steps)

    #function_in_L = sizeFunctionCommonvolume(L,D)
    lognormalfunction = sizeFunctionLognormal(L, sigma, mu)
    strainfunction = strainFunction(L, h, k, l, latticepar, a, b, A, B)

    s, I = fft(lognormalfunction*strainfunction)
    #s, I = fft(strainfunction)
    #s, I = fft(lognormalfunction)

    return s, Amplitude*I


def functionOfThePeak(s, *params):
    h, k, l = 1,1,0

    bkg = params[8]

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