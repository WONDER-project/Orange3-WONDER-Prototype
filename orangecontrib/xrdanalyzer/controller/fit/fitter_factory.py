from orangecontrib.xrdanalyzer.controller.fit.fitter_scipy import FitterScipy
from orangecontrib.xrdanalyzer.controller.fit.fitter_lmfit import FitterLmfit

import orangecontrib.xrdanalyzer.util.congruence as congruence

class FitterName:
    SCIPY = "scipy"
    LMFIT = "lmfit"

    @classmethod
    def tuple(cls):
        return [cls.SCIPY, cls.LMFIT]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.LMFIT, fitting_method=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.SCIPY:
            return FitterScipy()
        elif fitter_name == FitterName.LMFIT:
            return FitterLmfit(fitting_method=fitting_method)


class FitterViewListenerInterface:

    def signal_iteration(self, iteration_number):
        raise NotImplementedError("Abstract")