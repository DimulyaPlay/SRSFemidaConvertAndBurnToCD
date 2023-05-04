import sys
import os
import traceback
from glob import glob
from PyQt5 import QtWidgets, uic
from Utils import gather_path, sqlite
from UI_courtrooms_menu import CourtroomsMenu
from UI_settings_menu import SettingsMenu
from UI_search_menu import CasesMenu

# pyinstaller --noconfirm --onedir --console --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffmpeg.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffprobe.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/readme.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/server_db_path.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/foobar2000;foobar2000/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/CDBurnerXP;CDBurnerXP/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/assets;assets/"  "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/StartProgram.py"
# C:\Python36\scripts\pyinstaller.exe --noconfirm --onedir --console --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffmpeg.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffprobe.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/readme.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/server_db_path.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/foobar2000;foobar2000/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/CDBurnerXP;CDBurnerXP/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/assets;assets/"  "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/StartProgram.py"
if '-server_mode' in sys.argv:
    admin_mode = True
else:
    admin_mode = False


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self, sqlite, admin_mode=False):
        super().__init__()
        self.sqlite = sqlite
        uic.loadUi('assets\\main_menu.ui', self)
        pushbutton_cases = self.findChild(QtWidgets.QPushButton, 'pushButton_cases')
        pushbutton_cases.clicked.connect(lambda: self.open_cases_menu())
        pushbutton_courtrooms = self.findChild(QtWidgets.QPushButton, 'pushButton_courtrooms')
        pushbutton_courtrooms.clicked.connect(lambda: self.open_cr_menu())
        pushbutton_settings = self.findChild(QtWidgets.QPushButton, 'pushButton_settings')
        pushbutton_settings.clicked.connect(lambda: self.open_settings())
        if not admin_mode:
            pushbutton_settings.setDisabled(True)

    def open_cr_menu(self):
        try:
            crm = CourtroomsMenu(self, self.sqlite)
            crm.show()
        except:
            traceback.print_exc()
            raise

    def open_cases_menu(self):
        try:
            cm = CasesMenu(self, self.sqlite)
            cm.show()
        except:
            traceback.print_exc()
            raise

    def open_settings(self):
        try:
            sm = SettingsMenu(self, self.sqlite)
            sm.show()
        except:
            traceback.print_exc()
            raise


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mm = MainMenu(sqlite=sqlite, admin_mode=admin_mode)
    mm.show()
    sys.exit(app.exec_())
