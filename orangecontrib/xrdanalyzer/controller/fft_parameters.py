from orangecontrib.xrdanalyzer.util import congruence


class FFTInitParameters:

    s_max = 9.0
    n_step = 4096

    def __init__(self, s_max = 9.0, n_step = 4096):
        congruence.checkStrictlyPositiveNumber(s_max, "S_max")
        congruence.checkStrictlyPositiveNumber(n_step, "N_step")

        if not ((n_step & (n_step - 1)) == 0): raise ValueError("N_step should be a power of 2")

        self.s_max = s_max
        self.n_step = n_step

