from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
# from UI_search_menu import Cases_menu
# from UI_courtrooms_menu import Courtrooms_menu
from UI_settings_menu import Settings_menu
from Utils import *


class MainMenu(qtw.QWidget):
    def __init__(self, sqlite, admin_mode=False):
        super().__init__()
        self.setWindowTitle("SRS Femida. Экспорт аудиозаписей")
        self.resize(330,180)
        self.setLayout(qtw.QVBoxLayout())
        self.sqlite = sqlite
        button_cases = qtw.QPushButton('ИСКАТЬ ПО ДЕЛУ',clicked=lambda: self.open_cases_menu())
        button_cases.setFont(qtg.QFont('roboto', 24))
        self.layout().addWidget(button_cases)
        button_courtrooms = qtw.QPushButton('ОТКРЫТЬ ЗАЛЫ',clicked=lambda: self.open_cr_menu())
        button_courtrooms.setFont(qtg.QFont('roboto', 24))
        self.layout().addWidget(button_courtrooms)
        button_settings = qtw.QPushButton('ПАРАМЕТРЫ',clicked=lambda: self.open_settings())
        button_settings.setFont(qtg.QFont('roboto', 24))
        button_settings.setEnabled(admin_mode)
        self.layout().addWidget(button_settings)
        self.show()

    def open_cr_menu(self):
        self.hide()
        print('now new cr menu opened')
        Courtrooms_menu(self, self.sqlite)
        return

    def open_cases_menu(self):
        self.hide()
        print('now new cases menu opened')
        Cases_menu(self, self.sqlite)
        return

    def open_settings(self):
        self.hide()
        print('now new settings menu opened')
        Settings_menu(self, self.sqlite)
        return
