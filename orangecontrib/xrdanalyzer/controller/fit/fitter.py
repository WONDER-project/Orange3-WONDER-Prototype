from orangecontrib.xrdanalyzer import Singleton, synchronized_method
from orangecontrib.xrdanalyzer.util import congruence

@Singleton
class FitterListener():
    registered_fit_global_parameters = None
    space_parameters = None

    @synchronized_method
    def register_fit_global_parameters(self, fit_global_parameters = None):
        self.registered_fit_global_parameters = fit_global_parameters
        self.space_parameters = fit_global_parameters.space_parameters()

    def get_registered_fit_global_parameters(self):
        return self.registered_fit_global_parameters

    def get_registered_space_parameters(self):
        return self.space_parameters

class FitterInterface:

    def __init__(self):
        pass

    def do_fit(self, fitter_view_listener, fit_global_parameters=None, n_iterations=1):
        congruence.checkStrictlyPositiveNumber(n_iterations, "Number of Iterations")

        FitterListener.Instance().register_fit_global_parameters(fit_global_parameters)

        return self.do_specific_fit(fitter_view_listener, fit_global_parameters, n_iterations)

    def do_specific_fit(self, fit_global_parameters, n_iterations):
        raise NotImplementedError("Abstract")

