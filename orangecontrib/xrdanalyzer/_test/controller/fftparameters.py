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
