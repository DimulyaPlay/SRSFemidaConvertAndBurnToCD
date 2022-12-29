import sys
from glob import glob

from UI_main_menu import App
from Utils import *

if '-gather' in sys.argv:
    gather_all()

fps = glob(r'C:\Залы\зал 3\Case #1-402$2F2022 from 27-12-2022\*\*')
concat_audio_by_channels(fps)
app = App(sqlite=sqlite, admin_mode=True)
app.mainloop()
