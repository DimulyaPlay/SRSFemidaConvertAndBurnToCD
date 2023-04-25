import sys
import os
import traceback
from glob import glob
from PyQt5 import QtWidgets, uic
from Utils import gather_all, sqlite
from UI_courtrooms_menu import Courtrooms_menu
from UI_settings_menu import Settings_menu
from UI_search_menu import Cases_menu

#pyinstaller --noconfirm --onedir --console --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffmpeg.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffprobe.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/readme.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/server_db_path.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/foobar2000;foobar2000/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/CDBurnerXP;CDBurnerXP/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/assets;assets/"  "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/StartProgram.py"

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
        try:
            crm = Courtrooms_menu(self, self.sqlite)
            crm.show()
        except:
            traceback.print_exc()

    def open_cases_menu(self):
        try:
            cm = Cases_menu(self, self.sqlite)
            cm.show()
        except:
            traceback.print_exc()

    def open_settings(self):
        try:
            sm = Settings_menu(self, self.sqlite)
            sm.show()
        except:
            traceback.print_exc()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mm = MainMenu(sqlite=sqlite, admin_mode=True)
    mm.show()
    sys.exit(app.exec_())
