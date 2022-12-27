import os
import sys
from threading import Thread
from time import sleep
import clr
from simplesqlite import SimpleSQLite
current_path = os.getcwd()
clr.AddReference(current_path+'\\csburnermodule\\CDBurnerModule.dll')
from CDBurnerModule import CDBurner

# gg = CDBurner.IsDriveReady(0)
# print(gg, type(gg))
# CDBurner.BurnFiles(["C:\\Users\\CourtUser\\Downloads\\59RS0025-212-22-0000017_all_files.zip"], 0, True)
sqlite = SimpleSQLite(current_path+'\\courtrooms.db')


def wait_for_rom_ready():
    status_media = CDBurner.IsDriveReady(0)
    while status_media != 0:
        sleep(1)
        status_media = CDBurner.IsDriveReady(0)
    return True
