import numpy

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitGlobalParameters(FitParametersList):

    fit_initialization = None
    background_parameters = None
    instrumental_parameters = None
    size_parameters = None
    strain_parameters = None

    n_max_iterations = 10
    convergence_reached = False

    def __init__(self,
                 fit_initialization = None,
                 background_parameters = None,
                 instrumental_parameters = None,
                 size_parameters = None,
                 strain_parameters = None):
        super().__init__()

        self.fit_initialization = fit_initialization
        self.background_parameters = background_parameters
        self.instrumental_parameters = instrumental_parameters
        self.size_parameters = size_parameters
        self.strain_parameters = strain_parameters

        if not self.fit_initialization is None:
            self.append(self.fit_initialization.get_parameters())
        if not self.background_parameters is None:
            self.append(self.background_parameters.get_parameters())
        if not self.instrumental_parameters is None:
            self.append(self.instrumental_parameters.get_parameters())
        if not self.size_parameters is None:
            self.append(self.size_parameters.get_parameters())
        if not self.strain_parameters is None:
            self.append(self.strain_parameters.get_parameters())

        self.n_max_iterations = 10
        self.convergence_reached = False

    def set_n_max_iterations(self, value=10):
        self.n_max_iterations = value

    def get_n_max_iterations(self):
        return self.n_max_iterations

    def set_convergence_reached(self, value=True):
        self.convergence_reached = value

    def is_convergence_reached(self):
        return self.convergence_reached == True

    def to_scipy_tuple(self):
        fit_global_parameters = []
        fit_global_boundaries = [[],[]]

        if not self.fit_initialization is None:
            fit_global_parameters, fit_global_boundaries = self.fit_initialization.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        if not self.background_parameters is None:
            fit_global_parameters, fit_global_boundaries = self.background_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        if not self.instrumental_parameters is None:
            fit_global_parameters, fit_global_boundaries = self.instrumental_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        if not self.size_parameters is None:
            fit_global_parameters, fit_global_boundaries = self.size_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        if not self.strain_parameters is None:
            fit_global_parameters, fit_global_boundaries = self.strain_parameters.append_to_scipy_tuple(fit_global_parameters, fit_global_boundaries)

        return fit_global_parameters, fit_global_boundaries

    def space_parameters(self):
        return FitSpaceParameters(self)

    def duplicate(self):
        return FitGlobalParameters(fit_initialization=None if self.fit_initialization is None else self.fit_initialization.duplicate(),
                                   background_parameters=None if self.background_parameters is None else self.background_parameters.duplicate(),
                                   instrumental_parameters=None if self.instrumental_parameters is None else self.instrumental_parameters.duplicate(),
                                   size_parameters=None if self.size_parameters is None else self.size_parameters.duplicate(),
                                   strain_parameters=None if self.strain_parameters is None else self.strain_parameters.duplicate())

    def to_text(self):
        
        text = "FIT GLOBAL PARAMETERS\n"
        text += "###################################\n\n"
        
        if not self.fit_initialization is None:
            text += self.fit_initialization.to_text()

        if not self.background_parameters is None:
            text += self.background_parameters.to_text()
            
        if not self.instrumental_parameters is None:
            text += self.instrumental_parameters.to_text()
            
        if not self.size_parameters is None:
            text += self.size_parameters.to_text()

        if not self.strain_parameters is None:
            text += self.strain_parameters.to_text()
        
        text += "\n###################################\n"

        return text
        
class FitSpaceParameters:
    def __init__(self, fit_global_parameters):
        s_max   = fit_global_parameters.fit_initialization.fft_parameters.s_max
        n_steps = fit_global_parameters.fit_initialization.fft_parameters.n_step

        self.ds = s_max/(n_steps - 1)
        self.dL = 1 / (2 * s_max)

        self.L_max = (n_steps - 1) * self.dL
        self.L = numpy.linspace(self.dL, self.L_max + self.dL, n_steps)
