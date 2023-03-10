from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from Utils import *


class Worker(QThread):
    def __init__(self, file_list, root):
        super().__init__()
        self.file_list = file_list
        self.root = root
    intReady = pyqtSignal(int)
    strReady = pyqtSignal(str)

    @pyqtSlot()
    def run(self):
        self.strReady.emit('Подготовка к записи.')
        sdburnerout = write_to_cd(self.file_list)
        while True:
            line = sdburnerout.stdout.readline()
            line2 = line.decode().replace('\n', '').replace('\r', '')
            self.strReady.emit('Идет запись, подождите.')
            if line2.endswith('%'):
                self.strReady.emit('Идет запись, подождите.')
                self.intReady.emit(int(line2[:-1]))
            self.strReady.emit(fr'{line}')
            if not line:
                break
        self.root.close()
        self.quit()


class Progress_window(QtWidgets.QDialog):
    def __init__(self, root, list_to_write):
        super(Progress_window, self).__init__(parent=root)
        self.root = root
        self.list_to_write = list_to_write
        self.setWindowTitle("Запись на диск")
        self.setFixedSize(470, 70)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 5, 450, 25))
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(QtCore.QRect(10, 30, 450, 30))
        self.pbar.setAlignment(QtCore.Qt.AlignCenter)
        self.show()
        self.start_worker()

    def setPbarValue(self, value):
        self.pbar.setValue(value)
    
    def setLabelText(self, string):
        self.label.setText(string)

    def start_worker(self):
        self.show()
        self.thread = QThread()
        self.worker = Worker(self.list_to_write, self)
        self.worker.moveToThread(self.thread)
        self.worker.intReady.connect(self.setPbarValue)
        self.worker.strReady.connect(self.setLabelText)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
