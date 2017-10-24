from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit_parameter import PM2KParametersList

class FFTInitParameters(PM2KParametersList):

    s_max = 9.0
    n_step = 4096

    def __init__(self, s_max = 9.0, n_step = 4096):
        congruence.checkStrictlyPositiveNumber(s_max, "S_max")
        congruence.checkStrictlyPositiveNumber(n_step, "N_step")

        if not ((n_step & (n_step - 1)) == 0): raise ValueError("N_step should be a power of 2")

        self.s_max = s_max
        self.n_step = int(n_step)

    def to_PM2K(self):
        text  = "par !ftsteps " + str(self.n_step) + "\n"
        text += "par !smax "  + str(self.s_max) + "\n\n"
        text += "setFTSteps(ftsteps)" + "\n"
        text += "setSMax(smax)"
