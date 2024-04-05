import traceback
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from Utils import *
import os
import shutil


class MainUi(QtWidgets.QMainWindow):
    def __init__(self, sqlite):
        super().__init__(parent=None)
        uic.loadUi('assets/main_ui.ui', self)
        self.setWindowIcon(QtGui.QIcon('assets/avatar.jpg'))
        self.sqlite = sqlite
        self.courtrooms_dict = sqlite.get_courtrooms_dict()
        self.cr_list = list(self.courtrooms_dict.keys())
        self.cases_to_burn = []
        self.dict_chosenlist = {}
        try:
            self.comboBoxCourtrooms = self.findChild(QtWidgets.QComboBox, 'comboBox_cr')
            for cr in self.cr_list:
                self.comboBoxCourtrooms.addItem(cr)
            self.comboBoxCourtrooms.currentTextChanged.connect(self.refill_search_table)
            self.labelChosenCount = self.findChild(QtWidgets.QLabel, 'label_cases_to_burn')
            self.labelChosenCount.setText("Выбрано: 0 ")
            self.lineEdit_case = self.findChild(QtWidgets.QLineEdit, 'lineEdit_case')
            self.lineEdit_case.textChanged.connect(self.refill_search_table)
            current_date = QtCore.QDate.currentDate()
            self.dateEdit_from = self.findChild(QtWidgets.QDateEdit, 'dateEdit_from')
            self.dateEdit_from.setDate(current_date.addDays(-7))
            self.dateEdit_to = self.findChild(QtWidgets.QDateEdit, 'dateEdit_to')
            self.dateEdit_to.setDate(current_date)
            self.pushButtonStartBurning = self.findChild(QtWidgets.QPushButton, 'pushButton_burn')
            self.pushButtonStartBurning.clicked.connect(self.start_burning_process)
            self.pushButton_to_usb = self.findChild(QtWidgets.QPushButton, 'pushButton_to_usb')
            self.pushButton_to_usb.clicked.connect(self.send_to_usb)
            self.pushButton_refresh = self.findChild(QtWidgets.QPushButton, 'pushButton_refresh')
            self.pushButton_refresh.clicked.connect(self.refresh_tables)

            self.tableWidget_search = self.findChild(QtWidgets.QTableWidget, 'tableWidget_search')
            self.tableWidget_search.setStyleSheet("QTableWidget::item { padding: 3px; }")
            self.tableWidget_search.setColumnWidth(0, 120)
            self.tableWidget_search.setColumnWidth(1, 85)
            self.tableWidget_search.setColumnWidth(2, 95)
            self.tableWidget_search.setColumnWidth(3, 60)
            self.tableWidget_search.setColumnWidth(4, 100)
            self.tableWidget_search.setColumnWidth(5, 65)

            self.tableWidget_list = self.findChild(QtWidgets.QTableWidget, 'tableWidget_list')
            self.tableWidget_list.setStyleSheet("QTableWidget::item { padding: 3px; }")
            self.tableWidget_list.setColumnWidth(0, 120)
            self.tableWidget_list.setColumnWidth(1, 85)
            self.tableWidget_list.setColumnWidth(2, 95)
            self.tableWidget_list.setColumnWidth(3, 60)
            self.tableWidget_list.setColumnWidth(4, 100)
            self.tableWidget_list.setColumnWidth(5, 65)
            self.dateEdit_to.dateChanged.connect(self.refill_search_table)
            self.dateEdit_from.dateChanged.connect(self.refill_search_table)
        except:
            traceback.print_exc()

    def refresh_tables(self):
        self.refill_search_table()
        self.refill_list_table()

    def refill_search_table(self):
        current_cr = self.comboBoxCourtrooms.currentText()
        if current_cr == 'Все':
            current_cr = None
        date_from = self.dateEdit_from.date().toPyDate()
        date_to = self.dateEdit_to.date().toPyDate()
        case_prefix = self.lineEdit_case.text() if self.lineEdit_case.text() != '' else None
        data_for_table = self.sqlite.get_courthearings_by_prefix_courtroom_and_date(cr_name=current_cr,
                                                                                    from_to_date=[date_from, date_to],
                                                                                    period=None,
                                                                                    case_prefix=case_prefix)
        self.tableWidget_search.setRowCount(len(data_for_table))
        for idx, row in data_for_table.iterrows():
            case = row['case'].replace('$2F', '/')

            date = row['date'].strftime('%d-%m-%Y')
            cr = row['courtroomname']
            if row["mp3duration"] != '':
                duration_text = seconds_to_hh_mm_ss(int(row["mp3duration"]))
                mp3path = settings['server_media_path'] + row['mp3path']
            else:
                duration_text = 'нет mp3'
                mp3path = None
            courtHearing = [case, cr, date, duration_text, mp3path]
            label_case = QtWidgets.QLabel(case)
            self.tableWidget_search.setCellWidget(idx, 0, label_case)

            label_cr = QtWidgets.QLabel(cr)
            label_cr.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_search.setCellWidget(idx, 1, label_cr)

            label_date = QtWidgets.QLabel(date)
            label_date.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_search.setCellWidget(idx, 2, label_date)

            label_dur = QtWidgets.QLabel(duration_text)
            label_dur.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_search.setCellWidget(idx, 3, label_dur)

            button = QPushButton("Прослушать")
            button.clicked.connect(lambda clicked, mp3 = mp3path: open_mp3(mp3))
            self.tableWidget_search.setCellWidget(idx, 4, button)

            checkbox = QtWidgets.QCheckBox()
            if mp3path in self.cases_to_burn:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, mp3path=courtHearing, cb = checkbox: self.checkbox_state_changed(state, mp3path, cb))
            cell_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(cell_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.tableWidget_search.setCellWidget(idx, 5, cell_widget)
        print('updating')

    def checkbox_state_changed(self, state, mp3path, checkbox):
        try:
            if state == QtCore.Qt.Checked:
                self.cases_to_burn.append(mp3path[-1])
                if mp3path[-1] is not None:
                    self.dict_chosenlist[mp3path[-1]] = [mp3path, checkbox]
            else:
                self.cases_to_burn.remove(mp3path[-1])
                del self.dict_chosenlist[mp3path[-1]]
            self.labelChosenCount.setText(f'Выбрано: {len(self.cases_to_burn)} ')
            self.refill_list_table()
        except:
            traceback.print_exc()

    def refill_list_table(self):
        self.tableWidget_list.setRowCount(len(self.dict_chosenlist))
        for idx, (key, value) in enumerate(self.dict_chosenlist.items()):
            case = value[0][0]
            cr = value[0][1]
            date = value[0][2]
            duration_text = value[0][3]
            mp3path = value[0][4]

            label_case = QtWidgets.QLabel(case)
            self.tableWidget_list.setCellWidget(idx, 0, label_case)

            label_cr = QtWidgets.QLabel(cr)
            label_cr.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_list.setCellWidget(idx, 1, label_cr)

            label_date = QtWidgets.QLabel(date)
            label_date.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_list.setCellWidget(idx, 2, label_date)

            label_dur = QtWidgets.QLabel(duration_text)
            label_dur.setAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget_list.setCellWidget(idx, 3, label_dur)

            button = QPushButton("Прослушать")
            button.clicked.connect(lambda clicked, mp3=mp3path: open_mp3(mp3))
            self.tableWidget_list.setCellWidget(idx, 4, button)

            button_del = QPushButton('Х')
            button_del.clicked.connect(lambda clicked, cb = value[1]: self.remove_row_from_list(cb))
            self.tableWidget_list.setCellWidget(idx, 5, button_del)

    def start_burning_process(self):
        try:
            if self.cases_to_burn:
                print('writing to disk ', self.cases_to_burn)
                StartBurningProcessWithBar(self, self.cases_to_burn)
            else:
                popup_msg('Ошибка', "Должна быть выбрана хотя бы одна запись")
        except:
            traceback.print_exc()

    def remove_row_from_list(self, cb):
        try:
            cb.setChecked(False)
        except:
            traceback.print_exc()

    def send_to_usb(self):
        try:
            if self.cases_to_burn:
                to_usb = CopyUsbDialog(self.cases_to_burn)
                to_usb.exec_()

            else:
                popup_msg('Ошибка', "Должна быть выбрана хотя бы одна запись")
        except:
            traceback.print_exc()

