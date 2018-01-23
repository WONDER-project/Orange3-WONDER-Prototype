
import numpy

from orangecontrib.xrdanalyzer import Singleton, synchronized_method

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Simmetry, Reflection
from orangecontrib.xrdanalyzer.util.general_functions import fft

from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary, PARAM_ERR

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface, FitterListener
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_pm2k_util import *
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import create_one_peak


PRCSN = 2.5E-7

class FitterPM2K(FitterInterface):


    def __init__(self):
        super().__init__()

        self.reset()

    def reset(self, fit_global_parameters):
        self.totalWeight = 0.0

        self._lambda	= .001
        self._lmin	= 1E20
        self._totIter	= 0
        self._iter = 0
        self._nincr = 0
        self._phi = 1.2 # relaxation factor

        self.currpar = CVector()
        self.initialpar = CVector()

        self.parameters = fit_global_parameters.get_parameters()
        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        self.twotheta_experimental = twotheta_experimental
        self.intensity_experimental = intensity_experimental
        self.error_experimental = error_experimental
        self.s_experimental = s_experimental

        self.nprm = len(self.parameters)
        self.nfit = self.getNrParamToFit()
        self.nobs = self.getNrPoint()
        #weight = minObjList->getTotalWeight();

        self.a = CTriMatrix()
        self.c = CTriMatrix()
        self.g = CVector()
        self.grad = CVector()

        self.a.setSize(self.nfit)
        self.c.setSize(self.nfit)
        self.g.setSize(self.nfit)
        self.grad.setSize(self.nfit)

        self.currpar = CVector()
        self.initialpar = CVector()

        self.initialpar.setSize(self.nfit)
        self.currpar.setSize(self.nfit)

        self.nincr	= 0 # number of increments in lambda
        self.wss = self.getWSSQ()
        self.oldwss  = self.wss

        self.conver = False
        self.exitflag  = False

        j = 0
        for  i in range (0, self.nprm):
            parameter = self.parameters[i]

            if not parameter.fixed and not parameter.function:
                j += 1
                self.initialpar.setitem(j, parameter.value)

        self.mighell = False

    def do_specific_fit(self, fit_global_parameters):

        # check values of lambda for large number of iterations
        if (self._totIter > 4 and self._lambda < self._lmin): self._lmin = self._lambda

        #update total number of iterations
        self._totIter += 1

        #decrease lambda using golden section 0.31622777=1/(sqrt(10.0))
        self._lambda *= 0.31622777

        #number of increments in lambda
        self._nincr = 0

        #zero the working arrays
        self.a.zero()
        self.grad.zero()

        fmm = self.getWeightedDelta()
        deriv = self.getDerivative()

        for i in range(1, self.getNrPoint() + 1):
            for jj in range(1, self.nfit + 1):

                l = int(jj*(jj-1)/2)
                self.grad.setitem(jj, self.grad.getitem(jj) + deriv.getitem(jj, i)*fmm[i-1])

                for k in range(1, jj+1):
                    self.a.setitem(l+k, self.a.getitem(i) + deriv.getitem(jj,i)*deriv.getitem(k,i))

        self.c.assign(self.a) #save the matrix A and the current value of the parameters

        j = 0
        for  i in range (0, self.nprm):
            parameter = self.parameters[i]

            if not parameter.fixed and not parameter.function:
                j += 1
                self.initialpar.setitem(j, parameter.value)
                self.currpar.setitem(j, self.initialpar.getitem(j))

        # emulate C++ do ... while cycle
        do_cycle = True
        while do_cycle:
            self.exitflag = False
            self.conver = False

            #set the diagonal of A to be A*(1+lambda)+phi*lambda
            da = self._phi*self._lambda

            for jj in range(1, self.nfit+1):
                self.g.setitem(jj, -self.grad.getitem(jj))
                l = jj*(jj+1)/2
                self.a.setitem(l, self.c.getitem(l)*(1.0 + self._lambda) + da)
                if jj > 1:
                    for i in range (1, jj+1):
                        self.a.setitem(l-i, self.c.getitem(l-i))

            if self.a.chodec() == 0: # Cholesky decomposition
                # the matrix is inverted, so calculate g (change in the
				# parameters) by back substitution
                self.a.choback(self.g)

                recyc = False
                prevwss = self.oldwss
                recycle = 1

                # Update the parameters: param = old param + g
				# n0 counts the number of zero elements in g
                do_cycle = True
                while do_cycle:
                    recyc = False
                    n0 = 0
                    i = 0
                    for j in range(0, self.nprm):
                        parameter = self.parameters[j]

                        if not parameter.fixed and not parameter.function:
                            i += 1

                            # update value of parameter
                            self.parameters[j].value = self.currpar.get_item(i) + recycle*self.g.get_item(i)
                            #  apply the required constraints (min/max)
                            self.parameters[j].check_value()

                            # check number of parameters reaching convergence
                            if (abs(self.g.getitem(i))<=abs(PRCSN*self.currpar.getitem(i))): n0 += 1

                    if (n0==self.nfit): self.conver = True

                    # update the wss
                    self.wss = self.getWSSQ()

                    if self.wss < prevwss:
                        prevwss = self.wss
                        recyc = True
                        recycle += 1

                    # last line of while loop
                    do_cycle = recyc and recycle<10

                if recycle > 1:

                    # restore parameters to best value
                    recycle -= 1

                    i = 0
                    for j in range(0, self.nprm):
                        parameter = self.parameters[j]

                        if not parameter.fixed and not parameter.function:
                            i += 1

                            # update value of parameter
                            self.parameters[j].value = self.currpar.get_item(i) + recycle*self.g.get_item(i)
                            #  apply the required constraints (min/max)
                            self.parameters[j].check_value()

                    # update the wss
                    self.wss = self.getWSSQ()


                # if all parameters reached convergence then it's time to quit

                if self.wss < self.oldwss:
                    self.oldwss     = self.wss

                    self.exitflag   = True

                    ii = 0
                    for j in range(0, self.nprm):
                        parameter = self.parameters[j]

                        if not parameter.fixed and not parameter.function:
                            i += 1

                            # update value of parameter
                            self.initialpar.setitem(ii, self.currpar.get_item(ii) + recycle*self.g.get_item(ii))

                self.wss = self.getWSSQ()

                #TODO
                '''
				ss  = minObjList->getSSQFromData();

				double wsq	= minObjList->getWSQFromData();
				double rwp	= sqrt(wss / wsq);
				double rexp	= sqrt(((double)dof) / wsq);
				double gof	= rwp / rexp;
                '''
            else:
                if not self.exitflag  and not self.conver:
                    if self._lambda<PRCSN: self._lambda = PRCSN
                    self._nincr += 1
                    self._lambda *= 10.0
                    if self._lambda>(1E5*self._lmin): self.conver = True

            # last line of the while loop
            do_cycle =  not self.exitflag  and not self.conver

        j = 0

        for i in range(0, self.nprm):
            parameter = self.parameters[i]

            if not parameter.fixed and not parameter.function:
                j += 1
                self.parameters[i].value = self.initialpar.get_item(j)
                #  apply the required constraints (min/max)
                self.parameters[i].check_value()


        '''
        fitted_parameters = current_parameters


        fit_global_parameters_out = self.build_fit_global_parameters_out(fitted_parameters)

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_intensity = fit_function(s_experimental, fitted_parameters)

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=0.0,
                                                                                    s=s_experimental[index]))

        return fitted_pattern, fit_global_parameters_out
        '''

    def build_fit_global_parameters_out(self, fitted_parameters):
        fit_global_parameters = FitterListener.Instance().get_registered_fit_global_parameters().duplicate()
        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        crystal_structure.a.value = fitted_parameters[0]
        crystal_structure.b.value = fitted_parameters[1]
        crystal_structure.c.value = fitted_parameters[2]
        crystal_structure.alpha.value = fitted_parameters[3]
        crystal_structure.beta.value = fitted_parameters[4]
        crystal_structure.gamma.value = fitted_parameters[5]

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            crystal_structure.get_reflection(reflection_index).intensity.value = fitted_parameters[6+reflection_index]

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameters.background_parameters is None:
            fit_global_parameters.background_parameters.c0.value = fitted_parameters[last_index + 1]
            fit_global_parameters.background_parameters.c1.value = fitted_parameters[last_index + 2]
            fit_global_parameters.background_parameters.c2.value = fitted_parameters[last_index + 3]
            fit_global_parameters.background_parameters.c3.value = fitted_parameters[last_index + 4]
            fit_global_parameters.background_parameters.c4.value = fitted_parameters[last_index + 5]
            fit_global_parameters.background_parameters.c5.value = fitted_parameters[last_index + 6]

            last_index += fit_global_parameters.background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            fit_global_parameters.instrumental_parameters.U.value = fitted_parameters[last_index + 1]
            fit_global_parameters.instrumental_parameters.V.value = fitted_parameters[last_index + 2]
            fit_global_parameters.instrumental_parameters.W.value = fitted_parameters[last_index + 3]
            fit_global_parameters.instrumental_parameters.a.value = fitted_parameters[last_index + 4]
            fit_global_parameters.instrumental_parameters.b.value = fitted_parameters[last_index + 5]
            fit_global_parameters.instrumental_parameters.c.value = fitted_parameters[last_index + 6]

            last_index += fit_global_parameters.instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            fit_global_parameters.size_parameters.mu.value    = fitted_parameters[last_index + 1]
            fit_global_parameters.size_parameters.sigma.value = fitted_parameters[last_index + 2]

            last_index += fit_global_parameters.size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            fit_global_parameters.strain_parameters.aa.value = fitted_parameters[last_index + 1]
            fit_global_parameters.strain_parameters.bb.value = fitted_parameters[last_index + 2]
            fit_global_parameters.strain_parameters.e1.value = fitted_parameters[last_index + 3] # in realtà è E1 dell'invariante PAH
            fit_global_parameters.strain_parameters.e6.value = fitted_parameters[last_index + 4] # in realtà è E6 dell'invariante PAH

            last_index += fit_global_parameters.strain_parameters.get_parameters_count()

        return fit_global_parameters


    def getNrPoint(self):
        return len(self.twotheta_experimental)

    def getNrParamToFit(self):
        nfit = 0
        for parameter in self.parameters:
            if not parameter.fixed and not parameter.function:
                nfit += 1
        return nfit


    def setStep(self, step):
        self.y = numpy.zeros(self.np)
        self.fmm = numpy.zeros(self.np)


    # METODI minObj

    def getWeightedDelta(self):
        y = fit_function(self.parameters, self.s_experimental)

        fmm = numpy.zeros(self.getNrPoint())

        for i in range (0, self.getNrPoint()):
            if self.error_experimental[i] == 0:
                fmm[i] = 0
            else:
                fmm[i] = (y[i] - self.intensity_experimental[i])/self.error_experimental[i]


        return fmm


    def getDerivative(self):
        y = fit_function(self.parameters, self.s_experimental)

        deriv = CMatrix(self.getNrParamToFit())

        jj = 0
        for k in range (0, self.nprm):
            parameter = self.parameters[k]

            if not parameter.fixed:
                pk = parameter.value
                if parameter.step == PARAM_ERR: step = 0.001
                else: step = parameter.step

                if abs(pk) > PRCSN:
                    d = pk*step
                    parameter.value = k * (1.0 + step)
                    parameter.check_value()

                    deriv[jj] = fit_function(self.s_experimental, self.parameters)
                else:
                    d = step
                    parameter.value = pk + d
                    parameter.check_value()

                    deriv[jj] = fit_function(self.s_experimental, self.parameters)

                parameter.value = pk
                parameter.check_value()

                for i in range(0, len(y)):
                    if self.error_experimental[i] == 0:
                        deriv[jj][i] = 0.0
                    else:
                        deriv[jj][i] = (deriv[jj][i] - y[i]) / (d * self.error_experimental[i])
                jj += 1

        return deriv

    def getWSSQ(self):
        y = fit_function(self.parameters, self.s_experimental)

        wssq = 0.0
        wssqlow = 0.0

        if self.mighell:
            for i in range(0, self.getNrPoint()):
                tmp = self.intensity_experimental[i]
                if tmp < 1:
                    yv = y[i] - 2*self.intensity_experimental[i]
                else:
                    yv = y[i] - (self.intensity_experimental[i] + 1.0)

                wssqtmp = (yv**2)/(self.error_experimental[i]**2+1.0)

                if (wssqtmp<1E-2):
                    wssqlow += wssqtmp
                else:
                    wssq    += wssqtmp
        else:
            for i in range(0, self.getNrPoint()):
                if self.error_experimental[i] == 0.0:
                    yv = 0.0
                else:
                    yv = y[i] - (self.intensity_experimental[i]/self.error_experimental[i])

                    wssqtmp = (yv**2)

                    if (wssqtmp<1E-2):
                        wssqlow += wssqtmp
                    else:
                        wssq    += wssqtmp

        return wssq + wssqlow


