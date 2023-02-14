import sys
import os
from glob import glob
from PyQt5 import QtWidgets as qtw
from UI_main_menu import MainMenu
from Utils import gather_all, sqlite
if '-gather' in sys.argv:
    gather_all()


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook
# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook
app = qtw.QApplication(sys.argv)
mm = MainMenu(sqlite=sqlite, admin_mode=True)
sys.exit(app.exec_())
