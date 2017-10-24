
from scipy.optimize import curve_fit, least_squares

class FitParameter:
    pass

def fitterScipyCurveFit(function_to_fit, s_experimental, intensity_experimental,
           listparameters):
    #additional_infos contains information such as S_max,
    #minimization method, or other

    #the s_experimental has variable step, we construct the

    popt, pcov = curve_fit(function_to_fit, s_experimental, intensity_experimental,
                           listparameters)
    return popt, pcov



