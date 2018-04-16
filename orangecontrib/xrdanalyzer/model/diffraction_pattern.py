import numpy
import inspect

from orangecontrib.xrdanalyzer.util import congruence

#---------------------------------------
# DATA STRUCTURES
#---------------------------------------
class DiffractionPoint:
    twotheta = None
    intensity = None
    error = None
    s = None

    def __init__ (self,
                  twotheta = None,
                  intensity = None,
                  error = None,
                  s = None,
                  wavelength = None):
        self.intensity = intensity
        self.error = error

        if not wavelength is None:
            if twotheta is None:
                self.s = s
                self.twotheta = self._get_twotheta_from_s(s, wavelength)
            elif s is None:
                self.twotheta = twotheta
                self.s = self._get_s_from_twotheta(twotheta, wavelength)
        else:
            self.twotheta = twotheta
            self.s = s

        self._check_attributes_congruence()

    def get_array (self):
        return numpy.array([self.twotheta, self.intensity, self.error, self.s])

    @classmethod
    def _get_s_from_twotheta(cls, twotheta, wavelength):
        if twotheta is None: return None

        return 2*numpy.sin(numpy.radians(twotheta/2))/wavelength

    @classmethod
    def _get_twotheta_from_s(cls, s, wavelength):
        if s is None: return None

        return numpy.degrees(2*numpy.arcsin(s*wavelength/2))

    def _check_attributes_congruence(self):
        if self.s is None:
            congruence.checkPositiveNumber(self.twotheta, "twotheta")
        if self.twotheta is None:
            congruence.checkPositiveNumber(self.s, "s")
        congruence.checkPositiveNumber(self.intensity, "Intensity")

class DiffractionPattern:

    diffraction_pattern = None
    wavelength = None

    def __init__(self, n_points = 0, wavelength = None):
        if n_points > 0:
            self.diffraction_pattern = numpy.array([None]*n_points)
        else:
            self.diffraction_pattern = None
        if not wavelength is None:
            self.wavelength = wavelength
        else:
            self.wavelength = None

    def add_diffraction_point (self, diffraction_point):
        if diffraction_point is None: raise ValueError ("Diffraction Point is None")
        if not isinstance(diffraction_point, DiffractionPoint): raise ValueError ("diffraction point should be of type Diffraction Point")

        if self.diffraction_pattern is None:
            self.diffraction_pattern = numpy.array([self._check_diffraction_point(diffraction_point)])
        else:
            self.diffraction_pattern = numpy.append(self.diffraction_pattern, self._check_diffraction_point(diffraction_point))

    def set_diffraction_point(self, index, diffraction_point):
        self._check_diffraction_pattern()
        self.diffraction_pattern[index] = self._check_diffraction_point(diffraction_point)

    def diffraction_points_count(self):
        return 0 if self.diffraction_pattern is None else len(self.diffraction_pattern)

    def get_diffraction_point(self, index):#
        self._check_diffraction_pattern()

        return self.diffraction_pattern[index]

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength

    def get_wavelength(self):
        self._check_wavelength()
        return self.wavelength

    def matrix(self):
        n_points = self.diffraction_points_count()
        matrix = numpy.array([None] * n_points )
        for index in range(0, n_points):
            matrix[index] = self.get_diffraction_point(index).get_array()

    def tuples(self):
        n_points = self.diffraction_points_count()

        twotheta = numpy.zeros(n_points)
        intensity = numpy.zeros(n_points)
        error = numpy.zeros(n_points)
        s = numpy.zeros(n_points)

        for index in range(n_points):
            diffraction_point = self.get_diffraction_point(index)
            twotheta[index] = diffraction_point.twotheta
            intensity[index] = diffraction_point.intensity
            error[index] = diffraction_point.error
            s[index] = diffraction_point.s

        return twotheta, intensity, error, s

    def duplicate(self):
        self._check_diffraction_pattern()

        diffraction_pattern = DiffractionPattern(wavelength=self.wavelength)
        diffraction_pattern.diffraction_pattern = self.diffraction_pattern

        return diffraction_pattern

    def to_text(self):
        text = "DIFFRACTION PATTERN\n"
        text += "-----------------------------------\n"
        text += "Wavelength: " + str(self.get_wavelength()) + "\n"
        text += "-----------------------------------\n"

        return text

    def get_available_parameters(self):
        return "diffraction_pattern.wavelength = " + str(self.get_wavelength()) + "\n"

    # "PRIVATE METHODS"
    def _check_diffraction_pattern(self):
        if self.diffraction_pattern is None:
            raise AttributeError("diffraction pattern is "
                                 "not initialized")
    def _check_wavelength (self):
        if self.wavelength is None:
            raise AttributeError ("Wavelength (lambda) "
                                  "is not initialized")

    def _check_diffraction_point(self, diffraction_point):
        if not self.wavelength is None:
            if diffraction_point.s is None or diffraction_point.twotheta is None:
                diffraction_point = DiffractionPoint(twotheta=diffraction_point.twotheta,
                                                     intensity=diffraction_point.intensity,
                                                     error=diffraction_point.error,
                                                     s=diffraction_point.s,
                                                     wavelength=self.wavelength)
        return diffraction_point


# ----------------------------------------------------
#  FACTORY METHOD
# ----------------------------------------------------

class DiffractionPatternLimits:
    def __init__(self, twotheta_min = -numpy.inf, twotheta_max = numpy.inf):
        self.twotheta_max = twotheta_max
        self.twotheta_min = twotheta_min


