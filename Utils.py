import glob
import os
import subprocess
import sys
import tempfile
from pydub import AudioSegment
import soundfile as sf
from db_utilities import *
from errors import *
from datetime import datetime
from PyQt5.QtWidgets import QComboBox

current_path = os.getcwd()


def get_server_path():
    with open(current_path + '\\server_db_path.txt', 'r') as sp:
        server_db_path = sp.readline()
        print(server_db_path)
    return server_db_path


dp_path = get_server_path()
sqlite = db_host(dp_path)
AudioSegment.converter = current_path + "\\ffmpeg.exe"
mp3player = current_path + '\\foobar2000\\foobar2000.exe'
cdburnerxp = current_path + '\\CDBurnerXP\\cdbxpcmd.exe'
settings = sqlite.get_settings()
current_media_path = settings['server_media_path']


def open_mp3(mp3path):
    subprocess.Popen(mp3player + ' ' + fr'"{mp3path}"', shell=False)


def write_to_cd(mp3paths):
    if not mp3paths:
        return
    filestr = ''
    for mp3 in mp3paths:
        filestr += fr'-file[\]:"{current_media_path + mp3}" '
    print(cdburnerxp + ' ' + fr'--burn-data -device:0 {filestr} -close -eject')
    sdburnerout = subprocess.Popen(cdburnerxp + ' ' + fr'--burn-data -tao -import -device:0 {filestr}-eject',
                                   shell=False, stdout=subprocess.PIPE)
    return sdburnerout


# def gather_new_names_and_paths_from_cr(cr_name):
#     """
#     gather new courtheatings from folder into courthearings table
#     :param cr_name:
#     :return: list of lists with names and fpaths of new items in courtroom folder
#     """
#     current_ch_df = sqlite.get_courthearings_by_courtroom(cr_name)
#     target_dir = sqlite.get_courtrooms_dict()[cr_name]
#     current_ch_set = set(current_ch_df['foldername'])
#     new_ch_set = set(os.listdir(target_dir))
#     new_ch_set.difference_update(current_ch_set)
#     diff_names_list = list(new_ch_set)
#     diff_namesnpaths_list = [[i, os.path.join(target_dir, i)] for i in diff_names_list if
#                              os.path.isdir(os.path.join(target_dir, i))]
#     return diff_namesnpaths_list


def get_case_date_from_name(ch_name):
    """
    split foldername into case and date
    :param ch_name: foldername
    :return: case str, date str
    """
    ch_name = ch_name.split(' from ')
    date = ch_name[1]
    case = ch_name[0].split('Case #')[1]
    return case, date


def gather_from_courtroom(cr_name, settings, new_folder_path=None):
    """
    gather new audio from one courtroom
    :param new_folder_path: если путь дан, то импортируем только его
    :param settings: parameters
    :param cr_name: courtroomname
    :return:
    """
    convert_audio = settings['audio_convert']
    if not sqlite.is_courhearing_in_table(os.path.basename(new_folder_path)+'/'+cr_name):
        foldername, folderpath = os.path.basename(new_folder_path), new_folder_path
        case, date = get_case_date_from_name(foldername)
    else:
        return 1
    if convert_audio == "1" and current_media_path != '':
        try:
            if not os.path.exists(f'{current_media_path}\\{cr_name}\\'):
                os.mkdir(f'{current_media_path}\\{cr_name}\\')
            filepaths = glob.glob(folderpath + r'\*\*')
            mp3_path = f'{current_media_path}\\{cr_name}\\{foldername}.mp3'
            mp3_path_public = f'\\{cr_name}\\{foldername}.mp3'
            duration = concat_audio_by_time(filepaths, mp3_path)
        except Exception as e:
            mp3_path = ''
            duration = ''
    else:
        mp3_path = ''
        mp3_path_public = ''
        duration = ''
    sqldate = date.split('-')
    sqldate = sqldate[2] + '-' + sqldate[1] + '-' + sqldate[0]
    res = sqlite.add_courthearing(foldername=foldername, case=case, date=date, courtroomname=cr_name,
                                  mp3_path=mp3_path_public,
                                  mp3_duration=duration, sqldate=sqldate, many=True)
    if res == 0:
        return 0
    else:
        return 3


def gather_path(emitter, new_folder_path):
    """
    main gather function for walk over all courtrooms in db
    :return:
    """
    cr_dict = sqlite.get_courtrooms_dict()
    settings = sqlite.get_settings()
    for name, path in cr_dict.items():
        if os.path.dirname(new_folder_path) == path:
            emitter.emit(f'Найдена новая запись {os.path.basename(new_folder_path)} в {name}')
            res = gather_from_courtroom(name, settings, new_folder_path)
            if res > 0:
                emitter.emit('НЕ добавлен ' + name)
            else:
                emitter.emit('Добавлен ' + name)
    sqlite.db.commit()
    emitter.emit(f'{ctime()} - gathering completed')


def concat_audio_by_time(audio_filepaths, outmp3, normalize_volume=False):
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
        print('working on', os.path.basename(audio_path), idx + 1, "of", num_paths)
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
    for key, value in dict(sorted(audio_filepaths_by_time.items())).items():
        if out_sound:
            out_sound += value
        else:
            out_sound = value
    duration = int(len(out_sound) / 1000.0)
    out_sound.export(outmp3)
    for tf in tempfile_list_for_delete:
        os.unlink(tf)
    return duration


def set_to_target_level(sound, target_level):
    difference = target_level - sound.dBFS
    return sound.apply_gain(difference)


def ctime():
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")
