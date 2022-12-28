import os
import sys
import pandas as pd
from threading import Thread
from time import sleep
import clr
from simplesqlite import SimpleSQLite
from simplesqlite.query import Where
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


def get_cr_table():
    return pd.DataFrame(sqlite.select_as_dataframe(table_name="Courtrooms"))


def get_settings_table():
    df = pd.DataFrame(sqlite.select_as_dataframe(table_name="Settings"))
    settings = {}
    for idx, row in df.iterrows():
        settings[row['settingname']] = row['settingvalue']
    return settings


def update_settings_table(settings_dict):
    for key, value in settings_dict.items():
        sqlite.delete(table_name='Settings', where=Where(key='settingname', value=key))
        sqlite.insert(table_name='Settings', record=[key, value, ' ', ' '])


def add_cr_to_sql(name,path):
    sqlite.insert(table_name='Courtrooms', record = [name, path, ' ', ' '])


def del_cr_from_sql(name):
    sqlite.delete(table_name='Courtrooms', where=Where(key='courtroomname', value=name))
