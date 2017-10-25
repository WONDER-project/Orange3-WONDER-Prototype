import numpy


# ==================================
# ==================================
# ""GLOBAL"" variables
class Global:
    Smax = 9.0
    n_steps = pow(2, 12)

    ds = Smax/(n_steps-1)
    dL = 1 / (2 * Smax)

    Lmax = (n_steps-1) * dL
    L = numpy.linspace(dL, Lmax+dL, n_steps)

    s_cut_min = 0.

    s_cut_max = 100.

    #hkl_list = [[1,1,0], [2,0,0], [2,1,1], [2, 2, 0], [3,1,0], [2, 2, 2], [3, 2, 1], [4,0,0], [4,1,1], [4,2,0]]
    hkl_list = [[1,1,0], [2,0,0], [2,1,1], [2, 2, 0], [3,1,0]]

    n_peaks = len(hkl_list)


# ==================================
# ==================================
# -----------------------------------
# FOURIER FUNCTIONS
# -----------------------------------

def Fourier(y, N):
    return numpy.fft.fftshift(numpy.abs(numpy.real(numpy.fft.fft(y))))


def fft(f):
    N = Global.n_steps
    y_fft = Fourier(f, N)

    q = numpy.fft.fftfreq(N, Global.dL)
    q = numpy.fft.fftshift(q)

    integral = numpy.trapz(y_fft, q)

    return q, y_fft / integral
