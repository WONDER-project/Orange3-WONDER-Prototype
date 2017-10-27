import numpy

class Utilities:

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
