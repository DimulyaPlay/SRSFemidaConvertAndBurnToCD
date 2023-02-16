# -*- coding: utf-8 -*-
import os
from PyQt5 import QtCore, QtGui, QtWidgets
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
        self.startGatheringButton = QtWidgets.QPushButton(self.crooms_tab, clicked = lambda: gather_all())
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
        self.tabWidget.addTab(self.schedule_tab, "Расписание")
        self.label = QtWidgets.QLabel(self.schedule_tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 801, 53))
        self.label.setText("В разработке\n"
                             "\n"
                             "Сбор записей можно осуществлять в автоматическом режиме, \n"
                             "создав задачу в планировщике windows на запуск программы с параметром \'-gather\'.")
        # EXTRA TAB INIT
        self.extra_tab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.extra_tab, "Дополнительно")
        self.mp3_save_checkBox = QtWidgets.QCheckBox(self.extra_tab)
        self.mp3_save_checkBox.setGeometry(QtCore.QRect(10, 10, 231, 21))
        self.mp3_save_checkBox.setText("Конвертировать в MP3 при сборе записей")
        self.mp3_save_checkBox.setChecked(bool(int(self.settings['audio_convert'])))
        self.mp3_save_path = QtWidgets.QLineEdit(self.extra_tab)
        self.mp3_save_path.setGeometry(QtCore.QRect(10, 40, 231, 20))
        self.mp3_save_path.setPlaceholderText("Папка для сохранения mp3")
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
                QtWidgets.QMessageBox.about(self, result_name, result_text)
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
        sqlite.update_settings(self.settings)



