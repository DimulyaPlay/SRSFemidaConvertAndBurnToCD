import traceback

from PyQt5 import QtCore, QtWidgets, uic
from Utils import *
from UI_write_to_cd_progress_bar import ProgressWindow


class CasesMenu(QtWidgets.QMainWindow):
    def __init__(self, root, sqlite):
        super().__init__(parent=None)
        uic.loadUi('assets/cases_menu.ui', self)
        self.root = root
        self.sqlite = sqlite
        self.courtrooms_dict = sqlite.get_courtrooms_dict()
        self.cr_list = list(self.courtrooms_dict.keys())
        self.cases_to_burn = []
        try:
            self.comboBoxCourtrooms = self.findChild(QtWidgets.QComboBox, 'comboBox_cr')
            for cr in self.cr_list:
                self.comboBoxCourtrooms.addItem(cr)
            self.comboBoxCourtrooms.currentTextChanged.connect(self.refill_table)
            self.labelChosenCount = self.findChild(QtWidgets.QLabel, 'label_cases_to_burn')
            self.labelChosenCount.setText("Выбрано: 0")
            self.dateEdit_from = self.findChild(QtWidgets.QDateEdit, 'dateEdit_from')
            self.lineEdit_case = self.findChild(QtWidgets.QLineEdit, 'lineEdit_case')
            self.lineEdit_case.textChanged.connect(self.refill_table)
            current_date = QtCore.QDate.currentDate()
            self.dateEdit_from.setDate(current_date.addDays(-7))
            self.dateEdit_to = self.findChild(QtWidgets.QDateEdit, 'dateEdit_to')
            self.dateEdit_to.setDate(current_date)
            self.pushButtonStartBurning = self.findChild(QtWidgets.QPushButton, 'pushButton_burn')
            self.pushButtonStartBurning.clicked.connect(lambda: self.start_burning())
            self.list_widget = self.findChild(QtWidgets.QListWidget, 'listWidget')
            self.hat_list_widget = self.findChild(QtWidgets.QListWidget, 'listWidget_2')
            hat_widget = HatWidget()
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(hat_widget.sizeHint())
            self.hat_list_widget.addItem(item)
            self.hat_list_widget.setItemWidget(item, hat_widget)
            self.dateEdit_to.dateChanged.connect(self.refill_table)
            self.dateEdit_from.dateChanged.connect(self.refill_table)
        except:
            traceback.print_exc()
            raise
        self.refill_table()

    def refill_table(self):
        try:
            self.list_widget.clear()
            current_cr = self.comboBoxCourtrooms.currentText()
            if current_cr == 'Все':
                current_cr = None
            date_from = self.dateEdit_from.date().toPyDate()
            date_to = self.dateEdit_to.date().toPyDate()
            case_prefix = self.lineEdit_case.text() if self.lineEdit_case.text() != '' else None
            data_for_table = self.sqlite.get_courthearings_by_prefix_courtroom_and_date(cr_name = current_cr, from_to_date=[date_from, date_to], period=None, case_prefix = case_prefix)
            self.file_widgets_list = []
            for idx, row in data_for_table.iterrows():
                case = row['case'].replace('$2F', '/')
                date = row['date'].strftime('%d-%m-%Y')
                cr = row['courtroomname']
                if row["mp3duration"] != '':
                    duration_text = str(int(int(row["mp3duration"])/60))
                else:
                    duration_text = 'нет mp3'
                mp3path = settings['server_media_path'] + row['mp3path']
                file_widget = FileWidget(case, cr, date,duration_text, mp3path, self.cases_to_burn, self.labelChosenCount)
                self.file_widgets_list.append(file_widget)
            for file_widget in self.file_widgets_list:
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint(file_widget.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, file_widget)
        except:
            traceback.print_exc()
            raise

    def closeEvent(self, event):
        self.root.show()
        self.hide()
        event.ignore()

    def start_burning(self):
        try:
            if self.cases_to_burn:
                print('writing to disk ', self.cases_to_burn)
                ProgressWindow(self, self.cases_to_burn)
            else:
                popup_msg('Ошибка', "Должна быть выбрана хотя бы одна запись")
        except:
            traceback.print_exc()
            raise


class FileWidget(QtWidgets.QWidget):
    # Объект формирования строки виджетов для размещения в qlistwidget
    def __init__(self, case, cr, date, mp3duration, mp3path, cases_to_burn, num_cases):
        super().__init__()
        self.case, self.date, self.mp3path, self.mp3duration = case, date, mp3path, mp3duration
        self.cr = cr
        self.cases_to_burn = cases_to_burn
        self.num_cases = num_cases
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = DoubleClickableLabel(parent=case, widget=self)
        self.label.setFixedWidth(140)
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label)
        layout.addStretch(1)
        self.label_cr = QtWidgets.QLabel(cr)
        self.label_cr.setFixedWidth(100)
        self.label_cr.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_cr)
        self.label_date = QtWidgets.QLabel(date)
        self.label_date.setFixedWidth(80)
        self.label_date.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_date)

        self.label_duration = QtWidgets.QLabel(mp3duration)
        self.label_duration.setFixedWidth(80)
        self.label_duration.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_duration)

        self.check_box = QtWidgets.QCheckBox()
        self.check_box.setFixedWidth(20)
        self.check_box.setChecked(mp3path in self.cases_to_burn)
        self.check_box.stateChanged.connect(lambda: self.add_remove(mp3path))
        layout.addWidget(self.check_box)

        self.setLayout(layout)

    def add_remove(self, mp3path):
        if self.check_box.isChecked():
            self.cases_to_burn.append(mp3path)
            print('checker')
            print(self.cases_to_burn)
        else:
            self.cases_to_burn.remove(mp3path)
            print('unchecker')
            print(self.cases_to_burn)

        self.num_cases.setText(f'Выбрано: {len(self.cases_to_burn)}')


class HatWidget(QtWidgets.QWidget):
    # Объект формирования строки виджетов для размещения в qlistwidget
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QtWidgets.QLabel('Дело №')
        self.label.setFixedWidth(140)
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label)
        layout.addStretch(1)
        self.label_cr = QtWidgets.QLabel('Зал')
        self.label_cr.setFixedWidth(100)
        self.label_cr.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_cr)
        self.label_date = QtWidgets.QLabel('Дата')
        self.label_date.setFixedWidth(80)
        self.label_date.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_date)
        self.label_duration = QtWidgets.QLabel('Длит.')
        self.label_duration.setFixedWidth(80)
        self.label_duration.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label_duration)
        self.cb = QtWidgets.QLabel(' ')
        self.cb.setFixedWidth(20)
        self.cb.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.cb)
        self.setLayout(layout)


class DoubleClickableLabel(QtWidgets.QLabel):
    def __init__(self, parent=None, widget=None):
        super(DoubleClickableLabel, self).__init__(parent)
        self.widget = widget

    def mouseDoubleClickEvent(self, event):
        if self.widget.mp3path != '':
            open_mp3(self.widget.mp3path)
