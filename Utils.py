import glob
import os
import subprocess
import sys
from db_utilities import *
import pandas as pd
from threading import Thread
from time import sleep
from pydub import AudioSegment
import soundfile as sf
import tempfile
import clr
import tkinter as tk
from errors import *
current_path = os.getcwd()
clr.AddReference(current_path+'\\csburnermodule\\CDBurnerModule.dll')
from CDBurnerModule import CDBurner


sqlite = db_host(current_path+'\\courtrooms.db')
AudioSegment.converter = current_path+"\\ffmpeg.exe"
mp3player = current_path + '\\foobar2000\\foobar2000.exe'


def wait_for_rom_ready(drive):
    """
    Listening for the dvdrom is ready for burning
    :return:
    """
    status_media = CDBurner.IsDriveReady(drive)
    while status_media != 0:
        print('waiting for disk in drive', drive)
        sleep(1)
        status_media = CDBurner.IsDriveReady(drive)
    return


def burn_mp3_files_to_disk(filelist, drive=0):
    wait_for_rom_ready(drive)
    CDBurner.BurnFiles(filelist, drive, True)
    print('successfully writed')


def open_mp3(mp3path):
    subprocess.Popen(mp3player+' '+fr'"{mp3path}"', shell=False)


def gather_new_names_and_paths_from_cr(cr_name):
    """
    gather new courtheatings from folder into courthearings table
    :param cr_name:
    :return: list of lists with names and fpaths of new items in courtroom folder
    """
    current_ch_df = sqlite.get_courthearings_by_courtroom(cr_name)
    target_dir = sqlite.get_courtrooms_dict()[cr_name]
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
    convert_audio = settings['audio_convert']
    print('found', len(names_and_paths), 'records in', cr_name)
    for name, path in names_and_paths:
        case, date = gather_case_date_from_name(name)
        if convert_audio == "1":
            try:
                filepaths = glob.glob(path+r'\*\*')
                mp3_path = f'{mp3_root_path}\\{cr_name}\\{name}.mp3'
                duration = concat_audio_by_time(filepaths, mp3_path)
            except Exception as e:
                print('error on converting audio', name, e)
                mp3_path = ''
                duration = ''
                pass
        else:
            mp3_path = ''
            duration = ''
        if sqlite.add_courthearing(foldername = name, case = case, date = date, courtroomname = cr_name, mp3_path = mp3_path, mp3_duration = duration):
            print(case,' added')
        else:
            print(case,' not added')


def gather_all():
    """
    main gather function for walk over all courtrooms in db
    :return:
    """
    cr_dict = sqlite.get_courtrooms_dict()
    settings = sqlite.get_settings()
    print('start gathering from', len(cr_dict), 'courtrooms')
    for name, path in cr_dict.items():
        print('gathering from', name)
        gather_from_courtroom(name, settings)
        print('gathering from',name, 'complete')
    print('gathering successfully completed')


def convert_to_mp3(ch_foldername, cr_name, c):
    cr_folder = sqlite.get_courtrooms_dict()[cr_name]
    folder_to_convert = cr_folder + '\\' + ch_foldername
    filepaths = glob.glob(folder_to_convert + r'\*\*')
    mp3_path = f'{sqlite.get_settings()["mp3_path"]}\\{cr_name}\\{ch_foldername}.mp3'
    if not os.path.exists(f'{sqlite.get_settings()["mp3_path"]}\\{cr_name}\\'):
        os.mkdir(f'{sqlite.get_settings()["mp3_path"]}\\{cr_name}\\')
    duration = concat_audio_by_time(filepaths, mp3_path)
    sqlite.update_courthearing_add_mp3(ch_foldername, cr_name, mp3_path, duration)
    c = {}


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
    def __init__(self, master, **kwargs):
        self.outer = customtkinter.CTkFrame(master, bg_color='transparent', fg_color='transparent')
        self.vsb = customtkinter.CTkScrollbar(self.outer, orientation=tk.VERTICAL, corner_radius=10)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas = tk.Canvas(self.outer, highlightthickness=0, background='gray14')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
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
            return getattr(self.outer, item)
        else:
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
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def __str__(self):
        return str(self.outer)
