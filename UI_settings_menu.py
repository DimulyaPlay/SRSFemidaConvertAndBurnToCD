# -*- coding: utf-8 -*-
import os
import traceback
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from Utils import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue


class SettingsMenu(QtWidgets.QMainWindow):
    def __init__(self, sqlite):
        super(SettingsMenu, self).__init__()
        self.sqlite = sqlite
        self.settings = sqlite.get_settings()
        self.courtrooms = sqlite.get_courtrooms_dict()
        self.setWindowTitle("Сервер Femida Archive Wizard")
        self.setFixedSize(539, 431)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.tabBarClicked.connect(self.apply_settings)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 539, 431))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.crooms_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.crooms_tab, "Залы")
        self.addCourtroomButton = QtWidgets.QPushButton(self.crooms_tab, clicked=lambda: self.add_crroom())
        self.addCourtroomButton.setGeometry(QtCore.QRect(10, 10, 111, 31))
        self.addCourtroomButton.setText("Добавить зал")
        self.removeCourtroomButton = QtWidgets.QPushButton(self.crooms_tab, clicked = lambda: self.remove_crroom())
        self.removeCourtroomButton.setGeometry(QtCore.QRect(125, 10, 171, 31))
        self.removeCourtroomButton.setText("Удалить выбранный зал")
        self.mylist_listWidget = QtWidgets.QListWidget(self.crooms_tab)
        self.mylist_listWidget.setGeometry(QtCore.QRect(10, 50, 511, 351))
        self.cr_name_path_dict = {}
        for name, path in self.courtrooms.items():
            row = name + '\n' + fr'{path}'
            self.mylist_listWidget.addItem(row)
            self.cr_name_path_dict[row] = name
        self.schedule_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.schedule_tab, "Запуск сканирования")
        self.spinBox_period = QtWidgets.QSpinBox(self.schedule_tab)
        self.spinBox_period.setGeometry(QtCore.QRect(481, 10, 41, 20))
        self.spinBox_period.setValue(3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spinBox_period.setFont(font)
        self.spinBox_period.setMinimum(1)
        self.label_period = QtWidgets.QLabel(self.schedule_tab)
        self.label_period.setGeometry(QtCore.QRect(290, 10, 173, 21))
        self.label_period.setFont(font)
        self.label_period.setText("Задержка сканирования, мин")
        self.label_period.setToolTip('Промежуток времени через который начинать обрабатывать папку\n с момента ее обнаружения(фемида не мгновенно '
                                     'копирует \n все файлы сз на сервер. Необходимо некоторое время,\n чтобы все файлы скопировались в папку и обработались корректно)')
        self.pushButton_start = QtWidgets.QPushButton(self.schedule_tab, clicked = lambda:self.start_worker_scan())
        self.pushButton_start.setGeometry(QtCore.QRect(290, 40, 241, 41))
        self.pushButton_start.setFont(font)
        self.pushButton_start.setText("Запустить сканирование")
        self.pushButton_stop = QtWidgets.QPushButton(self.schedule_tab, clicked = lambda:self.stop_worker_scan())
        self.pushButton_stop.setGeometry(QtCore.QRect(290, 90, 241, 41))
        self.pushButton_stop.setFont(font)
        self.pushButton_stop.setText("Остановить сканирование")
        self.label_status = QtWidgets.QLabel(self.schedule_tab)
        self.label_status.setGeometry(QtCore.QRect(300, 140, 231, 41))
        self.label_status.setFont(font)
        self.label_status.setText("Текущий статус: ОСТАНОВЛЕНО")
        self.plainTextEdit_logger = QtWidgets.QPlainTextEdit(self.schedule_tab)
        self.plainTextEdit_logger.setGeometry(QtCore.QRect(10, 190, 511, 211))
        self.plainTextEdit_logger.setReadOnly(True)
        self.plainTextEdit_logger.appendPlainText('SRS Femida Archive Wizard v1.0 \nРазработка: Краснокамский суд ПК, Дмитрий Соснин, 2023. github.com/dimulyaplay')
        label_server = QtWidgets.QLabel(self.schedule_tab)
        label_server.setText("Сетевая папка для чтения mp3 клиентом")
        label_server.setGeometry(QtCore.QRect(10, 40, 251, 20))
        self.mp3_save_path_server = QtWidgets.QLineEdit(self.schedule_tab)
        self.mp3_save_path_server.setGeometry(QtCore.QRect(10, 60, 251, 20))
        if self.settings['server_media_path'] == '':
            self.mp3_save_path_server.setPlaceholderText(r"Пример: \\server\audio_db")
        else:
            self.mp3_save_path_server.setText(self.settings['server_media_path'])

    def add_crroom(self):
        add_courtroom = QtWidgets.QDialog(parent=self)
        add_courtroom.setFixedSize(277, 91)
        add_courtroom.setWindowTitle("Добавить зал")
        cr_name_line = QtWidgets.QLineEdit(add_courtroom)
        cr_name_line.setGeometry(QtCore.QRect(10, 10, 261, 20))
        cr_name_line.setPlaceholderText("Введите название, например: Зал 1")
        cr_path_line = QtWidgets.QLineEdit(add_courtroom)
        cr_path_line.setGeometry(QtCore.QRect(10, 40, 261, 20))
        cr_path_line.setPlaceholderText(r"Введите путь, например: С:\Залы\Зал 1")
        save_cancel_button = QtWidgets.QDialogButtonBox(parent = add_courtroom, orientation = QtCore.Qt.Horizontal)
        save_cancel_button.setGeometry(QtCore.QRect(60, 60, 161, 31))
        save_cancel_button.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        save_cancel_button.accepted.connect(lambda: add_room_to_base())  # type: ignore
        save_cancel_button.rejected.connect(add_courtroom.reject)  # type: ignore
        add_courtroom.show()

        def add_room_to_base():
            name = fr'{cr_name_line.text()}'.strip()
            path = fr'{cr_path_line.text()}'
            if os.path.exists(path):
                res = self.sqlite.add_courtroom(name, path)
                if res == 0:
                    result_name = 'Успех'
                    result_text = 'Зал был успешно добавлен.'
                else:
                    result_name = 'Неудача'
                    result_text = f'Зал не был добавлен. {errorcode[res]}'
                popup_msg(result_name, result_text)
                add_courtroom.close()
                row = f'{name}\n{path}'
                self.mylist_listWidget.addItem(row)
                self.cr_name_path_dict[row] = name
            else:
                QtWidgets.QMessageBox.about(self, 'Ошибка','Указанная директория недоступна')

    def remove_crroom(self):
        qm = QtWidgets.QMessageBox()
        clicked_idx = self.mylist_listWidget.currentRow()
        if clicked_idx == -1:
            return
        clicked_txt = self.mylist_listWidget.currentItem().text()
        ret = qm.question(self, '', "Удалить из базы данных все записи, связанные с этим залом?\nОтменить данное действие невозможно", qm.Yes | qm.No | qm.Cancel)
        if ret == qm.Yes:
            self.sqlite.remove_courtroom(self.cr_name_path_dict[clicked_txt], withrecords=True)
            self.mylist_listWidget.takeItem(clicked_idx)
        if ret == qm.No:
            self.sqlite.remove_courtroom(self.cr_name_path_dict[clicked_txt], withrecords=False)
            self.mylist_listWidget.takeItem(clicked_idx)
        if ret == qm.Cancel:
            return

    def apply_settings(self):
        self.settings['server_media_path'] = self.mp3_save_path_server.text()
        sqlite.update_settings(self.settings)

    def start_worker_scan(self):
        try:
            period = self.spinBox_period.value()*60
            self.monitor_threads = dict()
            self.converter_threads = dict()
            self.latest_converter_threads = dict()
            self.queues = dict()
            self.wait_queues = dict()
            self.pushButton_stop.setDisabled(False)
            self.pushButton_start.setDisabled(True)
            self.label_status.setText("Текущий статус: РАБОТАЕТ")
            for name, path in sqlite.get_courtrooms_dict().items():
                self.queues[name] = Queue()
                self.monitor_threads[name] = MonitorThread(path, self.queues[name])
                self.monitor_threads[name].start()
                self.addLogRow(f'{name} мониторинг запущен.')
                self.wait_queues[name] = Queue()
                self.converter_threads[name] = Worker(self.queues[name], self.wait_queues[name], period)
                self.converter_threads[name].add_string_to_log.connect(self.addLogRow)
                self.converter_threads[name].start()
                self.addLogRow(f'{name} конвертер запущен.')
                self.latest_converter_threads[name] = WorkerWaiter(self.wait_queues[name], self.queues[name])
                self.latest_converter_threads[name].add_string_to_log.connect(self.addLogRow)
                self.latest_converter_threads[name].start()
                self.addLogRow(f'{name} сервис передержки запущен.')
        except:
            traceback.print_exc()
            raise

    def stop_worker_scan(self):
        for name in list(self.courtrooms.keys()):
            try:
                self.monitor_threads[name]._Running = False
            except:
                pass
        self.addLogRow('Сканирование было остановлено пользователем.')
        self.pushButton_start.setDisabled(False)
        self.pushButton_stop.setDisabled(True)
        self.label_status.setText("Текущий статус: ОСТАНОВЛЕНО")

    def addLogRow(self, line):
        self.plainTextEdit_logger.appendPlainText(line)


class MonitorThread(QThread):
    class NewFolderHandler(FileSystemEventHandler):
        def __init__(self, parent=None):
            super().__init__()
            self.parent = parent

        def on_created(self, event):
            if event.is_directory:
                if os.path.basename(event.src_path).startswith('Case #'):
                    self.parent.queue.put(event.src_path)

    def __init__(self, folder_path, queue):
        super().__init__()
        self.folder_path = folder_path
        self.queue = queue
        self._Running = True

    def run(self):
        try:
            event_handler = self.NewFolderHandler(self)
            observer = Observer()
            observer.schedule(event_handler, path=self.folder_path, recursive=False)
            observer.start()
            while self._Running:
                time.sleep(1)
            self.queue.put(None)
            observer.stop()
            observer.join()
        except Exception as e:
            traceback.print_exc()


class Worker(QThread):
    def __init__(self, queue, waiter_queue, period):
        super().__init__()
        self._Running = True
        self.queue = queue
        self.waiter_queue = waiter_queue
        self.period = period

    add_string_to_log = pyqtSignal(str)

    def run(self):
        while True:
            try:
                fp = self.queue.get()
                if fp is None:
                    self.waiter_queue.put(None)
                    break
                try:
                    time.sleep(self.period)
                    res = gather_path(logger = self.add_string_to_log, new_folder_path=fp)
                    if res == 0:
                        self.add_string_to_log.emit('Добавлен ' + os.path.basename(fp))
                    elif res == 1:
                        self.add_string_to_log.emit('НЕ добавлен ' + os.path.basename(fp) + ', путь уже существует')
                    elif res == 2:
                        self.add_string_to_log.emit('НЕ добавлен ' + os.path.basename(fp) + ', отсутствуют файлы в папке')
                        self.add_string_to_log.emit('Отправлен на передержку на 4 часа')
                        self.waiter_queue.put(fp, time.time())
                    elif res == 3:
                        self.add_string_to_log.emit('НЕ добавлен ' + os.path.basename(fp) + ', ошибка конвертации')
                    else:
                        self.add_string_to_log.emit('НЕ добавлен ' + os.path.basename(fp) + ', ошибка sql')
                except Exception as e:
                    self.add_string_to_log.emit(f'Ошибка обработки {fp}, {e}')
            except Exception as e:
                self.add_string_to_log.emit(f'Ошибка обработки, {e}')


class WorkerWaiter(QThread):
    def __init__(self, wait_queue, main_queue):
        super().__init__()
        self._Running = True
        self.wait_queue = wait_queue
        self.main_queue = main_queue

    add_string_to_log = pyqtSignal(str)

    def run(self):
        while True:
            try:
                fp, start_time = self.wait_queue.get()
                if fp is None:
                    break
                current_time = time.time()
                if current_time - start_time >= 4 * 3600:
                    self.main_queue.put((fp, start_time))
                else:
                    self.wait_queue.put((fp, start_time))
                time.sleep(5)
            except Exception as e:
                self.add_string_to_log.emit(f'Ошибка обработки, {e}')
