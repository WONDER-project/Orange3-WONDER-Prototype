
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PARAM_ERR
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection, ZeroError
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground, ExpDecayBackground
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAH, WarrenModel, KrivoglazWilkensModel

from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface

try:
    from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_util import *
    from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import fit_function
except:
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fitters.fitter_minpack_util import *
    from orangecontrib.xrdanalyzer.recovery.controller.fit.wppm_functions import fit_function

PRCSN = 2.5E-7

class MinpackData:
    def __init__(self,
                 dof = 0.0,
                 wss = 0.0,
                 ss = 0.0,
                 wsq = 0.0,
                 nobs = 0.0,
                 nprm = 0.0,
                 nfit = 0.0,
                 calc_lambda = 0.0,
                 calculate = True):
        self.dof = dof
        self.wss = wss
        self.ss = ss
        self.wsq = wsq
        self.nprm = nprm
        self.nfit = nfit
        self.nobs = nobs
        self.calc_lambda = calc_lambda

        if calculate: self.calculate()

    def calculate(self):
        try:
            self.rwp  = numpy.sqrt(self.wss / self.wsq)
        except:
            self.rwp = 0.0

        try:
            self.rexp = numpy.sqrt(self.dof / self.wsq)
        except:
            self.rexp = 0.0

    def gof(self):
        return self.rwp / self.rexp

    def to_text(self):
        text = "WSS, SS, WSQ: " + str(self.wss) + ", " + str(self.ss) + ", " + str(self.wsq) + "\n"
        text += "LAMBDA: " + str(self.calc_lambda)+ "\n"
        text += "GOF: " + str(self.gof())+ "\n"
        text += "DOF, NOBS: " + str(self.dof) + ", " + str(self.nobs) + "\n"
        text += "NPARAM, NFIT: " + str(self.nprm) + ", " + str(self.nfit)

        return text

