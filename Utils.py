import glob
import os
import subprocess
import sys

import customtkinter
import pandas as pd
from threading import Thread
from time import sleep
from pydub import AudioSegment
import soundfile as sf
import tempfile
import clr
from simplesqlite import SimpleSQLite
from simplesqlite.query import Where, QueryItem
import tkinter as tk
current_path = os.getcwd()
clr.AddReference(current_path+'\\csburnermodule\\CDBurnerModule.dll')
from CDBurnerModule import CDBurner

# gg = CDBurner.IsDriveReady(0)
# print(gg, type(gg))
# CDBurner.BurnFiles(["C:\\Users\\CourtUser\\Downloads\\59RS0025-212-22-0000017_all_files.zip"], 0, True)
sqlite = SimpleSQLite(current_path+'\\courtrooms.db')
AudioSegment.converter = current_path+"\\ffmpeg.exe"
mp3player = current_path + '\\foobar2000\\foobar2000.exe'


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


def open_mp3(mp3path):
    subprocess.Popen(mp3player+' '+fr'"{mp3path}"', shell=False)


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
    df = pd.DataFrame(sqlite.select_as_dataframe(table_name="Courthearings", where=Where(key='courtroomname', value=cr_name)))
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df.sort_values('date', inplace=True, ascending=False)
    df.reset_index(drop=True, inplace=True)
    return df


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


def add_ch_to_sql(foldername, case, date, courtroomname, mp3_path, mp3_duration):
    sqlite.insert(table_name='Courthearings', record = [foldername, case, date, courtroomname, mp3_path, mp3_duration,' ', ' '])


def edit_ch_sql(foldername, mp3_path, mp3_duration):
    sqlite.update(table_name='Courthearings', set_query=f"mp3path = '{mp3_path}', mp3duration = '{mp3_duration}'", where=Where(key='foldername', value=foldername))


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
    case = ch_name[0].split('Case #')[1]
    return case, date


def gather_from_courtroom(cr_name, settings):
    """
    gather new audio from one courtroom
    :param settings: parameters
    :param cr_name: courtroomname
    :return:
    """
    names_and_paths = gather_new_names_and_paths_from_cr(cr_name)
    mp3_root_path = settings['mp3_path']
    convert_audio = bool(settings['audio_convert'])
    print('found', len(names_and_paths), 'records in', cr_name)
    for name, path in names_and_paths:
        case, date = gather_case_date_from_name(name)
        if convert_audio:
            try:
                filepaths = glob.glob(path+r'\*\*')
                mp3_path = mp3_root_path + '\\' + name + '.mp3'
                duration = concat_audio_by_time(filepaths, mp3_path)
            except Exception as e:
                print('error on converting audio', name, e)
                mp3_path = ''
                duration = ''
                pass
        else:
            mp3_path = ''
            duration = ''
        try:
            add_ch_to_sql(foldername = name, case = case, date = date, courtroomname = cr_name, mp3_path = mp3_path, mp3_duration = duration)
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
    settings = get_settings_table()
    print('start gathering from', len(cr_df), 'courtrooms')
    for idx, row in cr_df.iterrows():
        print('gathering from', row['courtroomname'])
        gather_from_courtroom(row['courtroomname'], settings)
        print('gathering from',row['courtroomname'], 'complete')
    print('gathering successfully completed')


def convert_to_mp3(ch_foldername, cr_name):
    cr_folder = get_cr_dict_by_cr_name(cr_name)[0]['diskdirectory']
    folder_to_convert = cr_folder + '\\' + ch_foldername
    filepaths = glob.glob(folder_to_convert + r'\*\*')
    mp3_path = get_settings_table()['mp3_path'] + '\\' + ch_foldername + '.mp3'
    duration = concat_audio_by_time(filepaths, mp3_path)
    edit_ch_sql(ch_foldername, mp3_path, duration)


def concat_audio_by_time(audio_filepaths, outmp3, normalize_volume = False):
    """
    groupping filepaths by time (all channels into one file)
    :param outmp3: file to save converted mp3
    :param normalize_volume: normalize all volumes to value in Db
    :param audio_filepaths: glob from audiopath
    :return: dict{time:audiosegment}
    """
    audio_filepaths = [i for i in audio_filepaths if i.endswith('.WAV')]
    audio_filepaths_by_time = {}
    tempfile_list_for_delete = []
    num_paths = len(audio_filepaths)
    for idx, audio_path in enumerate(audio_filepaths):
        print('working on', os.path.basename(audio_path), idx+1,"of",num_paths)
        audio_time_suffix = os.path.basename(audio_path).split('.')[0].split(' ')[-1]
        data, sr = sf.read(audio_path)

        sig, sr = sf.read(audio_path)
        fd, outpath = tempfile.mkstemp('.wav')
        tempfile_list_for_delete.append(outpath)
        os.close(fd)
        sf.write(outpath, sig, sr, format="wav", subtype='PCM_16')
        sound1 = AudioSegment.from_wav(outpath)
        if normalize_volume:
            print('normalizing to', normalize_volume, 'Db')
            sound1 = set_to_target_level(sound1, normalize_volume)
        if audio_time_suffix in audio_filepaths_by_time.keys():
            audio_filepaths_by_time[audio_time_suffix].overlay(sound1)
        else:
            audio_filepaths_by_time[audio_time_suffix] = sound1
    out_sound = None
    print('last combining')
    for key, value in dict(sorted(audio_filepaths_by_time.items())).items():
        if out_sound:
            out_sound += value
        else:
            out_sound = value
    duration = int(len(out_sound)/1000.0)
    print('saving file with duration', duration)
    out_sound.export(outmp3)
    print('clearing temp')
    for tf in tempfile_list_for_delete:
        os.unlink(tf)
    return duration


def set_to_target_level(sound, target_level):
    difference = target_level - sound.dBFS
    return sound.apply_gain(difference)


class VerticalScrolledFrame:
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    :width:, :height:, :bg: are passed to the underlying Canvas
    :bg: and all other keyword arguments are passed to the inner Frame
    note that a widget layed out in this frame will have a self.master 3 layers deep,
    (outer Frame, Canvas, inner Frame) so
    if you subclass this there is no built in way for the children to access it.
    You need to provide the controller separately.
    """
    def __init__(self, master, **kwargs):
        self.outer = customtkinter.CTkFrame(master, bg_color='transparent', fg_color='transparent')

        self.vsb = customtkinter.CTkScrollbar(self.outer, orientation=tk.VERTICAL, corner_radius=10)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas = tk.Canvas(self.outer, highlightthickness=0, background='gray14')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview

        self.inner = customtkinter.CTkFrame(self.canvas, bg_color='transparent', fg_color='transparent')
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(0, 0, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

    def __str__(self):
        return str(self.outer)