# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from Utils import *


class Settings_menu(QtWidgets.QMainWindow):
    def __init__(self, root, sqlite):
        super(Settings_menu, self).__init__(parent=root)
        self.root = root
        self.sqlite = sqlite
        self.settings = sqlite.get_settings()
        self.courtrooms = sqlite.get_courtrooms_dict()
        self.setWindowTitle("ПАРАМЕТРЫ")
        self.setFixedSize(539, 431)
        # MAIN TAB WIDGET
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.tabBarClicked.connect(self.apply_settings)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 539, 431))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        # CR TAB INIT
        self.crooms_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.crooms_tab, "Залы")
        self.addCourtroomButton = QtWidgets.QPushButton(self.crooms_tab, clicked=lambda: self.add_crroom())
        self.addCourtroomButton.setGeometry(QtCore.QRect(10, 10, 111, 31))
        self.addCourtroomButton.setText("Добавить зал")
        self.removeCourtroomButton = QtWidgets.QPushButton(self.crooms_tab, clicked = lambda: self.remove_crroom())
        self.removeCourtroomButton.setGeometry(QtCore.QRect(125, 10, 171, 31))
        self.removeCourtroomButton.setText("Удалить выбранный зал")
        self.startGatheringButton = QtWidgets.QPushButton(self.crooms_tab, clicked = lambda: self.startGatheringProcess())
        self.startGatheringButton.setGeometry(QtCore.QRect(351, 10, 171, 31))
        self.startGatheringButton.setText("Запустить сборщик записей")
        self.mylist_listWidget = QtWidgets.QListWidget(self.crooms_tab)
        self.mylist_listWidget.setGeometry(QtCore.QRect(10, 50, 511, 351))
        self.cr_name_path_dict = {}
        # GENERATE LIST OF CR
        for name, path in self.courtrooms.items():
            row = name + '\n' + fr'{path}'
            self.mylist_listWidget.addItem(row)
            self.cr_name_path_dict[row] = name
        # SCHDLE TAB INIT and text placeholder

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
        self.label_period.setGeometry(QtCore.QRect(290, 10, 171, 21))
        self.label_period.setFont(font)
        self.label_period.setText("Частота сканирования, мин")
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
        self.plainTextEdit_logger.appendPlainText('Разработка: Краснокамский суд ПК, Дмитрий Соснин, 2023. github.com/dimulyaplay')

        # EXTRA TAB INIT
        self.extra_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.extra_tab, "Дополнительно")
        self.mp3_save_checkBox = QtWidgets.QCheckBox(self.extra_tab)
        self.mp3_save_checkBox.setGeometry(QtCore.QRect(10, 10, 231, 21))
        self.mp3_save_checkBox.setText("Конвертировать в MP3 при сборе записей")
        self.mp3_save_checkBox.setChecked(bool(int(self.settings['audio_convert'])))
        labelServer = QtWidgets.QLabel(self.extra_tab)
        labelServer.setText("Сетевая папка для чтения mp3 клиентом")
        labelServer.setGeometry(QtCore.QRect(10, 40, 251, 20))
        self.mp3_save_path_server = QtWidgets.QLineEdit(self.extra_tab)
        self.mp3_save_path_server.setGeometry(QtCore.QRect(10, 60, 251, 20))
        if self.settings['server_media_path'] == '':
            self.mp3_save_path_server.setPlaceholderText(r"Пример: \\server\audio_db")
        else:
            self.mp3_save_path_server.setText(self.settings['server_media_path'])

        labelClient = QtWidgets.QLabel(self.extra_tab)
        labelClient.setText("Локальная папка для сохранения mp3 сервером")
        labelClient.setGeometry(QtCore.QRect(10, 90, 251, 20))
        self.mp3_save_path_client = QtWidgets.QLineEdit(self.extra_tab)
        self.mp3_save_path_client.setGeometry(QtCore.QRect(10, 110, 251, 20))
        if self.settings['client_media_path'] == '':
            self.mp3_save_path_client.setPlaceholderText(r"Пример: C:\\femida_MP3_archive\audio_db")
        else:
            self.mp3_save_path_client.setText(self.settings['client_media_path'])
        self.show()

    def closeEvent(self, event):
        self.apply_settings()
        self.hide()
        self.root.show()
        event.ignore()

    def add_crroom(self):
        addCourtroom = QtWidgets.QDialog(parent=self)
        addCourtroom.setFixedSize(277, 91)
        addCourtroom.setWindowTitle("Добавить зал")
        crNameLine = QtWidgets.QLineEdit(addCourtroom)
        crNameLine.setGeometry(QtCore.QRect(10, 10, 261, 20))
        crNameLine.setPlaceholderText("Введите название, например: Зал 1")
        crPathLine = QtWidgets.QLineEdit(addCourtroom)
        crPathLine.setGeometry(QtCore.QRect(10, 40, 261, 20))
        crPathLine.setPlaceholderText(r"Введите путь, например: С:\Залы\Зал 1")
        saveCancelButton = QtWidgets.QDialogButtonBox(parent = addCourtroom, orientation = QtCore.Qt.Horizontal)
        saveCancelButton.setGeometry(QtCore.QRect(60, 60, 161, 31))
        saveCancelButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        saveCancelButton.accepted.connect(lambda: add_room_to_base())  # type: ignore
        saveCancelButton.rejected.connect(addCourtroom.reject)  # type: ignore
        addCourtroom.show()

        def add_room_to_base():
            name = fr'{crNameLine.text()}'.strip()
            path = fr'{crPathLine.text()}'
            if os.path.exists(path):
                res = self.sqlite.add_courtroom(name, path)
                if res == 0:
                    print(f'New courtroom {name, path} added')
                    result_name = 'Успех'
                    result_text = 'Зал был успешно добавлен.'

                else:
                    result_name = 'Неудача'
                    result_text = f'Зал не был добавлен. {errorcode[res]}'
                    print(f'New courtroom {name, path} not added')
                    popup_msg(result_name, result_text)
                addCourtroom.close()
                row = f'{name}\n{path}'
                self.mylist_listWidget.addItem(row)
                self.cr_name_path_dict[row] = name
            else:
                QtWidgets.QMessageBox.about(self, 'Ошибка','Указанная директория недоступна')
                print('Директория недоступна')

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
        self.settings['audio_convert'] = int(self.mp3_save_checkBox.isChecked())
        self.settings['server_media_path'] = self.mp3_save_path_server.text()
        self.settings['client_media_path'] = self.mp3_save_path_client.text()
        sqlite.update_settings(self.settings)

    def start_worker_scan(self):
        self.pushButton_stop.setDisabled(False)
        self.pushButton_start.setDisabled(True)
        self.thread = QThread()
        self.worker = Worker(self.spinBox_period.value())
        self.worker.moveToThread(self.thread)
        self.worker.add_string_to_log.connect(self.addLogRow)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def stop_worker_scan(self):
        try:
            self.worker._Running = False
            self.thread.terminate()
        except:
            pass
        self.addLogRow('Сканирование было остановлено пользователем.')
        self.pushButton_start.setDisabled(False)
        self.pushButton_stop.setDisabled(True)

    def addLogRow(self, line):
        self.plainTextEdit_logger.appendPlainText(line)


class Worker(QThread):
    def __init__(self, sleeptimemins):
        super().__init__()
        self._Running = True
        self.sleeptime = sleeptimemins*60

    add_string_to_log = pyqtSignal(str)

    def run(self):
        self.add_string_to_log.emit(f'{ctime()} - Сканирование запущено')
        while self._Running:
            gather_all(self.add_string_to_log)
            sleep(self.sleeptime)
        self.exit(0)
