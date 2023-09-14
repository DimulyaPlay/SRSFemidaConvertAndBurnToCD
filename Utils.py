import glob
import os
import subprocess
import sys
import tempfile
import traceback
import time
import eyed3
from pydub import AudioSegment
import soundfile as sf
from db_utilities import *
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QDateTime, Qt
import shutil
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QProgressBar, QMessageBox
import win32file
import ctypes
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


def popup_msg(title, message):
    QMessageBox.about(None, title, message)


def get_drive_type(drive_letter):
    try:
        drive_path = f"{drive_letter}:\\"
        drive_type = win32file.GetDriveType(drive_path)
        return drive_type
    except Exception as e:
        return None


def get_drive_labels():
    drive_labels = {}
    drives = [f"{chr(drive)}:\\" for drive in range(65, 91) if os.path.exists(f"{chr(drive)}:")]

    for drive in drives:
        label = ctypes.create_unicode_buffer(256)
        file_system = ctypes.create_unicode_buffer(256)
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive),
            label,
            ctypes.sizeof(label),
            None,
            None,
            None,
            file_system,
            ctypes.sizeof(file_system)
        )
        drive_labels[drive] = label.value

    return drive_labels


def open_mp3(mp3path):
    if mp3path:
        subprocess.Popen(mp3player + ' ' + fr'"{mp3path}"', shell=False)
    else:
        print('No mp3')
        pass


def write_to_cd(mp3paths):
    if not mp3paths:
        return
    filestr = ''
    for mp3 in mp3paths:
        filestr += fr'-file[\]:"{mp3}" '
    sdburnerout = subprocess.Popen(cdburnerxp + ' ' + fr'--burn-data -tao -import -device:0 {filestr}-eject',
                                   shell=False, stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
    return sdburnerout


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
    diff_namesnpaths_list = [[i, os.path.join(target_dir, i)] for i in diff_names_list if
                             os.path.isdir(os.path.join(target_dir, i))]
    return diff_namesnpaths_list


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
    if not sqlite.is_courhearing_in_table(os.path.basename(new_folder_path)+'/'+cr_name):
        foldername, folderpath = os.path.basename(new_folder_path), new_folder_path
        case, date = get_case_date_from_name(foldername)
    else:
        return 1  # если уже есть в таблице
    try:
        if not os.path.exists(f'{current_media_path}\\{cr_name}\\'):
            os.mkdir(f'{current_media_path}\\{cr_name}\\')
        globpath = folderpath + r'\*\*'
        filepaths = glob.glob(globpath)
        mp3_path = f'{current_media_path}\\{cr_name}\\{foldername}.mp3'
        mp3_path_public = f'\\{cr_name}\\{foldername}.mp3'
        duration = concat_audio_by_time(filepaths, mp3_path)
    except Exception:
        traceback.print_exc()
        return 3  # если не удалось сконвертировать
    if duration == 'empty':
        return 2
    sqldate = date.split('-')
    sqldate = sqldate[2] + '-' + sqldate[1] + '-' + sqldate[0]
    res = sqlite.add_courthearing(foldername=foldername, case=case, date=date, courtroomname=cr_name,
                                  mp3_path=mp3_path_public,
                                  mp3_duration=duration, sqldate=sqldate, many=True)
    if res == 0:
        return 0
    else:
        return res


def gather_path(logger, new_folder_path):
    """
    main gather function for walk over all courtrooms in db
    :return:
    """
    cr_dict = sqlite.get_courtrooms_dict()
    settings = sqlite.get_settings()
    for name, path in cr_dict.items():
        if os.path.dirname(new_folder_path) == path:
            logger.emit(f'{ctime()} - {name} - Найдена новая запись {os.path.basename(new_folder_path)}')
            res = gather_from_courtroom(name, settings, new_folder_path)
    sqlite.db.commit()
    return res


def concat_audio_by_time(audio_filepaths, outmp3, normalize_volume=False):
    """
    groupping filepaths by time (all channels into one file)
    :param outmp3: file to save converted mp3
    :param normalize_volume: normalize all volumes to value in Db
    :param audio_filepaths: glob from audiopath
    :return: dict{time:audiosegment}
    """
    s_time = time.time()
    audio_filepaths = [i for i in audio_filepaths if i.endswith('.WAV')]
    if not audio_filepaths:
        return 'empty'
    audio_filepaths_by_time = {}
    tempfile_list_for_delete = []
    for idx, audio_path in enumerate(audio_filepaths):
        try:
            audio_time_suffix = os.path.basename(audio_path).split('.')[0].split(' ')[-1]
            data, sr = sf.read(audio_path)
            sig, sr = sf.read(audio_path)
            fd, outpath = tempfile.mkstemp('.wav')
            tempfile_list_for_delete.append(outpath)
            os.close(fd)
            sf.write(outpath, sig, sr, format="wav", subtype='PCM_16')
            sound1 = AudioSegment.from_wav(outpath)
            if normalize_volume:
                sound1 = set_to_target_level(sound1, normalize_volume)
            if audio_time_suffix in audio_filepaths_by_time.keys():
                audio_filepaths_by_time[audio_time_suffix].overlay(sound1)
            else:
                audio_filepaths_by_time[audio_time_suffix] = sound1
        except Exception:
            traceback.print_exc()
            return ''
    try:
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
    except Exception:
        traceback.print_exc()
        return ''
    checkfile = eyed3.load(outmp3)
    if checkfile is None:
        print('mp3 check fail')
        return ''
    else:
        print('mp3 checked successfully, converted in ', time.time()-s_time, ' сек.')
    return duration


def set_to_target_level(sound, target_level):
    difference = target_level - sound.dBFS
    return sound.apply_gain(difference)


def ctime():
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")


class Worker(QThread):
    def __init__(self, file_list):
        super().__init__()
        self.file_list = file_list

    intReady = pyqtSignal(int)
    strReady = pyqtSignal(str)

    @pyqtSlot()
    def run(self):
        self.strReady.emit('Подготовка к записи.')
        sdburnerout = write_to_cd(self.file_list)
        finished = False
        error = 0
        while not finished:
            line = sdburnerout.stdout.readline()
            line2 = line.decode().replace('\n', '').replace('\r', '')
            print(line2)
            self.strReady.emit('Идет запись, подождите.')
            if line2.endswith('%'):
                self.strReady.emit('Идет запись, подождите.')
                self.intReady.emit(int(line2[:-1]))
            if 'An error (275) occured' in line2:
                self.strReady.emit('Неподдреживаемая файловая система. Попробуйте другой метод')
                error = 1
                alternative_write = CopyUsbDialog(self.file_list)
                alternative_write.exec_()
                break
            if not line:
                break
        if not error:
            self.strReady.emit('Запись успешно завершена!')


class StartBurningProcessWithBar(QtWidgets.QDialog):
    def __init__(self, root, list_to_write):
        super().__init__(parent=root)
        self.root = root
        self.list_to_write = list_to_write
        self.setWindowTitle("Запись на диск")
        self.setFixedSize(470, 70)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 5, 450, 25))
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(QtCore.QRect(10, 30, 450, 30))
        self.pbar.setAlignment(QtCore.Qt.AlignCenter)
        self.show()
        self.start_worker()

    def setPbarValue(self, value):
        self.pbar.setValue(value)

    def setLabelText(self, string):
        self.label.setText(string)

    def start_worker(self):
        self.show()
        as_disk = 0
        available_drives = [f"{chr(drive)}:\\" for drive in range(65, 91) if os.path.exists(f"{chr(drive)}:")]
        dvdrom_drives = [drive for drive in available_drives if get_drive_type(drive[0]) == win32file.DRIVE_CDROM]
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")
        folder_name = f"Аудиозаписи-{current_datetime}"
        if dvdrom_drives:
            try:
                # если мы можем создать директорию, значит файловая система позволяет копирование на нее
                destination = os.path.join(dvdrom_drives[0], folder_name)
                os.mkdir(destination)
            except PermissionError:
                traceback.print_exc()
                print('unable to write on disk as files')
                # иначе будем записывать с помощью cdburnerxp
                as_disk = 1
        if dvdrom_drives and not as_disk:
            self.setLabelText('Запись на диск. По окончании откроется папка с записями.')
            self.copyThread = CopyThread(self.list_to_write)
            self.copyThread.update_progress.connect(self.setPbarValue)
            self.copyThread.destination = destination
            self.copyThread.start()
        else:
            self.thread = QThread()
            self.worker = Worker(self.list_to_write)
            self.worker.moveToThread(self.thread)
            self.worker.intReady.connect(self.setPbarValue)
            self.worker.strReady.connect(self.setLabelText)
            self.thread.started.connect(self.worker.run)
            self.thread.start()


class CopyThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, source):
        super().__init__()
        self.source = source
        self.destination = None

    def run(self):
        for i, file in enumerate(self.source):
            shutil.copy(file, self.destination)
            progress = int(((i + 1) / len(self.source)) * 100)
            self.update_progress.emit(progress)
        os.startfile(self.destination)


class CopyUsbDialog(QDialog):
    def __init__(self, file_paths):
        super().__init__()
        self.setWindowTitle("Выберите диск для сохранения")

        layout = QVBoxLayout()

        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.progressBar)

        self.copyThread = CopyThread(file_paths)
        self.copyThread.update_progress.connect(self.update_progress_bar)
        self.copyThread.finished.connect(self.copy_finished)
        available_drives = [f"{chr(drive)}:\\" for drive in range(65, 91) if os.path.exists(f"{chr(drive)}:")]
        drive_labels = get_drive_labels()
        for drive in available_drives:
            drive_button = QtWidgets.QPushButton(f"Сохранить на диске {drive} ({drive_labels[drive]})")
            drive_button.clicked.connect(lambda checked, drive=drive: self.start_copying(drive))
            layout.addWidget(drive_button)
        self.setLayout(layout)

    def start_copying(self,drive):
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss")
        folder_name = f"Аудиозаписи-{current_datetime}"
        destination = os.path.join(drive, folder_name)
        self.progressBar.setValue(0)
        os.makedirs(destination)
        self.copyThread.destination = destination
        self.copyThread.start()

    def update_progress_bar(self, progress):
        self.progressBar.setValue(progress)

    def copy_finished(self):
        self.progressBar.setValue(100)
