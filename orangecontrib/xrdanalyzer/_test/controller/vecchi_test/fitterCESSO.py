import numpy
from scipy.optimize import curve_fit
from scipy.special import erfc
import itertools
import operator
import matplotlib.pyplot as plt



# ==================================
# ==================================
# ""GLOBAL"" variables
class Global:
    Smax = 9.0
    n_steps = pow(2, 13)
    ds = 2*Smax/n_steps

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

    parameters, boundaries = listparameters.tuple()


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


def createonepeak(params, h, k, l):
    latticepar = params[0]
    Amplitude = params[1]
    D = params[2]
    mu = params[3]
    a = params[4]
    b = params[5]
    A = params[6]
    B = params[7]

    L = numpy.linspace(Global.dL, Global.Lmax, Global.n_steps)

    #function_in_L = sizeFunctionCommonvolume(L,D)
    lognormalfunction = sizeFunctionLognormal(L, D, mu)
    #strainfunction = strainFunction(L, h, k, l, latticepar,
     #                               a, b, A, B)


    #s, I = fft(lognormalfunction*strainfunction)
    #s, I = fft(strainfunction)
    s, I = fft(lognormalfunction)

    return s, Amplitude*I

def functionOfThePeak(s, *params):
    swrong, Iwrong = createonepeak(params)
    I = numpy.interp(s, swrong, Iwrong)
    return I

def functionOfManyPeaks(s, *params):
    #all same parameters except  the
    # second one, which is Amplitude
    # one for each peak

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

    unpacked_params = [params_peak1, params_peak2,
                       params_peak3]
    separated_peaks_functions = []

    distances = first3(params[0], "bcc")

    for i in range(0, len(distances)):
        h = int(distances[i][0].split()[0])
        k = int(distances[i][0].split()[1])
        l = int(distances[i][0].split()[2])
        sanalitycal, Ianalitycal = createonepeak(unpacked_params[i], h, k, l)
        sanalitycal += distances[i][1]

        separated_peaks_functions.append([sanalitycal, Ianalitycal])

    super_s = numpy.linspace(0, 4*Global.Smax, Global.n_steps)
    super_I = numpy.zeros(Global.n_steps)

    for function in separated_peaks_functions:
        super_I += numpy.interp(super_s, function[0], function[1])

    return numpy.interp(s, super_s, super_I) + params[-1]

# --------------------------------
# Functions in L space
# --------------------------------
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

    shkl = s_hkl(latticepar, h, k, l)
    H = Hinvariant(h,k,l)
    C = A +B*H*H
    exponent = -2*((numpy.pi*shkl)**2)*C*(a*L + b*L*L)

    return numpy.exp(exponent)


def Hinvariant(h,k,l):
    numerator = (h*h*k*k +k*k*l*l + l*l*h*h)
    denominator = (h*h + k*k + l*l)**2
    return numerator/denominator


def s_hkl(a, h, k, l):
    return numpy.sqrt(h * h + k * k + l * l) / a



# -------------------------------------------
#   SOME UTILITY FUNCTIONS
#   (to be moved somewhere else later)
# -------------------------------------------
def isolate_peak(s, I, smin, smax):
    data = []
    N = numpy.size(s)
    for i in numpy.arange(0, N):
        if s[i] > smin and s[i] < smax:
            data.append([s[i], I[i]])
    output = numpy.asarray(data)
    return output[:, 0], output[:, 1]


def is_even(a):
    if (a & 1 ) == 0:
        return True
    else: return False

def is_odd(a):
    return not is_even(a)

def satisfyselectionrule_fcc(a,b,c):
    if (is_even(a) and is_even(b) and is_even(c)):
        return True
    elif (is_odd(a) and is_odd(b) and is_odd(c)):
        return True
    else: return False


def satisfyselectionrule_bcc(a,b,c):
    if is_even(a + b + c):
        return True
    else: return  False


def simplify(a, b, c, cube):
    #UNUSED
    maxdivisor = numpy.max([a, b, c])
    divisor = maxdivisor

    if cube == "fcc":
        satisfyselectionrule = satisfyselectionrule_fcc
    elif cube == "bcc":
        satisfyselectionrule = satisfyselectionrule_bcc
    else:
        raise ValueError("mona")

    while (divisor > 1):
        if (a / divisor == int(a / divisor) and b / divisor == int(b / divisor) and c / divisor == int(c / divisor)):
            a = a / divisor
            b = b / divisor
            c = c / divisor

            simplify(a, b, c, cube)

        else:
            divisor -= 1

    if (satisfyselectionrule(int(a), int(b), int(c))):
        return (int(a), int(b), int(c))
    else:
        return (int(2 * a), int(2 * b), int(2 * c))

def first3(latticepar, cube):
    dist_and_hkl = dict()
    listofhkl = set()
    if cube == "fcc":
        satisfyselectionrule = satisfyselectionrule_fcc
    elif cube == "bcc":
        satisfyselectionrule = satisfyselectionrule_bcc
    else:
        raise ValueError("mona")

    for h in range(1, 6):
        for k in range(0, 6):
            for l in range(0, 6):
                if satisfyselectionrule(h, k, l):
                    for perma in list(itertools.permutations([h, k, l])):
                        perma = sorted(perma)
                        perma = tuple(perma)
                        if (perma not in listofhkl):
                            dist_and_hkl['{} {} {}'.format(perma[0], perma[1], perma[2])] = s_hkl(latticepar, h, k, l)


    distances = []
    for key, value in dist_and_hkl.items():
        distances.append([key, value])

    distances = sorted(distances, key=operator.itemgetter(1))
    distances3 = [distances[i] for i in range(0, 3)]
    return distances3




def mergefunctions(listofpairs, dx):
    # x step must be the same for all functions
    minx = 10000000
    maxx = -10000000
    for function in listofpairs:
        x = function[0]
        y = function[1]
        if numpy.min(x) < minx: minx = numpy.min(x)
        if numpy.max(x) > maxx: maxx = numpy.max(x)
    newx = numpy.arange(minx, maxx, dx)
    newsize = numpy.size(newx)
    newy = numpy.zeros(newsize)
    startingindex = 0.
    for function in listofpairs:
        x = function[0]
        y = function[1]
        for i in range(0, newsize - 1):
            if (newx[i] <= x[0] and newx[i + 1] > x[0]):
                startingindex = i
        for j in range(0, numpy.size(x) - 1):
            newy[j + startingindex] += y[j]

    return newx, newy

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




