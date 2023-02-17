import sys
import os
from glob import glob
from PyQt5 import QtWidgets as qtw
from UI_main_menu import MainMenu
from Utils import gather_all, sqlite
if '-gather' in sys.argv:
    gather_all()
    sys.exit(0)

if '-server_mode' in sys.argv:
    admin_mode = True
else:
    admin_mode = False


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys._excepthook = sys.excepthook
sys.excepthook = my_exception_hook
app = qtw.QApplication(sys.argv)
mm = MainMenu(sqlite=sqlite, admin_mode=admin_mode)
sys.exit(app.exec_())
