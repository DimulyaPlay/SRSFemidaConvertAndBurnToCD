import sys
import os
from glob import glob
from UI_main_menu import App
from Utils import gather_all, sqlite
if '-gather' in sys.argv:
    gather_all()

app = App(sqlite=sqlite, admin_mode=True)
app.mainloop()