class CommonFittingData():

    def __init__(self, parameters):
        fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
        crystal_structure = fit_global_parameter.fit_initialization.crystal_structure

        self.lattice_parameter = parameters[0]

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameter.background_parameters is None:
            self.c0 = parameters[last_index + 1]
            self.c1 = parameters[last_index + 2]
            self.c2 = parameters[last_index + 3]
            self.c3 = parameters[last_index + 4]
            self.c4 = parameters[last_index + 5]
            self.c5 = parameters[last_index + 6]

            last_index += fit_global_parameter.background_parameters.get_parameters_count()

        if not fit_global_parameter.instrumental_parameters is None:
            self.U = parameters[last_index + 1]
            self.V = parameters[last_index + 2]
            self.W = parameters[last_index + 3]
            self.a = parameters[last_index + 4]
            self.b = parameters[last_index + 5]
            self.c = parameters[last_index + 6]

            last_index += fit_global_parameter.instrumental_parameters.get_parameters_count()

        if not fit_global_parameter.size_parameters is None:
            self.mu    = parameters[last_index + 1]
            self.sigma = parameters[last_index + 2]

            last_index += fit_global_parameter.size_parameters.get_parameters_count()

        if not fit_global_parameter.strain_parameters is None:
            self.aa = parameters[last_index + 1]
            self.bb = parameters[last_index + 2]
            self.A = parameters[last_index + 3] # in realtà è E1 dell'invariante PAH
            self.B = parameters[last_index + 4] # in realtà è E6 dell'invariante PAH

            last_index += fit_global_parameter.strain_parameters.get_parameters_count()

        self.last_index = last_index

    @classmethod
    def get_amplitude(cls, parameters, reflection_index):
        return parameters[6 + reflection_index]


#################################################
#
# FIT FUNCTION
#
#################################################

def fit_function(s, *parameters):

    if len(parameters) == 1:
        parameters = parameters[0]

    fit_global_parameter = FitterListener.Instance().get_registered_fit_global_parameters()
    common_fitting_data = CommonFittingData(parameters)

    if CrystalStructure.is_cube(fit_global_parameter.fit_initialization.crystal_structure.simmetry):
        separated_peaks_functions = []

        for reflection_index in range(fit_global_parameter.fit_initialization.crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, parameters, common_fitting_data)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        s_large, I_large = Utilities.merge_functions(separated_peaks_functions,
                                                     fit_global_parameter.fit_initialization.fft_parameters.s_max,
                                                     fit_global_parameter.fit_initialization.fft_parameters.n_step)

        # TEMPORARY BACKGROUND - to be replaced with proper Chebyshev
        if not fit_global_parameter.background_parameters is None:
            background = numpy.array([common_fitting_data.c0] * len(s_large))
        else:
            background = numpy.zeros(s_large.size)

        return numpy.interp(s, s_large, background + I_large)
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")










