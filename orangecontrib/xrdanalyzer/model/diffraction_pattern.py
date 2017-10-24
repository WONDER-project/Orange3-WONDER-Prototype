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

        return 2*numpy.cos(numpy.radians(twotheta/2))/wavelength

    @classmethod
    def _get_twotheta_from_s(cls, s, wavelength):
        if s is None: return None

        return numpy.degrees(2*numpy.arccos(s*wavelength/2))

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

    def add_diffraction_point (self, diffraction_point = DiffractionPoint(twotheta=0.0, intensity=0.0)):
        if diffraction_point is None: raise ValueError ("Diffraction Point is None")
        if not isinstance(diffraction_point, DiffractionPoint): raise ValueError ("diffraction point should be of type Diffraction Point")

        if self.diffraction_pattern is None:
            self.diffraction_pattern = numpy.array([diffraction_point])
        else:
            self.diffraction_pattern.append(diffraction_point)

    def set_diffraction_point(self, index = 0, diffraction_point = DiffractionPoint(twotheta=0.0, intensity=0.0)):
        self._check_diffraction_pattern()
        self.diffraction_pattern[index] = diffraction_point

    def set_diffraction_points (self, diffraction_pattern = numpy.array([None] *0)):
        self.diffraction_pattern = diffraction_pattern

    def diffraction_points_count(self):
        return 0 if self.diffraction_pattern is None else len(self.diffraction_pattern)

    def get_diffraction_point(self, index):#
        self._check_diffraction_pattern()
        return self.diffraction_pattern[index]

    def set_wavelength(self, wavelength):
        self._check_wavelength()
        self.wavelength = wavelength

    def get_wavelength(self):
        self._check_wavelength()
        return self.wavelength

    def matrix(self):
        Npoints = self.diffraction_points_count()
        matrix = numpy.array([None] * Npoints )
        for index in range(0, Npoints):
            matrix[index] = \
                        self.get_diffraction_point(index).get_array()
    # "PRIVATE METHODS"
    def _check_diffraction_pattern(self):
        if self.diffraction_pattern is None:
            raise AttributeError("diffraction pattern is "
                                 "not initialized")
    def _check_wavelength (self):
        if self.wavelength is None:
            raise AttributeError ("Wavelength (lambda) "
                                  "is not initialized")




# ----------------------------------------------------
#  FACTORY METHOD
# ----------------------------------------------------

class DiffractionPatternFactory:
    @classmethod
    def create_diffraction_pattern_from_file(clscls, file_name):
        return DiffractionPatternFactoryChain.Instance().create_diffraction_pattern_from_file(file_name)

import os

# ----------------------------------------------------
#  CHAIN OF RESPONSABILITY
# ----------------------------------------------------

class DiffractionPatternFactoryInterface():
    def create_diffraction_pattern_from_file(self, file_name):
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

    def create_diffraction_pattern_from_file(self, file_name):
        file_extension = self._get_extension(file_name)

        for handler in self._chain_of_handlers:
            if handler.is_handler(file_extension):
                return handler.create_diffraction_pattern_from_file(file_name)

        raise ValueError ("File Extension not recognized")

    def _get_handlers_list(self):
        classes = numpy.array([m[0] for m in inspect.getmembers(sys.modules[__name__], predicate)])

        return numpy.asarray(classes[numpy.where(classes !=
                                                 "DiffractionPatternFactoryHandler")])

# ---------------------------------------------------
# HANDLERS INTERFACE
# ---------------------------------------------------

class DiffractionPatternFactoryHandler (DiffractionPatternFactoryInterface):

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

    def create_diffraction_pattern_from_file(self, file_name):
        return DiffractionPatternXye(file_name = file_name)

class DiffractionPatternRawFactoryHandler(DiffractionPatternFactoryHandler):

    def _get_handled_extension(self):
        return ".raw"

    def create_diffraction_pattern_from_file(self, file_name):
        return DiffractionPatternRaw(file_name= file_name)


# ----------------------------------------------------
# PERSISTENCY MANAGAMENT
# ----------------------------------------------------

class DiffractionPatternXye(DiffractionPattern):
    def __init__(self, file_name= ""):
        super(DiffractionPatternXye, self).__init__(n_points = 0)

        self.__initialize_from_file(file_name)

    def __initialize_from_file(self, file_name):
        #method supposes only 2 rows of header are present
        #can be changed. Right now i want to finish
        with open(file_name, 'r') as xyefile : lines = xyefile.readlines()
        n_points = len(lines) - 2
        if n_points > 0:
            if len(lines) < 3: raise Exception("Number of lines in file < 3: wrong file format")
            self.diffraction_pattern = numpy.array([None] *n_points)

            for i in numpy.arange(2, n_points+2):
                line = lines[i].split()

                if len(lines) < 2 : raise  Exception("Number of columns in line " + str(i) + " < 2: wrong file format")

                point = DiffractionPoint(twotheta=float(line[0]), intensity=float(line[1]))

                self.set_diffraction_point(index=i-2,diffraction_point= point)



class DiffractionPatternRaw(DiffractionPattern):
    def __init__(self, file_name= ""):
        super(DiffractionPatternRaw, self).__init__(n_points = 0)

        self.__initialize_from_file(file_name)

    def __initialize_from_file(self, file_name):
        #method supposes only 1 rows of header is present
        #can be changed.
        with open(file_name, 'r') as rawfile : lines = rawfile.readlines()

        splitted_row = lines[1].split(sep=',')
        n_points = int(splitted_row[0])
        step = float(splitted_row[1])
        starting_theta = float(splitted_row[2])

        self.wavelength = float(splitted_row[3])
        self.diffraction_pattern = numpy.array([None] *n_points)

        for i in numpy.arange(2, n_points+2):
            index = i-2
            line = lines[i]

            point = DiffractionPoint(twotheta=starting_theta + step*index,
                                     intensity=float(line),
                                     wavelength=self.wavelength)

            self.set_diffraction_point(index, diffraction_point= point)