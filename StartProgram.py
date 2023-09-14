import sys
from Utils import sqlite
from UI_settings_menu import SettingsMenu
from UI_main_menu import MainUi
from PyQt5.QtWidgets import QApplication

# pyinstaller --noconfirm --onedir --console --windowed --icon "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/assets/avatar.png" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffmpeg.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/ffprobe.exe;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/readme.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/server_db_path.txt;." --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/foobar2000;foobar2000/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/CDBurnerXP;CDBurnerXP/" --add-data "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/assets;assets/"  "C:/Users/CourtUser/Desktop/release/SRSFemidaConvertAndBurnToCD/StartProgram.py"

if '-server_mode' in sys.argv:
    admin_mode = True
else:
    admin_mode = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if admin_mode:
        mm = SettingsMenu(sqlite=sqlite)
        mm.show()
    else:
        mm = MainUi(sqlite = sqlite)
        mm.refill_search_table()
        mm.show()
    sys.exit(app.exec_())
