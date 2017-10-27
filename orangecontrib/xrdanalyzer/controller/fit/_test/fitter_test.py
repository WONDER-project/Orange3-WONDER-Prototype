
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternLimits, DiffractionPatternFactory

from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterListener, FitterInterface, FitterFactory

if __name__=="__main__":
    filename = "/Users/admin/Documents/workspace/Alberto_Flor/Orange3-Flor/Examples/FeMo_Batch4_GiaraA_1_HQ.xye"
    #filename = "C:\\Users\\alber\\Documents\\Workspace\\Orange\\Orange3-Flor\\Examples\\FeMo_Batch4_GiaraA_1_HQ.xye"
    wavelength = 0.0826# nm

    crystal_structure = CrystalStructure.init_cube(a0=FitParameter(value=0.2873, fixed=True), simmetry=Simmetry.BCC)
    crystal_structure.add_reflection(Reflection(1, 1, 0, intensity=FitParameter(value=1000.0, boundary=Boundary(min_value=100, max_value=20000.0))))

    fit_initialization = FitInitialization(diffraction_pattern=DiffractionPatternFactory.create_diffraction_pattern_from_file(file_name=filename,
                                                                                                                              wavelength=wavelength,
                                                                                                                              limits=DiffractionPatternLimits(twotheta_min=20,
                                                                                                                                                              twotheta_max=27)),
                                           crystal_structure=crystal_structure,
                                           fft_parameters=FFTInitParameters(s_max=9.0, n_step=8192))

    size_parameters = SizeParameters(shape=Shape.SPHERE,
                                     distribution=Distribution.LOGNORMAL,
                                     mu=FitParameter(value=2.1711, boundary=Boundary(min_value=0.01, max_value=10.0)),
                                     sigma=FitParameter(value=0.353, boundary=Boundary(min_value=0.01, max_value=0.8)))

    fit_global_parameters = FitGlobalParameters(fit_initialization=fit_initialization,
                                                size_parameters=size_parameters)

    fitter = FitterFactory.create_fitter()

    fit, param = fitter.do_fit(fit_global_parameters)

    tt, I, e, s = fit.tuples()

    print(param.to_text())

    plt.plot(tt, I)
    plt.show()