class DiffractionPatternFactory:
    @classmethod
    def create_diffraction_pattern_from_file(clscls, file_name, wavelength=None, limits=None):
        return DiffractionPatternFactoryChain.Instance().create_diffraction_pattern_from_file(file_name, wavelength, limits)

import os

# ----------------------------------------------------
#  CHAIN OF RESPONSABILITY
# ----------------------------------------------------

class DiffractionPatternFactoryInterface():
    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        raise NotImplementedError ("Method is Abstract")

    def _get_extension(self, file_name):
        filename, file_extension = os.path.splitext(file_name)
        return file_extension

from orangecontrib.xrdanalyzer import Singleton
import sys

def predicate(class_name):
    return inspect.isclass(class_name) and issubclass(class_name, DiffractionPatternFactoryHandler)

@Singleton
class DiffractionPatternFactoryChain(DiffractionPatternFactoryInterface):
    _chain_of_handlers = []

    def __init__(self):
        self.initialize_chain()

    def initialize_chain(self):
        self._chain_of_handlers = []

        for handler in self._get_handlers_list():
            self._chain_of_handlers.append((globals()[handler])())

    def append_handler(self, handler = None):
        if self._chain_of_handlers is None: self.initialize_chain()

        if handler is None:
            raise ValueError ("Handler is None")

        if not isinstance(handler, DiffractionPatternFactoryHandler):
            raise ValueError("Handler Type not correct")

        self._chain_of_handlers.append(handler)

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        file_extension = self._get_extension(file_name)

        for handler in self._chain_of_handlers:
            if handler.is_handler(file_extension):
                return handler.create_diffraction_pattern_from_file(file_name, wavelength, limits)

        raise ValueError ("File Extension not recognized")

    def _get_handlers_list(self):
        classes = numpy.array([m[0] for m in inspect.getmembers(sys.modules[__name__], predicate)])

        return numpy.asarray(classes[numpy.where(classes !=
                                                 "DiffractionPatternFactoryHandler")])

# ---------------------------------------------------
# HANDLERS INTERFACE
# ---------------------------------------------------

class DiffractionPatternFactoryHandler(DiffractionPatternFactoryInterface):

    def _get_handled_extension(self):
        raise NotImplementedError()

    def is_handler(self, file_extension):
        return file_extension == self._get_handled_extension()

# ---------------------------------------------------
# HANDLERS
# ---------------------------------------------------

class DiffractionPatternXyeFactoryHandler(DiffractionPatternFactoryHandler):

    def _get_handled_extension(self):
        return ".xye"

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        return DiffractionPatternXye(file_name = file_name, wavelength=wavelength, limits=limits)

class DiffractionPatternRawFactoryHandler(DiffractionPatternFactoryHandler):

    def _get_handled_extension(self):
        return ".raw"

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        return DiffractionPatternRaw(file_name= file_name, limits=limits)


# ----------------------------------------------------
# PERSISTENCY MANAGAMENT
# ----------------------------------------------------

class DiffractionPatternXye(DiffractionPattern):
    def __init__(self, file_name= "", wavelength=None, limits=None):
        super(DiffractionPatternXye, self).__init__(n_points=0, wavelength=wavelength)

        self.__initialize_from_file(file_name, limits)

    def __initialize_from_file(self, file_name, limits):
        #method supposes only 2 rows of header are present
        #can be changed. Right now I want to finish
        with open(file_name, 'r') as xyefile : lines = xyefile.readlines()
        n_points = len(lines) - 2
        if n_points > 0:
            if len(lines) < 3: raise Exception("Number of lines in file < 3: wrong file format")
            if limits is None: self.diffraction_pattern = numpy.array([None] *n_points)

            for i in numpy.arange(2, n_points+2):
                line = lines[i].split()

                if len(line) < 2 : raise  Exception("Number of columns in line " + str(i) + " < 2: wrong file format")

                twotheta = float(line[0])
                intensity = float(line[1])

                if len(line) >= 3:
                    error = float(line[2])
                else:
                    error = numpy.sqrt(intensity)

                if limits is None:
                    self.set_diffraction_point(index=i-2,
                                               diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                  intensity=intensity,
                                                                                  error=error))
                else:

                    if  limits.twotheta_min <= twotheta <= limits.twotheta_max:
                        self.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                      intensity=intensity,
                                                                                      error=error))

class DiffractionPatternRaw(DiffractionPattern):
    def __init__(self, file_name= "", limits=None):
        super(DiffractionPatternRaw, self).__init__(n_points = 0)

        self.__initialize_from_file(file_name, limits)

    def __initialize_from_file(self, file_name, limits):
        #method supposes only 1 rows of header is present
        #can be changed.
        with open(file_name, 'r') as rawfile : lines = rawfile.readlines()

        splitted_row = lines[1].split(sep=',')
        n_points = int(splitted_row[0])
        step = float(splitted_row[1])
        starting_theta = float(splitted_row[2])

        self.wavelength = float(splitted_row[3])
        if limits is None: self.diffraction_pattern = numpy.array([None] *n_points)

        for i in numpy.arange(2, n_points+2):
            index = i-2
            line = lines[i]

            intensity = float(line)
            error = numpy.sqrt(intensity)

            if limits is None:
                self.set_diffraction_point(index,
                                           diffraction_point= DiffractionPoint(twotheta=starting_theta + step*index,
                                                                               intensity=intensity,
                                                                               error=error,
                                                                               wavelength=self.wavelength))
            else:
                twotheta = starting_theta + step*index

                if  limits.twotheta_min <= twotheta <= limits.twotheta_max:
                    self.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                  intensity=intensity,
                                                                                  error=error,
                                                                                  wavelength=self.wavelength))



