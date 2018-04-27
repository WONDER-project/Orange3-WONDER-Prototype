
import numpy

l = numpy.array([1 + 1j*3, 2+1j*8])

l1 = numpy.array([1, 2])
l2 = numpy.array([3, 8])

l3 = l1 + 1j*l2

print(isinstance(l3[0], complex))