from orangecontrib.xrdanalyzer import is_recovery

if not is_recovery:
    from orangecontrib.xrdanalyzer.util import congruence
    from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import Boundary, FitParameter, FitParametersList
else:
    from orangecontrib.xrdanalyzer.recovery.util import congruence
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fit_parameter import Boundary, FitParameter, FitParametersList


class ThermalPolarizationParameters(FitParametersList):

    debye_waller_factor = None
    use_lorentz_factor = True
    use_polarization_factor = True
    twotheta_mono = None

    def __init__(self,
                 debye_waller_factor = FitParameter(parameter_name="B", value=1e-1, boundary=Boundary(min_value=0.0)),
                 use_lorentz_factor = False,
                 use_polarization_factor=False,
                 twotheta_mono=None):
        self.debye_waller_factor = debye_waller_factor
        self.use_lorentz_factor = use_lorentz_factor
        self.use_polarization_factor = use_polarization_factor
        self.twotheta_mono = twotheta_mono

    @classmethod
    def get_parameters_prefix(cls):
        return "tp_"

    def duplicate(self):
        return ThermalPolarizationParameters(debye_waller_factor=None if self.debye_waller_factor is None else self.debye_waller_factor.duplicate(),
                                             use_lorentz_factor=self.use_lorentz_factor,
                                             use_polarization_factor=self.use_polarization_factor,
                                             twotheta_mono=self.twotheta_mono)

    def to_text(self):
        text = "THERMAL/POLARIZATION PARAMETERS\n"
        text += "-----------------------------------\n"
        text += "B      : " + "" if self.debye_waller_factor is None else self.debye_waller_factor.to_text() + "\n"
        text += "use LF : " + str(self.use_lorentz_factor) + "\n"
        text += "use PF : " + str(self.use_polarization_factor) + "\n"
        if not self.twotheta_mono is None: text += "2th_m : " + str(self.twotheta_mono) + "\n"
        text += "-----------------------------------\n"

        return text
