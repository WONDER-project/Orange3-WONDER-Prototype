from orangecontrib.xrdanalyzer import Singleton, synchronized_method

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

    def init_fitter(self, fit_global_parameters=None):
        raise NotImplementedError("Abstract")

    def do_fit(self, fit_global_parameters=None, current_iteration=0):
        FitterListener.Instance().register_fit_global_parameters(fit_global_parameters)

        return self.do_specific_fit(fit_global_parameters, current_iteration)

    def do_specific_fit(self, fit_global_parameters, current_iteration):
        raise NotImplementedError("Abstract")

    def finalize_fit(self):
        raise NotImplementedError("Abstract")


