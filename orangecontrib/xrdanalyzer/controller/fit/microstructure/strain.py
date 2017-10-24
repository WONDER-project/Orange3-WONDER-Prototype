import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PM2KParametersList, FitParametersList, FitParameter, Boundary

class LaueGroup:

    laue_groups = {}
    laue_groups["-1"] = "1"
    laue_groups["2/m"] = "2"
    laue_groups["2/mmm"] = "3"
    laue_groups["4/m"] = "4"
    laue_groups["4/mmm"] = "5"
    laue_groups["-3R"] = "6"
    laue_groups["-31mR"] = "7"
    laue_groups["-3"] = "8"
    laue_groups["-3m1"] = "9"
    laue_groups["-31m"] = "10"
    laue_groups["6/m"] = "11"
    laue_groups["6/mmm"] = "12"
    laue_groups["m3"] = "13"
    laue_groups["m3m"] = "14"

    @classmethod
    def get_laue_id(cls, laue_group):
        return cls.laue_groups[laue_group]

    @classmethod
    def get_laue_group(cls, laue_id):
        for key, value in cls.laue_groups.items():
            if int(value) == laue_id:
                return key

class InvariantPAH(FitParametersList, PM2KParametersList):
    aa = None
    bb = None
    laue_id = 1
    e1 = None
    e2 = None
    e3 = None
    e4 = None
    e5 = None
    e6 = None
    e7 = None
    e8 = None
    e9 = None
    e10 = None
    e11 = None
    e12 = None
    e13 = None
    e14 = None
    e15 = None

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 laue_id = 1,
                 e1  = None,
                 e2  = None,
                 e3  = None,
                 e4  = None,
                 e5  = None,
                 e6  = None,
                 e7  = None,
                 e8  = None,
                 e9  = None,
                 e10 = None,
                 e11 = None,
                 e12 = None,
                 e13 = None,
                 e14 = None,
                 e15 = None):

        self.aa = aa
        self.bb = bb
        self.laue_id = laue_id

        self.add_parameter(self.aa)
        self.add_parameter(self.bb)

        self.e1  = e1
        self.e2  = e2
        self.e3  = e3
        self.e4  = e4
        self.e5  = e5
        self.e6  = e6
        self.e7  = e7
        self.e8  = e8
        self.e9  = e9
        self.e10 = e10
        self.e11 = e11
        self.e12 = e12
        self.e13 = e13
        self.e14 = e14
        self.e15 = e15

        if not self.e1  is None: self.add_parameter(e1)
        if not self.e2  is None: self.add_parameter(e2)
        if not self.e3  is None: self.add_parameter(e3)
        if not self.e4  is None: self.add_parameter(e4)
        if not self.e5  is None: self.add_parameter(e5)
        if not self.e6  is None: self.add_parameter(e6)
        if not self.e7  is None: self.add_parameter(e7)
        if not self.e8  is None: self.add_parameter(e8)
        if not self.e9  is None: self.add_parameter(e9)
        if not self.e10 is None: self.add_parameter(e10)
        if not self.e11 is None: self.add_parameter(e11)
        if not self.e12 is None: self.add_parameter(e12)
        if not self.e13 is None: self.add_parameter(e13)
        if not self.e14 is None: self.add_parameter(e14)
        if not self.e15 is None: self.add_parameter(e15)

    def get_invariant(self, h, k, l):
        invariant = self.e1.value*(h**4)

        if not self.e2  is None: invariant += self.e2.value*(k**4)
        if not self.e3  is None: invariant += self.e3.value*(l**4)
        if not self.e4  is None: invariant += 2*(self.e4.value*(h**2)*(k**2))
        if not self.e5  is None: invariant += 2*(self.e5.value*(k**2)*(l**2))
        if not self.e6  is None: invariant += 2*(self.e6.value*(h**2)*(l**2))
        if not self.e7  is None: invariant += 4*(self.e7.value*(h**3)*k)
        if not self.e8  is None: invariant += 4*(self.e8.value*(h**3)*l)
        if not self.e9  is None: invariant += 4*(self.e9.value*(k**3)*h)
        if not self.e10 is None: invariant += 4*(self.e10.value*(k**3)*l)
        if not self.e11 is None: invariant += 4*(self.e11.value*(l**3)*h)
        if not self.e12 is None: invariant += 4*(self.e12.value*(l**3)*k)
        if not self.e13 is None: invariant += 4*(self.e13.value*(h**2)*k*l)
        if not self.e14 is None: invariant += 4*(self.e14.value*(k**2)*h*l)
        if not self.e15 is None: invariant += 4*(self.e15.value*(l**2)*h*k)

        return invariant

    def to_PM2K(self):
        raise NotImplementedError("TODO!!!!!")


