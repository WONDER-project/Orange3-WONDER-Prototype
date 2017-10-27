from orangecontrib.xrdanalyzer import Singleton, synchronized_method
from orangecontrib.xrdanalyzer.util import congruence

@Singleton
class FitterListener():
    registered_fit_global_parameters = None
    space_parameters = None
    specific_fitter_data = None

    @synchronized_method
    def register_fit_global_parameters(self, fit_global_parameters = None):
        self.registered_fit_global_parameters = fit_global_parameters
        self.space_parameters = fit_global_parameters.space_parameters()

    @synchronized_method
    def register_specific_fitter_data(self, specific_fitter_data=None):
        self.specific_fitter_data = specific_fitter_data
    
    def get_registered_fit_global_parameters(self):
        return self.registered_fit_global_parameters

    def get_registered_space_parameters(self):
        return self.space_parameters
    
    def get_registered_specific_fitter_data(self):
        return self.specific_fitter_data


class FitterInterface:

    def __init__(self):
        pass

    def do_fit(self, fit_global_parameters=None, n_iterations=1):
        congruence.checkStrictlyPositiveNumber(n_iterations, "Number of Iterations")

        FitterListener.Instance().register_fit_global_parameters(fit_global_parameters)

        return self.do_specific_fit(fit_global_parameters, n_iterations)

    def do_specific_fit(self, fit_global_parameters, n_iterations):
        raise NotImplementedError("Abstract")

