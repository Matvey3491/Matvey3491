# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QByteArray
import time
import struct

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.flagBegin = False
        self.reverse = 0

    def run(self):
        i = 1
        i1 = 0
        iflag = 1
        self.running = True
        self.flagBegin = True
        self.reverse = 0.05
        while (i > -1) and (self.running):

            self.mysignal.emit("i = %s" % i, i)
            i = i + iflag
            if (i == 94) or (i == 1):
                iflag = -iflag
            if self.reverse != 0:
                time.sleep(0.08)
            else:
                time.sleep(0.08)


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()
        self.spisImage=[]
        fopen = open('data.bin', 'rb')
        for i in range(1, 96):
            datasize = struct.unpack("<I", fopen.read(4))
            imgas = QPixmap()
            imgas.loadFromData(QByteArray(fopen.read(datasize[0])))
            self.spisImage.append(imgas)
        fopen.close()

        self.mythread = MyThread()
        self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.offset = None
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.offset = event.pos()
        elif event.type() == QtCore.QEvent.MouseMove and self.offset is not None:
            self.move(self.pos() - self.offset + event.pos())
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            self.offset = None
        elif event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.close()
            return True
        elif event.type() == QtCore.QEvent.Wheel:
            delta = int(event.angleDelta().y() /8)
            if delta > 0:
                self.resize(self.width()+20,self.height()+10)

            elif delta < 0:
                self.resize(self.width()-20,self.height()-10)

            return True
        return super().eventFilter(source, event)


    def on_change(self, s, i):

        pixmap = (self.spisImage[i].scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))

        pal = self.palette()
        pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
        pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
        self.setPalette(pal)
        self.setMask(pixmap.mask())


# nuitka --mingw64 --plugin-enable=pyqt5 --include-qt-plugins=sensible --windows-disable-console --onefile  MyProgRybka_4_1.py
# создание exe файла

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()

    window.resize(450, 450)
    pixmap = (window.spisImage[0].scaled(window.width(),window.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    pal = window.palette()
    pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
    pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
    window.setPalette(pal)

    window.setMask(pixmap.mask())
    window.mythread.start()
    window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    window.show()
    sys.exit(app.exec_())

