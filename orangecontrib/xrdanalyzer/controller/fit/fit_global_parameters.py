
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Caglioti
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAH

class FitGlobalParameters:

    fit_initialization = None
    background_parameters = None
    instrumental_parameters = None
    size_parameters = None
    strain_parameters = None

    def __init__(self,
                 fit_initialization = None,
                 background_parameters = None,
                 instrumental_parameters = None,
                 size_parameters = None,
                 strain_parameters = None):
        self.fit_initialization = fit_initialization
        self.background_parameters = background_parameters
        self.instrumental_parameters = instrumental_parameters
        self.size_parameters = size_parameters
        self.strain_parameters = strain_parameters


    def to_scipy_tuple(self):
        fit_global_parameters = []
        fit_global_boundaries = [[],[]]

        fit_global_parameters, fit_global_boundaries = self.fit_initialization.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)
        fit_global_parameters, fit_global_boundaries = self.background_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)
        fit_global_parameters, fit_global_boundaries = self.instrumental_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)
        fit_global_parameters, fit_global_boundaries = self.size_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)
        fit_global_parameters, fit_global_boundaries = self.strain_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        return fit_global_parameters, fit_global_boundaries


