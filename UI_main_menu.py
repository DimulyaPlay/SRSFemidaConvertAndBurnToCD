from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
# from UI_search_menu import Cases_menu
from UI_courtrooms_menu import Courtrooms_menu
from UI_settings_menu import Settings_menu
from Utils import *


class MainMenu(qtw.QMainWindow):
    def __init__(self, sqlite, admin_mode=False):
        super().__init__()
        self.sqlite = sqlite
        self.admin_mode = admin_mode
        self.main_window()
        self.show()

    def main_window(self):
        self.setFixedSize(339, 201)
        self.setWindowTitle("SRS Femida. Экспорт аудиозаписей")
        self.mmenu = qtw.QWidget(self)
        self.mmenu.setFixedSize(339, 201)
        self.mmenu.setLayout(qtw.QVBoxLayout())
        button_cases = qtw.QPushButton('ИСКАТЬ ПО ДЕЛУ',clicked=lambda: self.open_cases_menu())
        button_cases.setFont(qtg.QFont('roboto', 24))
        self.mmenu.layout().addWidget(button_cases)
        button_courtrooms = qtw.QPushButton('ОТКРЫТЬ ЗАЛЫ',clicked=lambda: self.open_cr_menu())
        button_courtrooms.setFont(qtg.QFont('roboto', 24))
        self.mmenu.layout().addWidget(button_courtrooms)
        button_settings = qtw.QPushButton('ПАРАМЕТРЫ',clicked=lambda: self.open_settings())
        button_settings.setFont(qtg.QFont('roboto', 24))
        button_settings.setEnabled(self.admin_mode)
        self.mmenu.layout().addWidget(button_settings)
        self.mmenu.show()

    def open_cr_menu(self):
        print('now new cr menu opened')
        Courtrooms_menu(self, self.sqlite)

    def open_cases_menu(self):
        print('now new cases menu opened')
        Cases_menu(self, self.sqlite)

    def open_settings(self):
        print('now new settings menu opened')
        Settings_menu(self, self.sqlite)
