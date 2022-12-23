import os
import sys

import clr
from simplesqlite import SimpleSQLite
from UI_main_menu import App

current_path = os.getcwd()
print(current_path)
# clr.AddReference(current_path+'\\csmodule\\csburning.dll')
ssl = SimpleSQLite(current_path+'\\courtrooms.db')
print(res)
app = App(sqlite=ssl, admin_mode=True)
app.mainloop()
