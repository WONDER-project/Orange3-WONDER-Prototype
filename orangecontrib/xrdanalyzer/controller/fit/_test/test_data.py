from scipy import special

print(lambda x: special.jv(2.5,x))


'''
import numpy

l = numpy.array([1 + 1j*3, 2+1j*8])

l1 = numpy.array([1, 2])
l2 = numpy.array([3, 8])

l3 = l1 + 1j*l2

print(isinstance(l3[0], complex))

from PyQt5 import QtCore, QtGui, QtWidgets
import sys, time

class mythread(QtCore.QThread):

    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, n):
        super(mythread, self).__init__(parent)
        self.n = n

    def run(self):
        self.total.emit(self.n)
        i = 0
        while (i<self.n):
            if (time.time() % 1==0):
                i+=1
                #print str(i)
                self.update.emit()

# create the dialog for zoom to point
class progress(QtWidgets.QProgressBar):

    def __init__(self, parent=None):
        super(progress, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setValue(0)

        self.thread = mythread(self, 20)

        self.thread.total.connect(self.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)

        self.n = 0
        self.thread.start()

    def update(self):
        self.n += 1
        print (self.n)
        self.setValue(self.n)

if __name__=="__main__":
    app = QtWidgets.QApplication([])
    progressWidget = progress()
    progressWidget.move(300, 300)
    progressWidget.show()
    sys.exit(app.exec_())
'''