import numpy
import inspect


def distance(X, Y):
    return numpy.linalg.norm(X-Y)







def attributes_of_a_point (myClass):
    # HERE, I WANT TO return a list of all attributes of
    #a class (even those that are initialized to None)
    # using "test2.py" it seems to work
    # this should be put in some utility file, together
    # with the other method used below (def predicate)
    attr = inspect.getmembers(myClass,
                              lambda a: not (inspect.isroutine(a)))
    attr = [a for a in attr if not (a[0].startswith('__')
                                    and a[0].endswith('__'))]
    attr = [getattr(myClass, attr[i][0]) for i in range(0, len(attr))]

    return [attr[3], attr[1], attr[0], attr[2]]

