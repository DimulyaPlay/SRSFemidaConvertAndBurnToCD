import os
import sys
import pandas as pd
from threading import Thread
from time import sleep
import pydub
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
pydub.AudioSegment.converter = current_path+"\\ffmpeg.exe"


def wait_for_rom_ready():
    """
    Listening for the dvdrom is ready for burning
    :return:
    """
    status_media = CDBurner.IsDriveReady(0)
    while status_media != 0:
        sleep(1)
        status_media = CDBurner.IsDriveReady(0)
    return


def get_cr_table():
    """
    getting full courtrooms table from DB
    :return: table as df
    """
    return pd.DataFrame(sqlite.select_as_dataframe(table_name="Courtrooms"))


def get_ch_table():
    """
    getting all courthearings table from DB
    :return: table as df
    """
    return pd.DataFrame(sqlite.select_as_dataframe(table_name="Courthearings"))


def get_settings_table():
    """
    getting all settings table from DB
    :return: table as dict
    """
    df = pd.DataFrame(sqlite.select_as_dataframe(table_name="Settings"))
    settings = {}
    for idx, row in df.iterrows():
        settings[row['settingname']] = row['settingvalue']
    return settings


def get_cr_dict_by_cr_name(cr_name):
    """
    getting a courtroom dict by name
    :param cr_name: courtroom name
    :return: ordered dict of courtroom params
    """
    cr_dict = sqlite.select_as_dict(table_name="Courtrooms", where=Where(key='courtroomname', value=cr_name))
    return cr_dict


def get_ch_table_by_cr_name(cr_name):
    """
    getting courthearings table where coutroom==cr_name
    :param cr_name: name of the courtroom
    :return: courthearings df from only one courtroom
    """
    return pd.DataFrame(sqlite.select_as_dataframe(table_name="Courthearings", where=Where(key='courtroomname', value=cr_name)))


def update_settings_table(settings_dict):
    """
    replacing ALL setting by new and old parameters from dict
    todo: change replacing by modifying only changes
    :param settings_dict: current_settings dictionary
    :return:
    """
    for key, value in settings_dict.items():
        sqlite.delete(table_name='Settings', where=Where(key='settingname', value=key))
        sqlite.insert(table_name='Settings', record=[key, value, ' ', ' '])


def add_cr_to_sql(cr_name,cr_path):
    """
    add new courtroom to the courtrooms table
    :param cr_name: name attribute
    :param cr_path: folderpath attribute(without ending slash)
    :return:
    """
    sqlite.insert(table_name='Courtrooms', record = [cr_name, cr_path, ' ', ' '])


def add_ch_to_sql(foldername, case, date, courtroomname, mp3_path):
    sqlite.insert(table_name='Courthearings', record = [foldername, case, date, courtroomname, mp3_path, ' ', ' '])


def del_cr_from_sql(cr_name):
    """
    del courtroom from courtrooms table
    :param cr_name: name attribute
    :return:
    """
    sqlite.delete(table_name='Courtrooms', where=Where(key='courtroomname', value=cr_name))


def gather_new_names_and_paths_from_cr(cr_name):
    """
    gather new courtheatings from folder into courthearings table
    :param cr_name:
    :return: list of lists with names and fpaths of new items in courtroom folder
    """
    current_ch_df = get_ch_table_by_cr_name(cr_name)
    target_dir = get_cr_dict_by_cr_name(cr_name)[0]['diskdirectory']
    current_ch_set = set(current_ch_df['foldername'])
    new_ch_set = set(os.listdir(target_dir))
    new_ch_set.difference_update(current_ch_set)
    diff_names_list = list(new_ch_set)
    diff_namesnpaths_list = [[i,os.path.join(target_dir,i)] for i in diff_names_list if os.path.isdir(os.path.join(target_dir,i))]
    return diff_namesnpaths_list


def gather_case_date_from_name(ch_name):
    """
    split foldername into case and date
    :param ch_name: foldername
    :return: case str, date str
    """
    ch_name = ch_name.split(' from ')
    date = ch_name[1]
    case = ch_name[0].split('Case ')[1]
    return case, date


def gather_from_courtroom(cr_name, convert_audio):
    """
    gather new audio from one courtroom
    :param cr_name:
    :param convert_audio: bool is we need to convert to mp3
    :return:
    """
    names_and_paths = gather_new_names_and_paths_from_cr(cr_name)
    print('found', len(names_and_paths), 'records in', cr_name)
    for name, path in names_and_paths:
        case, date = gather_case_date_from_name(name)
        if convert_audio:
            mp3_path = ''
        else:
            mp3_path = ''
        try:
            add_ch_to_sql(foldername = name, case = case, date = date, courtroomname = cr_name, mp3_path = mp3_path)
            print(case,date,'added to DB')
        except Exception as e:
            print('error on appending to DB', e)
            pass


def gather_all():
    """
    main gather function for walk over all courtrooms in db
    :return:
    """
    cr_df = get_cr_table()
    print('start gathering from', len(cr_df), 'courtrooms')
    for idx, row in cr_df.iterrows():
        print('gathering from', row['courtroomname'])
        gather_from_courtroom(row['courtroomname'], False)
        print('gathering from',row['courtroomname'], 'complete')
    print('gathering successfully completed')


def concat_audio_by_time(audio_filepaths):
    """
    groupping filepaths by time (all channels into one file)
    :param audio_filepaths: glob from audiopath
    :return: dict{time:audiosegment}
    """
    audio_filepaths = [i for i in audio_filepaths if i.endswith('.WAV')]
    print(audio_filepaths)