class FitterMinpack(FitterInterface):

    def __init__(self):
        super().__init__()

    def init_fitter(self, fit_global_parameters):
        self.fit_global_parameters = fit_global_parameters

        self.totalWeight = 0.0

        self._lambda	= .001
        self._lmin	= 1E20
        self._totIter	= 0
        self._nincr = 0
        self._phi = 1.2 # relaxation factor

        self.currpar = CVector()
        self.initialpar = CVector()

        # INITIALIZATION OF FUNCTION VALUES

        self.fit_global_parameters.evaluate_functions()

        self.parameters = self.fit_global_parameters.get_parameters()
        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = self.fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        self.twotheta_experimental = twotheta_experimental
        self.intensity_experimental = intensity_experimental
        self.error_experimental = error_experimental
        self.s_experimental = s_experimental

        self.nprm = len(self.parameters)
        self.nfit = self.getNrParamToFit()
        self.nobs = self.getNrPoints()
        self.dof = self.nobs - self.nfit

        self.a = CTriMatrix()
        self.c = CTriMatrix()
        self.g = CVector()
        self.grad = CVector()
        self.currpar = CVector()
        self.initialpar = CVector()

        self.a.setSize(self.nfit)
        self.c.setSize(self.nfit)
        self.g.setSize(self.nfit)
        self.grad.setSize(self.nfit)
        self.initialpar.setSize(self.nfit)
        self.currpar.setSize(self.nfit)

        self.mighell = False

        self.nincr	= 0 # number of increments in lambda
        self.wss = self.getWSSQ()
        self.oldwss  = self.wss

        self.fit_data = MinpackData(wss=self.wss,
                                    dof=self.dof,
                                    nobs=self.nobs,
                                    nprm=self.nprm,
                                    nfit=self.nfit)

        self.conver = False
        self.exitflag  = False

        j = 0
        for  i in range (0, self.nprm):
            parameter = self.parameters[i]

            if parameter.is_variable():
                j += 1
                self.initialpar.setitem(j, parameter.value)

    def do_fit(self, current_fit_global_parameters, current_iteration):
        self.fit_global_parameters = current_fit_global_parameters.duplicate()

        if current_iteration <= current_fit_global_parameters.get_n_max_iterations() and not self.conver:
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

            self.set()

            self.c.assign(self.a) #save the matrix A and the current value of the parameters

            j = 0
            for i in range(0, self.nprm):
                if self.parameters[i].is_variable():
                    j += 1
                    self.initialpar.setitem(j, self.parameters[i].value)
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
                    l = int(jj*(jj+1)/2)
                    self.a.setitem(l, self.c.getitem(l)*(1.0 + self._lambda) + da)
                    if jj > 1:
                        for i in range (1, jj):
                            self.a.setitem(l-i, self.c.getitem(l-i))

                if self.a.chodec() == 0: # Cholesky decomposition
                    # the matrix is inverted, so calculate g (change in the
                    # parameters) by back substitution

                    print("Chlolesky decomposition ok")

                    self.a.choback(self.g)

                    prevwss = self.oldwss
                    recycle = 1

                    # Update the parameters: param = old param + g
                    # n0 counts the number of zero elements in g
                    do_cycle_2 = True
                    while do_cycle_2:
                        recyc = False
                        n0 = 0
                        i = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                i += 1

                                # update value of parameter
                                #  apply the required constraints (min/max)
                                self.parameters[j].set_value(self.currpar.getitem(i) + recycle*self.g.getitem(i))

                                # check number of parameters reaching convergence
                                if (abs(self.g.getitem(i))<=abs(PRCSN*self.currpar.getitem(i))): n0 += 1

                        # calculate functions

                        self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

                        if (n0==self.nfit):
                            self.conver = True

                        # update the wss
                        self.wss = self.getWSSQ()

                        if self.wss < prevwss:
                            prevwss = self.wss
                            recyc = True
                            recycle += 1

                        # last line of while loop
                        do_cycle_2 = recyc and recycle<10

                    if recycle > 1:

                        # restore parameters to best value
                        recycle -= 1

                        i = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                i += 1

                                # update value of parameter
                                #  apply the required constraints (min/max)
                                self.parameters[j].set_value(self.currpar.getitem(i) + recycle*self.g.getitem(i))

                        # calculate functions
                        self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

                        # update the wss
                        self.wss = self.getWSSQ()

                    # if all parameters reached convergence then it's time to quit

                    if self.wss < self.oldwss:
                        self.oldwss     = self.wss
                        self.exitflag   = True

                        ii = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                ii += 1

                                # update value of parameter
                                self.initialpar.setitem(ii, self.currpar.getitem(ii) + recycle*self.g.getitem(ii))

                    y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

                    self.build_minpack_data(y=y)

                    print(self.fit_data.to_text())
                else:
                    self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

                    print("Chlolesky decomposition failed")

                if not self.exitflag  and not self.conver:
                    if self._lambda<PRCSN: self._lambda = PRCSN
                    self._nincr += 1
                    self._lambda *= 10.0
                    if self._lambda>(1E5*self._lmin): self.conver = True

                # last line of the while loop
                do_cycle =  not self.exitflag and not self.conver

            j = 0
            for i in range(0, self.nprm):
                if self.parameters[i].is_variable():
                    j += 1
                    self.parameters[i].set_value(self.initialpar.getitem(j))

            self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

        fitted_parameters = self.parameters

        fit_global_parameters_out = self.build_fit_global_parameters_out(fitted_parameters)
        fit_global_parameters_out.set_convergence_reached(self.conver)

        fitted_pattern = self.build_fitted_diffraction_pattern(fit_global_parameters=fit_global_parameters_out)

        self.conver = False

        errors = [0] * len(self.parameters)

        self.a.zero()
        self.grad.zero()
        self.set()

        if self.a.chodec() == 0: # Cholesky decomposition
            k = 0
            for i in range (0, self.nprm):
                if self.parameters[i].is_variable():

                    self.g.zero()
                    self.g[k] = 1.0
                    self.a.choback(self.g)
                    errors[i] = numpy.sqrt(numpy.abs(self.g[k]))
                    k += 1
        else:
            print("Errors not calculated: chodec != 0")

        fit_global_parameters_out = self.build_fit_global_parameters_out_errors(errors=errors)

        return fitted_pattern, fit_global_parameters_out, self.fit_data

    def set(self):
        fmm = self.getWeightedDelta()
        deriv = self.getDerivative()

        for i in range(1, self.getNrPoints() + 1):
            for jj in range(1, self.nfit + 1):

                l = int(jj * (jj - 1) / 2)
                self.grad.setitem(jj, self.grad.getitem(jj) + deriv.getitem(jj, i) * fmm[i - 1])

                for k in range(1, jj + 1):
                    self.a.setitem(l + k, self.a.getitem(l + k) + deriv.getitem(jj, i) * deriv.getitem(k, i))

    def finalize_fit(self):
        pass


    def build_fit_global_parameters_out(self, fitted_parameters):
        fit_global_parameters = self.fit_global_parameters

        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        crystal_structure.a.set_value(fitted_parameters[0].value)
        crystal_structure.b.set_value(fitted_parameters[1].value)
        crystal_structure.c.set_value(fitted_parameters[2].value)
        crystal_structure.alpha.set_value(fitted_parameters[3].value)
        crystal_structure.beta.set_value(fitted_parameters[4].value)
        crystal_structure.gamma.set_value(fitted_parameters[5].value)

        last_index = 5

        if crystal_structure.use_structure:
            crystal_structure.intensity_scale_factor.set_value(fitted_parameters[6].value)
            last_index += 1

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            crystal_structure.get_reflection(reflection_index).intensity.set_value(fitted_parameters[last_index + 1 + reflection_index].value)

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None \
                and not fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor is None:
            fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor.set_value(fitted_parameters[last_index + 1].value)

            last_index += fit_global_parameters.fit_initialization.thermal_polarization_parameters.get_parameters_count()

        if not fit_global_parameters.background_parameters is None:
            for key in fit_global_parameters.background_parameters.keys():
                background_parameters = fit_global_parameters.get_background_parameters(key)

                if not background_parameters is None:
                    if key == ChebyshevBackground.__name__:
                        background_parameters.c0.set_value(fitted_parameters[last_index + 1].value)
                        background_parameters.c1.set_value(fitted_parameters[last_index + 2].value)
                        background_parameters.c2.set_value(fitted_parameters[last_index + 3].value)
                        background_parameters.c3.set_value(fitted_parameters[last_index + 4].value)
                        background_parameters.c4.set_value(fitted_parameters[last_index + 5].value)
                        background_parameters.c5.set_value(fitted_parameters[last_index + 6].value)
                    elif key == ExpDecayBackground.__name__:
                        background_parameters.a0.set_value(fitted_parameters[last_index + 1].value)
                        background_parameters.b0.set_value(fitted_parameters[last_index + 2].value)
                        background_parameters.a1.set_value(fitted_parameters[last_index + 3].value)
                        background_parameters.b1.set_value(fitted_parameters[last_index + 4].value)
                        background_parameters.a2.set_value(fitted_parameters[last_index + 5].value)
                        background_parameters.b2.set_value(fitted_parameters[last_index + 6].value)

                last_index += background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            fit_global_parameters.instrumental_parameters.U.set_value(fitted_parameters[last_index + 1].value)
            fit_global_parameters.instrumental_parameters.V.set_value(fitted_parameters[last_index + 2].value)
            fit_global_parameters.instrumental_parameters.W.set_value(fitted_parameters[last_index + 3].value)
            fit_global_parameters.instrumental_parameters.a.set_value(fitted_parameters[last_index + 4].value)
            fit_global_parameters.instrumental_parameters.b.set_value(fitted_parameters[last_index + 5].value)
            fit_global_parameters.instrumental_parameters.c.set_value(fitted_parameters[last_index + 6].value)

            last_index += fit_global_parameters.instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.shift_parameters is None:
            for key in fit_global_parameters.shift_parameters.keys():
                shift_parameters = fit_global_parameters.get_shift_parameters(key)

                if not shift_parameters is None:
                    if key == Lab6TanCorrection.__name__:
                        shift_parameters.ax.set_value(fitted_parameters[last_index + 1].value)
                        shift_parameters.bx.set_value(fitted_parameters[last_index + 2].value)
                        shift_parameters.cx.set_value(fitted_parameters[last_index + 3].value)
                        shift_parameters.dx.set_value(fitted_parameters[last_index + 4].value)
                        shift_parameters.ex.set_value(fitted_parameters[last_index + 5].value)
                    elif key == ZeroError.__name__:
                        shift_parameters.shift.set_value(fitted_parameters[last_index + 1].value)

                last_index += shift_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            fit_global_parameters.size_parameters.mu.set_value(fitted_parameters[last_index + 1].value)
            fit_global_parameters.size_parameters.sigma.set_value(fitted_parameters[last_index + 2].value)

            last_index += fit_global_parameters.size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            if isinstance(fit_global_parameters.strain_parameters, InvariantPAH):
                fit_global_parameters.strain_parameters.aa.set_value(fitted_parameters[last_index + 1].value)
                fit_global_parameters.strain_parameters.bb.set_value(fitted_parameters[last_index + 2].value)
                fit_global_parameters.strain_parameters.e1.set_value(fitted_parameters[last_index + 3].value) # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e2.set_value(fitted_parameters[last_index + 4].value) # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e3.set_value(fitted_parameters[last_index + 5].value) # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e4.set_value(fitted_parameters[last_index + 6].value) # in realtà è E4 dell'invariante PAH
                fit_global_parameters.strain_parameters.e5.set_value(fitted_parameters[last_index + 7].value) # in realtà è E4 dell'invariante PAH
                fit_global_parameters.strain_parameters.e6.set_value(fitted_parameters[last_index + 8].value) # in realtà è E4 dell'invariante PAH
            elif isinstance(fit_global_parameters.strain_parameters, KrivoglazWilkensModel):
                fit_global_parameters.strain_parameters.rho.set_value(fitted_parameters[last_index + 1].value)
                fit_global_parameters.strain_parameters.Re.set_value(fitted_parameters[last_index + 2].value)
                fit_global_parameters.strain_parameters.Ae.set_value(fitted_parameters[last_index + 3].value)
                fit_global_parameters.strain_parameters.Be.set_value(fitted_parameters[last_index + 4].value)
                fit_global_parameters.strain_parameters.As.set_value(fitted_parameters[last_index + 5].value)
                fit_global_parameters.strain_parameters.Bs.set_value(fitted_parameters[last_index + 6].value)
                fit_global_parameters.strain_parameters.mix.set_value(fitted_parameters[last_index + 7].value)
                fit_global_parameters.strain_parameters.b.set_value(fitted_parameters[last_index + 8].value)
            elif isinstance(fit_global_parameters.strain_parameters, WarrenModel):
                fit_global_parameters.strain_parameters.average_cell_parameter.set_value(fitted_parameters[last_index + 1].value)

            last_index += fit_global_parameters.strain_parameters.get_parameters_count()

        if fit_global_parameters.has_functions(): fit_global_parameters.evaluate_functions()

        return fit_global_parameters

    def build_fit_global_parameters_out_errors(self, errors):
        fit_global_parameters = self.fit_global_parameters

        crystal_structure = fit_global_parameters.fit_initialization.crystal_structure

        crystal_structure.a.error = errors[0]
        crystal_structure.b.error = errors[1]
        crystal_structure.c.error = errors[2]
        crystal_structure.alpha.error = errors[3]
        crystal_structure.beta.error = errors[4]
        crystal_structure.gamma.error = errors[5]

        last_index = 5

        if crystal_structure.use_structure:
            crystal_structure.intensity_scale_factor.error = errors[6]
            last_index += 1

        for reflection_index in range(fit_global_parameters.fit_initialization.crystal_structure.get_reflections_count()):
            crystal_structure.get_reflection(reflection_index).intensity.error = errors[last_index+reflection_index]

        last_index = crystal_structure.get_parameters_count() - 1

        if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None  \
                and not fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor is None:
            fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor.error = errors[last_index + 1]

            last_index += fit_global_parameters.fit_initialization.thermal_polarization_parameters.get_parameters_count()

        if not fit_global_parameters.background_parameters is None:
            for key in fit_global_parameters.background_parameters.keys():
                background_parameters = fit_global_parameters.get_background_parameters(key)

                if not background_parameters is None:
                    if key == ChebyshevBackground.__name__:
                        background_parameters.c0.error = errors[last_index + 1]
                        background_parameters.c1.error = errors[last_index + 2]
                        background_parameters.c2.error = errors[last_index + 3]
                        background_parameters.c3.error = errors[last_index + 4]
                        background_parameters.c4.error = errors[last_index + 5]
                        background_parameters.c5.error = errors[last_index + 6]
                    elif key == ExpDecayBackground.__name__:
                        background_parameters.a0.error = errors[last_index + 1]
                        background_parameters.b0.error = errors[last_index + 2]
                        background_parameters.a1.error = errors[last_index + 3]
                        background_parameters.b1.error = errors[last_index + 4]
                        background_parameters.a2.error = errors[last_index + 5]
                        background_parameters.b2.error = errors[last_index + 6]

                last_index += background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            fit_global_parameters.instrumental_parameters.U.error = errors[last_index + 1]
            fit_global_parameters.instrumental_parameters.V.error = errors[last_index + 2]
            fit_global_parameters.instrumental_parameters.W.error = errors[last_index + 3]
            fit_global_parameters.instrumental_parameters.a.error = errors[last_index + 4]
            fit_global_parameters.instrumental_parameters.b.error = errors[last_index + 5]
            fit_global_parameters.instrumental_parameters.c.error = errors[last_index + 6]

            last_index += fit_global_parameters.instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.shift_parameters is None:
            for key in fit_global_parameters.shift_parameters.keys():
                shift_parameters = fit_global_parameters.get_shift_parameters(key)

                if not shift_parameters is None:
                    if key == Lab6TanCorrection.__name__:
                        shift_parameters.ax.error = errors[last_index + 1]
                        shift_parameters.bx.error = errors[last_index + 2]
                        shift_parameters.cx.error = errors[last_index + 3]
                        shift_parameters.dx.error = errors[last_index + 4]
                        shift_parameters.ex.error = errors[last_index + 5]
                    elif key == ZeroError.__name__:
                        shift_parameters.shift.error = errors[last_index + 1]

                last_index += shift_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            fit_global_parameters.size_parameters.mu.error    = errors[last_index + 1]
            fit_global_parameters.size_parameters.sigma.error = errors[last_index + 2]

            last_index += fit_global_parameters.size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            if isinstance(fit_global_parameters.strain_parameters, InvariantPAH):
                fit_global_parameters.strain_parameters.aa.error = errors[last_index + 1]
                fit_global_parameters.strain_parameters.bb.error = errors[last_index + 2]
                fit_global_parameters.strain_parameters.e1.error = errors[last_index + 3] # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e2.error = errors[last_index + 4] # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e3.error = errors[last_index + 5] # in realtà è E1 dell'invariante PAH
                fit_global_parameters.strain_parameters.e4.error = errors[last_index + 6] # in realtà è E4 dell'invariante PAH
                fit_global_parameters.strain_parameters.e5.error = errors[last_index + 7] # in realtà è E4 dell'invariante PAH
                fit_global_parameters.strain_parameters.e6.error = errors[last_index + 8] # in realtà è E4 dell'invariante PAH
            elif isinstance(fit_global_parameters.strain_parameters, KrivoglazWilkensModel):
                fit_global_parameters.strain_parameters.rho.error = errors[last_index + 1]
                fit_global_parameters.strain_parameters.Re.error = errors[last_index + 2]
                fit_global_parameters.strain_parameters.Ae.error = errors[last_index + 3]
                fit_global_parameters.strain_parameters.Be.error = errors[last_index + 4]
                fit_global_parameters.strain_parameters.As.error = errors[last_index + 5]
                fit_global_parameters.strain_parameters.Bs.error = errors[last_index + 6]
                fit_global_parameters.strain_parameters.mix.error = errors[last_index + 7]
                fit_global_parameters.strain_parameters.b.error = errors[last_index + 8]
            elif isinstance(fit_global_parameters.strain_parameters, WarrenModel):
                fit_global_parameters.strain_parameters.average_cell_parameter.error = errors[last_index + 1]

            last_index += fit_global_parameters.strain_parameters.get_parameters_count()

        if fit_global_parameters.has_functions(): fit_global_parameters.evaluate_functions()

        return fit_global_parameters

    def build_fitted_diffraction_pattern(self, fit_global_parameters):
        wavelength = fit_global_parameters.fit_initialization.diffraction_pattern.wavelength

        fitted_pattern = DiffractionPattern()
        fitted_pattern.wavelength = wavelength

        fitted_intensity = fit_function(self.s_experimental, fit_global_parameters)
        fitted_residual = self.intensity_experimental - fitted_intensity

        for index in range(0, len(fitted_intensity)):
            fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=self.twotheta_experimental[index],
                                                                                    intensity=fitted_intensity[index],
                                                                                    error=fitted_residual[index],
                                                                                    s=self.s_experimental[index]))
        return fitted_pattern

    def build_minpack_data(self, y=None):
        self.wss = self.getWSSQ(y=y)

        self.fit_data.wss = self.wss
        self.fit_data.ss = self.getSSQFromData(y=y)
        self.fit_data.wsq = self.getWSQFromData(y=y)
        self.fit_data.calc_lambda = self._lambda
        self.fit_data.calculate()


    ###############################################
    #
    # METODI minObj
    #
    ###############################################

    def getNrPoints(self):
        return len(self.twotheta_experimental)

    def getNrParamToFit(self):
        nfit = 0
        for parameter in self.parameters:
            if parameter.is_variable():
                nfit += 1
        return nfit

    def getWeightedDelta(self):
        y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

        fmm = numpy.zeros(self.getNrPoints())

        for i in range (0, self.getNrPoints()):
            if self.error_experimental[i] == 0:
                fmm[i] = 0
            else:
                fmm[i] = (y[i] - self.intensity_experimental[i])/self.error_experimental[i]

        return fmm

    def getDerivative(self):
        y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

        deriv = CMatrix(self.getNrParamToFit(), self.getNrPoints())

        jj = 0
        for k in range (0, self.nprm):
            parameter = self.parameters[k]

            if parameter.is_variable():
                pk = parameter.value
                if parameter.step == PARAM_ERR: step = 0.001
                else: step = parameter.step

                if abs(pk) > PRCSN:
                    d = pk*step
                    parameter.value = pk * (1.0 + step)
                    parameter.check_value()

                    deriv[jj] = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))
                else:
                    d = step
                    parameter.value = pk + d
                    parameter.check_value()

                    deriv[jj] = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

                parameter.value = pk
                parameter.check_value()

                for i in range(0, self.getNrPoints()):
                    if self.error_experimental[i] == 0:
                        deriv[jj][i] = 0.0
                    else:
                        deriv[jj][i] = (deriv[jj][i] - y[i]) / (d * self.error_experimental[i])
                jj += 1

        return deriv

    def getWSSQ(self, y=None, fit_global_parameter=None):
        if y is None: y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

        wssqlow = 0.0
        wssq = 0.0

        if self.mighell:
            for i in range(0, self.getNrPoints()):
                if self.intensity_experimental[i] < 1:
                    yv = y[i] - 2*self.intensity_experimental[i]
                else:
                    yv = y[i] - (self.intensity_experimental[i] + 1.0)

                wssqtmp = (yv**2)/(self.error_experimental[i]**2+1.0)

                if (wssqtmp<1E-2):
                    wssqlow += wssqtmp
                else:
                    wssq    += wssqtmp
        else:
            for i in range(0, self.getNrPoints()):
                if self.error_experimental[i] == 0.0:
                    yv = 0.0
                else:
                    yv = (y[i] - self.intensity_experimental[i])/self.error_experimental[i]

                    wssqtmp = (yv**2)

                    if (wssqtmp<1E-2):
                        wssqlow += wssqtmp
                    else:
                        wssq    += wssqtmp

        return wssq + wssqlow


    def getWSQFromData(self, y=None):
        if y is None: y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

        wssq = 0.0

        for i in range(0, self.getNrPoints()):
            if not self.mighell:
                if self.error_experimental[i] == 0.0:
                    yv = 0.0
                else:
                    yv = (y[i] - self.intensity_experimental[i])/self.error_experimental[i]

                wssq += (yv**2)
            else:
                if self.intensity_experimental[i] < 1:
                    yv = y[i] - 2*self.intensity_experimental[i]
                else:
                    yv = y[i] - (self.intensity_experimental[i] + 1.0)

                wssq += (yv**2)/(self.error_experimental[i]**2+1.0)

        return wssq

    def getSSQFromData(self, y=None):
        if y is None: y = fit_function(self.s_experimental, self.build_fit_global_parameters_out(self.parameters))

        ss = 0.0

        for i in range(0, self.getNrPoints()):
            if not self.mighell:
                yv = (y[i] - self.intensity_experimental[i])
            else:
                if self.intensity_experimental[i] < 1:
                    yv = y[i] - 2*self.intensity_experimental[i]
                else:
                    yv = y[i] - (self.intensity_experimental[i] + 1.0)

            ss += yv**2

        return ss

