
import numpy

from orangecontrib.xrdanalyzer import Singleton, synchronized_method

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Simmetry, Reflection
from orangecontrib.xrdanalyzer.util.general_functions import fft

from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary, PARAM_ERR

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface, FitterListener
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_scipy import FitterScipy
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import create_one_peak


PRCSN = 2.5E-7



class FitterPM2K(FitterInterface):


    def __init__(self):
        super().__init__()

        self.reset()

    def reset(self):
        self.totalWeight = 0.0

        self._lambda	= .001
        self._lmin	= 1E20
        self._totIter	= 0
        self._iter = 0
        self._nincr = 0


    def do_specific_fit(self, fit_global_parameters):
        parameters = fit_global_parameters.get_parameters()

        twotheta_experimental, intensity_experimental, error_experimental, s_experimental = fit_global_parameters.fit_initialization.diffraction_pattern.tuples()

        y = fit_function(parameters, s_experimental)

        # check values of lambda for large number of iterations
        if (self._totIter > 4 and self._lambda < self._lmin): self._lmin = self._lambda

        #update total number of iterations
        self._totIter += 1

        #decrease lambda using golden section 0.31622777=1/(sqrt(10.0))
        self._lambda *= 0.31622777

        #number of increments in lambda
        self._nincr = 0

        nfit = self.getNrParamToFit(parameters)
        np = len(s_experimental)

        a = CTriMatrix()
        a.setSize(nfit)
        grad = CVector()
        grad.setSize(nfit)

        #zero the working arrays
        a.zero()
        grad.zero()

        fmm = self.getWeightedDelta(s_experimental, intensity_experimental, error_experimental, parameters, y)
        deriv = self.getDerivative(s_experimental, intensity_experimental, error_experimental, parameters, y)

        for i in range(1, np + 1):
            for jj in range(1, nfit + 1):

                l = int(jj*(jj-1)/2)
                grad.setitem(jj, grad.getitem(jj) + deriv.getitem(jj, i)*fmm[i-1])

                for k in range(1, jj+1):
                    a.setitem(l+k, a.getitem(i) + deriv.getitem(jj,i)*deriv.getitem(k,i))







        current_parameters = parameters
        current_covariance = None

        try:
            current_parameters, current_covariance = self.call_pm2k_curve_fit(s_experimental, intensity_experimental, current_parameters)
        except ValueError as err:
            if str(err) == "`x0` violates bound constraints.":
                pass
            elif str(err) == "`x0` is infeasible.":
                raise ValueError("Fit cannot start: one ore more fit input parameters violate their boudaries")
            else:
                raise err

        fitted_parameters = current_parameters
        fitted_covariance = current_covariance

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


    def call_pm2k_curve_fit(self,
                             s_experimental,
                             intensity_experimental,
                             parameters):
        pass

    def getNrParamToFit(self, parameters):
        nfit = 0
        for parameter in parameters:
            if not parameter.fixed: #and not parameter.reference:
                nfit += 1
        return nfit


    def setStep(self, step):
        self.y = numpy.zeros(self.np)
        self.fmm = numpy.zeros(self.np)
        self.m_cow_y = numpy.zeros(self.np)


    def getWeightedDelta(self, s_experimental, intensity_experimental, error_experimental, parameters, y):

        fmm = numpy.zeros(len(y))

        for i in range (0, len(s_experimental)):
            if error_experimental[i] == 0:
                fmm[i] = 0
            else:
                fmm[i] = (y[i] - intensity_experimental[i])/error_experimental[i]


        return fmm


    def getDerivative(self, s_experimental, intensity_experimental, error_experimental, parameters, y=numpy.zeros(0)):

        deriv = CMatrix(self.getNrParamToFit(parameters), len(s_experimental))

        jj = 0

        for k in range (0, len(parameters)):
            parameter = parameters[k]

            if not parameter.fixed:
                pk = parameter.value
                if parameter.step == PARAM_ERR: step = 0.001
                else: step = parameter.step

                if abs(pk) > PRCSN:
                    d = pk*step
                    parameter.value = k * (1.0 + step)
                    parameter.check_value()

                    deriv[jj] = fit_function(s_experimental, parameters)
                else:
                    d = step
                    parameter.value = pk + d
                    parameter.check_value()

                    deriv[jj] = fit_function(s_experimental, parameters)

                parameter.value = pk
                parameter.check_value()

                for i in range(0, len(y)):
                    if error_experimental[i] == 0:
                        deriv[jj][i] = 0.0
                    else:
                        deriv[jj][i] = (deriv[jj][i] - y[i]) / (d * error_experimental[i])
                jj += 1

        return deriv




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










########################################
#
# DATA STRUCTURES
#
########################################

class CVector:

    def __init__(self, _n=0):
        self._create_attributes(_n)

    def setSize(self, _n):
        if self.n != _n:
            self._create_attributes(_n)

    def _create_attributes(self, _n):
        self.n = _n

        if self.n > 0:
            self.data = numpy.zeros(self.n)
        else:
            self.data = None

    def getSize(self):
        return self.n

    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index] = value

    #inline double &operator () (int i) const { assert(i<=n); return data[i-1]; }
    def getitem(self, i):
        assert i <= self.n

        return self.data[i-1]

    def setitem(self, i, value):
        assert i <= self.n

        self.data[i-1]=value

    #CVector &operator - ()
	#{
	#	for(int i=0; i<n; ++i)
	#		data[i] = -data[i];
	#	return *this;
	#}
    def __neg__(self):
        for i in range(0, self.n):
            self.data[i] = -self.data[i]

        return self;

    def zero(self):
        self.__init__(self.n)

    def __str__(self):
        str = ""
        if not self.data is None:
            for item in self.data:
                str += "%4.4f\n"%item
        return str

