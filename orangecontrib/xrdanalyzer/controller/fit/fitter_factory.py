try:
    import orangecontrib.xrdanalyzer.util.test_recovery
    is_recovery = False
except:
    is_recovery = True

if not is_recovery:
    import orangecontrib.xrdanalyzer.util.congruence as congruence
    from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack import FitterMinpack
else:
    import orangecontrib.xrdanalyzer.recovery.util.congruence as congruence
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fitters.fitter_minpack import FitterMinpack


class FitterName:
    MINPACK  = "minpack"

    @classmethod
    def tuple(cls):
        return [cls.MINPACK]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK, additional_data=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