class InvariantPAHLaueGroup1(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e2  = FitParameter(parameter_name="e2" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e5  = FitParameter(parameter_name="e5" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4),
                 e8  = FitParameter(parameter_name="e8" , value=1e-4),
                 e9  = FitParameter(parameter_name="e9" , value=1e-4),
                 e10 = FitParameter(parameter_name="e10", value=1e-4),
                 e11 = FitParameter(parameter_name="e11", value=1e-4),
                 e12 = FitParameter(parameter_name="e12", value=1e-4),
                 e13 = FitParameter(parameter_name="e13", value=1e-4),
                 e14 = FitParameter(parameter_name="e14", value=1e-4),
                 e15 = FitParameter(parameter_name="e15", value=1e-4)):
        super().__init__(aa, bb, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12, e13, e14, e15)


class InvariantPAHLaueGroup2(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e2  = FitParameter(parameter_name="e2" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e5  = FitParameter(parameter_name="e5" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4),
                 e9  = FitParameter(parameter_name="e9" , value=1e-4),
                 e15 = FitParameter(parameter_name="e15", value=1e-4)):
        super().__init__(aa, bb, 2, e1, e2, e3, e4, e5, e6, e7, e9=e9, e15=e15)

class InvariantPAHLaueGroup3(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e2  = FitParameter(parameter_name="e2" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e5  = FitParameter(parameter_name="e5" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4)):
        super().__init__(aa, bb, 3, e1, e2, e3, e4, e5, e6, e7)

class InvariantPAHLaueGroup4(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4)):
        super().__init__(aa, bb, 4, e1, e3=e3, e4=e4, e6=e6, e7=e7)

class InvariantPAHLaueGroup5(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4)):
        super().__init__(aa, bb, 5, e1, e3=e3, e4=e4, e6=e6)



class InvariantPAHLaueGroup6(InvariantPAH):

    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4),
                 e9  = FitParameter(parameter_name="e9" , value=1e-4),
                 e15 = FitParameter(parameter_name="e15", value=1e-4)):
        super().__init__(aa, bb, 6, e1, e3=e3, e4=e4, e6=e6, e7=e7, e9=e9, e15=e15)

class InvariantPAHLaueGroup7(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4),
                 e9  = FitParameter(parameter_name="e9" , value=1e-4),
                 e15 = FitParameter(parameter_name="e15", value=1e-4)):
        super().__init__(aa, bb, 7, e1, e3=e3, e4=e4, e6=e6, e7=e7, e9=e9, e15=e15)

class InvariantPAHLaueGroup8(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e4  = FitParameter(parameter_name="e4" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e7  = FitParameter(parameter_name="e7" , value=1e-4),
                 e9  = FitParameter(parameter_name="e9" , value=1e-4),
                 e15 = FitParameter(parameter_name="e15", value=1e-4)):
        super().__init__(aa, bb, 8, e1, e3=e3, e4=e4, e6=e6, e7=e7, e9=e9, e15=e15)

class InvariantPAHLaueGroup9(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e13 = FitParameter(parameter_name="e13", value=1e-4)):
        super().__init__(aa, bb, 9, e1, e3=e3, e6=e6, e13=e13)


class InvariantPAHLaueGroup10(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4),
                 e13 = FitParameter(parameter_name="e13", value=1e-4)):
        super().__init__(aa, bb, 10, e1, e3=e3, e6=e6, e13=e13)

class InvariantPAHLaueGroup11(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4)):
        super().__init__(aa, bb, 11, e1, e3=e3, e6=e6)


class InvariantPAHLaueGroup12(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e3  = FitParameter(parameter_name="e3" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4)):
        super().__init__(aa, bb, 12, e1, e3=e3, e6=e6)


class InvariantPAHLaueGroup13(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4)):
        super().__init__(aa, bb, 13, e1, e6=e6)

class InvariantPAHLaueGroup14(InvariantPAH):
    def __init__(self,
                 aa=FitParameter(parameter_name="aa", value=1e-3),
                 bb=FitParameter(parameter_name="bb", value=1e-3),
                 e1  = FitParameter(parameter_name="e1" , value=1e-4),
                 e6  = FitParameter(parameter_name="e6" , value=1e-4)):
        super().__init__(aa, bb, 14, e1, e6=e6)