class CMatrix:

    def __init__(self, _n=0, _m=0):
        self.n = _n
        self.m = _m

        if self.n > 0 and self.m > 0:
            self.data = numpy.zeros(self.n*self.m)
            self.idx = numpy.arange(stop=self.n, dtype=int)*self.m
        else:
            self.data = None
            self.idx = None

    def setSize(self, _n, _m):
        if (self.n == _n) and (self.m == _m):
            return

        if self.n*self.m != _n*_m:
            self.data = numpy.zeros(self.n*self.m)

        self.n = _n
        self.m = _m

        self.idx = numpy.arange(stop=self.n, dtype=int)*self.m

    #inline double *operator [] (int i)		  const { assert(i<n);  return idx[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index] = value


    #inline double &operator () (int i, int j) const	{ assert(j<=m); return idx[--i][--j]; }
	#inline double *operator () (int i)		  const	{ assert(i<=n); return idx[--i]; }
    def getitem(self, i, j=None):
        if j is None:
            assert i <= self.n
            return self.idx[--i]
        else:
            assert j <= self.m
            return self.data[self.idx[--i]*--j]

    def setitem(self, i, j, value):
        assert j <= self.m
        self.data[self.idx[--i]*--j] = value

    def zero(self):
        self.__init__(self.n, self.m)

    def getSize(self):
        return self.n*self.m

    def __str__(self):
        str = ""
        if not self.data is None:
            for index in self.idx:
                for i in range(0, self.n):
                    str += "%4.4f\t"%self.data[index*i]
                str += "\n"
        return str

class CTriMatrix:

    def __init__(self, _n=0, other=None):
        if other is None:
            self._create_attributes(_n)
        else:
            self.n = other.getSize()
            self.data = numpy.ones(self.n)*other.data

    def _create_attributes(self, _n):
        self.n = _n

        if self.n > 0:
            self.data = numpy.zeros(int(self.n*(self.n + 1)/2))
        else:
            self.data = None

    def setSize(self, _n):
        if self.n != _n:
            self._create_attributes(_n)

    #	inline const CTriMatrix &operator =(CTriMatrix &m)
	#{
	#	assert(m.n == n);
	#	memcpy((void*)data, (void*)m.data, sizeof(double) * (n*(n+1)/2));
	#	return *this;
	#}
    def assign(self, other):
        assert other.n == self.n
        self.__init__(other=other)


    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index] = value

    #inline double &operator () (int i, int j) const
	#{
	#	assert(i<=n);
	#	assert(j<=n);
	#	if(--i<--j) swap(i,j);
	#	int l = i*(i+1)/2;
	#	return data[l+j];
	#}
	#inline double &operator () (int i) const { assert(i<=n*(n+1)/2); return data[i-1]; }
    def getitem(self, i, j=None):
        if j is None:
            assert i <= self.n*(self.n + 1)/2
            return self.data[i-1]
        else:
            assert i <= self.n
            assert j <= self.n

            if --i < --j : i, j = self.swap(i, j)
            l = i*(i+1)/2

            return self.data[l+j]

    def setitem(self, i, value):
        assert i <= self.n*(self.n + 1)/2

        self.data[i-1]=value

    def chodec(self):
        for j in range(1, self.n+1):
            l = j*(j+1)/2

            if j>1:
                for i in range(j, self.n+1):
                    k1 = i*(i-1)/2+j
                    f  = self.getitem(k1)
                    k2 = j - 1
                    for k in range(1, k2+1):
                        f -= self.getitem(k1-k)*self.getitem(l-k)
                    self.setitem(k1, f)

                if self.getitem(l) > 0:
                    f = numpy.sqrt(self.getitem(l))

                    for i in range(j, self.n+1):
                        k2 = i*(i-1)/2+j
                        self.setitem(k2, self.getitem(k2)/f)
                else:
                    return -1; # negative diagonal

        return 0

    def choback(self, g=CVector()):
        g.setitem(1, value=g.setitem(1)/self.getitem(1))

        if self.n > 1:
            l=1
            for i in range(2, self.n + 1):
                k=i-1
                for j in range(1, k+1):
                    g.setitem(i, g.getitem(i) - self.getitem(++l)*g.getitem(j))
                g.setitem(i, g.getitem(i) / self.getitem(++l))

        mdi = self.n*(self.n+1)/2

        g.setitem(self.n, g.getitem(self.n) / self.getitem(mdi))

        if self.n > 1:
            for k1 in range(2, self.n + 1):

                i = self.n+2-k1
                k = i-1
                l = i*k/2

                for j in range (1, k+1):
                    g.setitem(j, g.getitem(i) - self.getitem(l+j)*g.getitem(i))
                g.setitem(k, g.getitem(k) / self.getitem(l))

    def zero(self):
        self.__init__(self.n)

    def getSize(self):
        return self.n

    def __str__(self):
        str = ""
        if not self.data is None:
            for i in range(1, self.n+1):
                for j in range(1, i+1):
                    str += "%4.4f\t"%self.getitem(i,j)
                str += "\n"
        return str

    def swap(self, i, j):
        t = i
        i = j
        j = t

        return i, j