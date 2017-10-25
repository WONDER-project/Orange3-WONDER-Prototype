from orangecontrib.xrdanalyzer import Singleton, synchronized_method

@Singleton
class FitterListener():

    registered_fit_global_parameters = None

    @synchronized_method
    def register_fit_global_parameters(self, fit_global_parameters = None):
        self.registered_fit_global_parameters = fit_global_parameters

    @synchronized_method
    def get_registered_fit_global_parameters(self):
        return self.registered_fit_global_parameters