import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc


# ==================================
# ==================================
# ""GLOBAL"" variables
class Global:
    Smax =9
    n_steps = pow(2,13)
    ds = Smax/n_steps

    dL = 1 / (2 * Smax)
    Lmax = n_steps * dL
    L = numpy.linspace(dL, Lmax, n_steps)

# ==================================
# ==================================



def fitterScipyCurveFit(function_to_fit,
                        s_experimental,
                        intensity_experimental,
                        listparameters):
    #additional_infos contains information such as S_max,
    #minimization method, or other
    #the s_experimental has variable step, we construct the

    parameters, boundaries = listparameters.to_scipy_tuple()

    popt, pcov = curve_fit(f=function_to_fit,
                           xdata=s_experimental,
                           ydata=intensity_experimental,
                           #sigma=numpy.sqrt(intensity_experimental),
                           p0=parameters,
                           bounds=boundaries)
    return popt, pcov


# -----------------------------------
# FOURIER FUNCTIONS
# -----------------------------------

def Fourier(y, N):
    return numpy.fft.fftshift(numpy.abs(numpy.real(numpy.fft.fft(y)))) / numpy.sqrt(N)


def fft(f):
    N = Global.n_steps
    y_fft = Fourier(f, N)

    q = numpy.fft.fftfreq(N, Global.ds)
    q = numpy.fft.fftshift(q)

    integral = numpy.trapz(y_fft, q)

    return q, y_fft / integral


def createonepeak(params):
    Amplitude = params[0]
    D = params[1]
    mu = params[2]
    latticepar = params[3]
    a = params[4]
    b = params[5]
    A = params[6]
    B = params[7]

    h, k , l = 2, 2, 0
    L = numpy.linspace(Global.dL, Global.Lmax, Global.n_steps)
    #function_in_L = sizeFunctionCommonvolume(L,D)
    lognormalfunction = sizeFunctionLognormal(L, D, mu)
    strainfunction = strainFunction(L, h, k, l, latticepar,
                                    a, b, A, B)


    s, I = fft(lognormalfunction*strainfunction)

    return s, Amplitude*I

def functionOfThePeak(s, *params):
    swrong, Iwrong = createonepeak(params)
    I = numpy.interp(s, swrong, Iwrong)
    return I

# --------------------------------
# Functions in L space
# --------------------------------
def sizeFunctionCommonvolume (L, D):
    LfracD = L/D
    return 1 - 1.5*LfracD + 0.5*LfracD**3


def sizeFunctionLognormal(L, sigma, mu):
    #L is supposed always positive
    lnL = numpy.log(L)
    sqrt2 = numpy.sqrt(2)
    a = 0.5*erfc((lnL - mu -3*sigma*sigma)/(sigma*sqrt2))
    b = -0.75*L*erfc((lnL - mu -2*sigma*sigma)/(sigma*sqrt2))\
                *numpy.exp(-mu - 2.5*sigma*sigma)
    c = 0.25*L*L*L*erfc((lnL - mu)/(sigma*sqrt2)) \
                *numpy.exp(-3*mu - 4.5*sigma*sigma)

    return  a + b + c

def strainFunction (L, h, k, l, latticepar ,a ,b, A, B):

    shkl = s_hkl(latticepar, h, k, l)
    H = Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -shkl*shkl*C*(a*L + b*L*L)

    return numpy.exp(exponent)


def Hinvariant(h,k,l):
    numerator = (h*h*k*k +k*k*l*l + l*l*h*h)
    denominator = (h*h + k*k + l*l)**2
    return numerator/denominator


def s_hkl(a, h, k, l):
    return numpy.sqrt(h * h + k * k + l * l) / a



# --------------------------------
# FUNCTIONS FOR THE TEST
# --------------------------------
def gaussianpeak_analytical(x, Amplitude, a ,xshift):

    return Amplitude*numpy.exp(-a*(x-xshift)**2)

def gaussianpeak_experimental (x, parameters):

    gaussianpeakfunction = numpy.zeros(numpy.size(x))

    for p in parameters:
        gaussianpeakfunction += numpy.exp(-x*x*p)

    return gaussianpeakfunction


# ================================




