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
        raise NotImplementedError("Abstract")


#################################################
#
# FIT FUNCTION
#
#################################################

import numpy
from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import create_one_peak, add_chebyshev_background


def fit_function(s, fit_global_parameter):
    if CrystalStructure.is_cube(fit_global_parameter.fit_initialization.crystal_structure.simmetry):
        separated_peaks_functions = []

        for reflection_index in range(fit_global_parameter.fit_initialization.crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, fit_global_parameter)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = Utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        if not fit_global_parameter.background_parameters is None:
            add_chebyshev_background(s_large,
                                     I_large,
                                     parameters=[fit_global_parameter.background_parameters.c0.value,
                                                 fit_global_parameter.background_parameters.c1.value,
                                                 fit_global_parameter.background_parameters.c2.value,
                                                 fit_global_parameter.background_parameters.c3.value,
                                                 fit_global_parameter.background_parameters.c4.value,
                                                 fit_global_parameter.background_parameters.c5.value])

        # TODO: AGGIUNGERE Debye-Waller factors con strutture dati + widget ad hoc

        return numpy.interp(s, s_large, I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")








