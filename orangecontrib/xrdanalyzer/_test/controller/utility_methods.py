import numpy
import itertools
import operator

from orangecontrib.xrdanalyzer._test.controller.fftparameters import Global


#utiliies will be moved somewhere else
class utilities:

    @classmethod
    def Hinvariant(cls, h, k, l):
        numerator = (h * h * k * k + k * k * l * l + l * l * h * h)
        denominator = (h * h + k * k + l * l) ** 2
        return numerator / denominator

    @classmethod
    def s_hkl(cls, a, h, k, l):
        return numpy.sqrt(h * h + k * k + l * l) / a

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
    def is_even(cls,a):
        if (a & 1) == 0:
            return True
        else:
            return False

    @classmethod
    def is_odd(cls, a):
        return not cls.is_even(a)

    @classmethod
    def satisfyselectionrule_fcc(cls,a, b, c):
        if (cls.is_even(a) and cls.is_even(b) and cls.is_even(c)):
            return True
        elif (cls.is_odd(a) and cls.is_odd(b) and cls.is_odd(c)):
            return True
        else:
            return False

    @classmethod
    def satisfyselectionrule_bcc(cls, a, b, c):
        if cls.is_even(a + b + c):
            return True
        else:
            return False

    @classmethod
    def firstpeaks(cls, latticepar, cube, howmany):
        dist_and_hkl = dict()
        listofhkl = set()
        if cube == "fcc":
            satisfyselectionrule = cls.satisfyselectionrule_fcc
        elif cube == "bcc":
            satisfyselectionrule = cls.satisfyselectionrule_bcc
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
                                dist_and_hkl['{} {} {}'.format(perma[0], perma[1], perma[2])] \
                                    = cls.s_hkl(latticepar, h, k,l)

        distances = []
        for key, value in dist_and_hkl.items():
            distances.append([key, value])

        distances = sorted(distances, key=operator.itemgetter(1))
        distances_selected = [distances[i] for i in range(0, howmany)]
        return distances_selected

    @classmethod
    def mergefunctions(cls, listofpairs):
        # x step must be the same for all functions
        super_s = numpy.linspace(0, 4 * Global.Smax, Global.n_steps)
        super_I = numpy.zeros(Global.n_steps)

        for function in listofpairs:
            super_I += numpy.interp(super_s, function[0], function[1])

        return super_s, super_I




