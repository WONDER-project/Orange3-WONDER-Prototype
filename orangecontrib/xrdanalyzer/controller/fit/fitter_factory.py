#from orangecontrib.xrdanalyzer.controller.fit.fitters.old.fitter_lmfit import FitterLmfit
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_scipy import FitterScipy
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack import FitterMinpack

import orangecontrib.xrdanalyzer.util.congruence as congruence

class FitterName:
    SCIPY = "scipy"
    LMFIT = "lmfit"
    MINPACK  = "minpack"

    @classmethod
    def tuple(cls):
        return [cls.MINPACK]#, cls.SCIPY]#, cls.LMFIT]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK, fitting_method=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        elif fitter_name == FitterName.SCIPY:
            return FitterScipy()
        #elif fitter_name == FitterName.LMFIT:
        #    return FitterLmfit(fitting_method=fitting_method)
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
