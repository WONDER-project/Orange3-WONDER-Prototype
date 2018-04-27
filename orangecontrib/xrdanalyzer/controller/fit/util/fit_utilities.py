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
    def theta(cls, s, wavelength):
        return numpy.arcsin(s * wavelength / 2)

    @classmethod
    def s(cls, theta, wavelength):
        return 2*numpy.sin(theta)/wavelength

    @classmethod
    def theta_hkl (cls, a, h, k, l , wavelength):
        return numpy.arcsin(cls.s_hkl(a, h, k, l) * wavelength / 2)

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



import operator
import itertools
import math
import numpy

def is_even(a):
    return a % 2 == 0

def is_odd(a):
    return a % 2 == 1

def is_fcc(h, k, l):
    if (is_even(h) and is_even(k) and is_even(l)):
        return True
    elif (is_odd(h) and is_odd(k) and is_odd(l)):
        return True
    else:
        return False


def is_bcc(h, k, l):
    if is_even(h+k+l):
        return True
    else:
        return False


def hkl_gcd(hkl_list):
    h, k, l = hkl_list
    return math.gcd(math.gcd(h,k), l)

def simplify_hkl(hkl_list):
    return [i/hkl_gcd(hkl_list) for i in hkl_list]

def list_of_s_bragg(n_peaks, lattice_param, cell_type):
    if cell_type == 'fcc':
        s_list = []
        possible_indeces = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for h, k, l in itertools.combinations_with_replacement(possible_indeces, 3):
            if is_fcc(h, k, l):
                s_list.append([[h, k, l], numpy.sqrt(h ** 2 + k ** 2 + l ** 2) / lattice_param])

        s_list = sorted(s_list, key=operator.itemgetter(1))
        for listina in s_list:
            listina[0] = sorted(listina[0], reverse=True)
        s_list.pop(0)
        return s_list[0:n_peaks]

    elif cell_type == 'bcc':
        s_list = []
        possible_indeces = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for h, k, l in itertools.combinations_with_replacement(possible_indeces, 3):
            if is_bcc(h, k, l):
                s_list.append([[h, k, l], numpy.sqrt(h ** 2 + k ** 2 + l ** 2) / lattice_param])

        s_list = sorted(s_list, key=operator.itemgetter(1))
        for listina in s_list:
            listina[0] = sorted(listina[0], reverse=True)
        s_list.pop(0)
        return s_list[0:n_peaks]
    else:
        return []


print(list_of_s_bragg(10, 3.89, 'bcc'))