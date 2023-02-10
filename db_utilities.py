import sqlite3
import pandas as pd
from errors import *


class db_host:
    def __init__(self, db_filepath):
        self.db = sqlite3.connect(db_filepath)
        self.cursor = self.db.cursor()
    """
    COURTROOMS TABLE SECTION - START
    """
    def add_courtroom(self, courtroomname, filepath):
        data_tuple = (courtroomname, filepath)
        self.cursor.execute(f'INSERT INTO Courtrooms VALUES {data_tuple}')
        try:
            self.db.commit()
            return True
        except Exception as e:
            print('Не удалось добавить зал, такое имя уже занято', e)
            show_error("Ошибка", f"Зал не был добавлен, {e}")
            return False

    def get_courtrooms_dict(self):
        df = pd.read_sql_query("SELECT * FROM Courtrooms", self.db)
        cr_dict = {}
        for idx, row in df.iterrows():
            cr_dict[row['courtroomname']] = row['diskdirectory']
        return cr_dict

    def remove_courtroom(self, courtroomname):
        self.cursor.execute(f"DELETE FROM Courtrooms WHERE courtroomname = '{courtroomname}'")
        try:
            self.db.commit()
            return True
        except Exception as e:
            print('Не удалось добавить зал, такое имя уже занято', e)
            show_error("Ошибка", f"Зал не был удален, {e}")
            return False

    """
    COURTROOMS TABLE SECTION - END
    
    COURTHEARINGS TABLE SECTION - START
    """

    def add_courthearing(self, foldername, case, date, courtroomname, mp3_path, mp3_duration):
        foldername_courtroomname = foldername + '/' + courtroomname
        data_tuple = (foldername_courtroomname, foldername, case, date, courtroomname, mp3_path, mp3_duration)
        self.cursor.execute(f'INSERT INTO Courthearings VALUES {data_tuple}')
        try:
            self.db.commit()
            return True
        except Exception as e:
            print('Не удалось добавить заседание, комбинация "имя/зал" уже занята', e)
            return False

    def get_courthearings(self):
        df = pd.read_sql_query("SELECT * FROM Courthearings", self.db)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df.sort_values('date', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)
        return df

    def get_courthearings_by_courtroom(self, cr_name):
        df = pd.read_sql_query(f"SELECT * FROM Courthearings WHERE courtroomname = '{cr_name}'", self.db)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df.sort_values('date', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)
        return df

    def update_courthearing_add_mp3(self, foldername, courtroomname, mp3_path, mp3_duration):
        self.cursor.execute(f"UPDATE Courthearings SET mp3path = '{mp3_path}', mp3duration = '{mp3_duration}' WHERE foldername_cr = '{foldername+'/'+courtroomname}'")
        try:
            self.db.commit()
            print(f'{foldername} updated')
        except Exception as e:
            show_error('Ошибка', f'Ошибка обновления записи: {e}')

    """
    COURTHEARINGS TABLE SECTION - END
    
    SETTING TABLE SECTION - START
    """
    def get_settings(self):
        df = pd.read_sql_query("SELECT * FROM Settings", self.db)
        settings = {}
        for idx, row in df.iterrows():
            settings[row['settingname']] = row['settingvalue']
        return settings

    def update_settings(self, settings_dict):
        for key, value in settings_dict.items():
            self.cursor.execute(f"UPDATE Settings SET settingvalue = '{value}' WHERE settingname = '{key}'")
        try:
            self.db.commit()
            print('Settings updated')
        except Exception as e:
            show_error('Ошибка', f'Ошибка обновления параметров: {e}')

    """
    SETTING TABLE SECTION - END
    """
