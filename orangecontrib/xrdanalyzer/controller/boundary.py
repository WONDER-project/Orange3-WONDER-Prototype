import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence

class Boundary:

    _min_value = -numpy.inf
    _max_value = numpy.inf

    def __init__(self, min_value = -numpy.inf, max_value = numpy.inf):
        congruence.checkGreaterOrEqualThan(max_value, min_value, "Max Value", "Min Value")

        self._min_value = min_value
        self._max_value = max_value

    def get_max_value(self):
        return self._max_value

    def get_min_value(self):
        return self._min_value