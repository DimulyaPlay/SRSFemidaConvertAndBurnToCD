import sqlite3
import pandas as pd
import datetime
from Utils import *


class db_host:
    def __init__(self, db_filepath):
        try:
            self.db = sqlite3.connect(db_filepath, check_same_thread=False)  # disable check safety because only server can write to the DB with one write op at time
            self.cursor = self.db.cursor()
        except:
            popup_msg('Ошибка', f'Не удалость соединиться с БД {db_filepath}')

    """
    COURTROOMS TABLE SECTION - START
    """
    def add_courtroom(self, courtroomname, filepath):
        data_tuple = (courtroomname, filepath)
        try:
            self.cursor.execute(f'INSERT INTO Courtrooms VALUES {data_tuple}')
            self.db.commit()
            return 0
        except Exception as e:
            popup_msg('Ошибка', f'Не удалось добавить зал. Возможно имя повторяется.')
            return e

    def get_courtrooms_dict(self):
        df = pd.read_sql_query("SELECT * FROM Courtrooms", self.db)
        cr_dict = {}
        for idx, row in df.iterrows():
            cr_dict[row['courtroomname']] = row['diskdirectory']
        return cr_dict

    def remove_courtroom(self, courtroomname, withrecords=False):
        try:
            self.cursor.execute(f"DELETE FROM Courtrooms WHERE courtroomname = '{courtroomname}'")
            if withrecords:
                self.cursor.execute(f"DELETE FROM Courthearings WHERE courtroomname = '{courtroomname}'")
            self.db.commit()
            return 0
        except Exception as e:
            popup_msg('Ошибка', f'Не удалось удалить зал, {e}')
            return e

    """
    COURTROOMS TABLE SECTION - END
    
    COURTHEARINGS TABLE SECTION - START
    """

    def add_courthearing(self, foldername, case, date, courtroomname, mp3_path, mp3_duration, sqldate, many=False):
        foldername_courtroomname = foldername + '/' + courtroomname
        data_tuple = (foldername_courtroomname, foldername, case, date, courtroomname, mp3_path, mp3_duration, sqldate)
        try:
            self.cursor.execute(f'INSERT INTO Courthearings VALUES {data_tuple}')
            if not many:
                self.db.commit()

            return 0
        except Exception as e:
            return e

    def remove_courthearing(self, foldername_courtroomname):
        self.cursor.execute('DELETE FROM Courthearings WHERE foldername_cr = ?', (foldername_courtroomname,))
        self.db.commit()

    def is_courhearing_in_table(self, foldername_courtroomname):
        self.cursor.execute(f"SELECT * FROM Courthearings WHERE foldername_cr = ?", (foldername_courtroomname,))
        res = self.cursor.fetchall()
        return True if len(res) > 0 else False

    def get_courthearings_by_prefix_courtroom_and_date(self, cr_name, from_to_date=None, period=None, case_prefix = None):
        query = 'SELECT * FROM Courthearings WHERE '
        if cr_name is not None:
            query += f"courtroomname = '{cr_name}' AND "
        if period is not None:
            now_str = datetime.datetime.now().strftime('%Y-%m-%d')
            query += f"sqldate >= date('{now_str}', '-{period} day') AND "
        if from_to_date is not None:
            query += f"sqldate BETWEEN '{from_to_date[0]}' AND '{from_to_date[1]}' AND "
        query = query[:-5]
        df = pd.read_sql_query(query,  self.db, parse_dates={'date': '%d-%m-%Y'})
        if case_prefix is not None:
            df = df[df['case'].str.startswith(case_prefix)]
        df.sort_values('date', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)
        return df
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
