
from scipy.optimize import curve_fit, least_squares


def fitterScipyCurveFit(function_to_fit,
                        s_experimental,
                        intensity_experimental,
                        listparameters):
    #additional_infos contains information such as S_max,
    #minimization method, or other
    #the s_experimental has variable step, we construct the

    parameters, boundaries = listparameters.to_scipy_tuple()

    popt, pcov = curve_fit(f=function_to_fit,
                           xdata=s_experimental,
                           ydata=intensity_experimental,
                           p0=parameters,
                           bounds=boundaries)
    return popt, pcov



