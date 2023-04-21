import sys
import os
from glob import glob
from PyQt5 import QtWidgets, uic
from Utils import gather_all, sqlite
from UI_courtrooms_menu import Courtrooms_menu
from UI_settings_menu import Settings_menu

if '-server_mode' in sys.argv:
    admin_mode = True
else:
    admin_mode = False


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self, sqlite, admin_mode=False):
        super().__init__()
        self.sqlite = sqlite
        uic.loadUi('assets\\main_menu.ui', self)
        pushButton_cases = self.findChild(QtWidgets.QPushButton, 'pushButton_cases')
        pushButton_cases.clicked.connect(lambda: self.open_cases_menu())
        pushButton_courtrooms = self.findChild(QtWidgets.QPushButton, 'pushButton_courtrooms')
        pushButton_courtrooms.clicked.connect(lambda: self.open_cr_menu())
        pushButton_settings = self.findChild(QtWidgets.QPushButton, 'pushButton_settings')
        pushButton_settings.clicked.connect(lambda: self.open_settings())
        self.admin_mode = admin_mode

    def open_cr_menu(self):
        crm = Courtrooms_menu(self, self.sqlite)
        crm.show()

    def open_cases_menu(self):
        cm = Cases_menu(self, self.sqlite)
        cm.show()

    def open_settings(self):
        sm = Settings_menu(self, self.sqlite)
        sm.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mm = MainMenu(sqlite=sqlite, admin_mode=True)
    mm.show()
    sys.exit(app.exec_())
