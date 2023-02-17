from PyQt5 import QtCore, QtGui, QtWidgets
from Utils import *
import datetime


class Courtrooms_menu(QtWidgets.QMainWindow):
    def __init__(self,root, sqlite):
        super().__init__(parent=root)
        self.root = root
        self.sqlite = sqlite
        self.courtrooms_dict = sqlite.get_courtrooms_dict()
        self.cr_list = list(self.courtrooms_dict.keys())
        self.periods_list_to_query = {'7 дней':"7day", '30 дней':"30day", '365 дней':"365day", 'Все записи':None}
        self.cases_to_burn = []
        self.setFixedSize(685, 550)
        self.setWindowTitle("ПРОСМОТР ЗАЛОВ")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setFixedSize(760, 550)
        self.comboBoxCourtrooms = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxCourtrooms.setGeometry(QtCore.QRect(10, 10, 161, 22))
        for cr in self.cr_list:
            self.comboBoxCourtrooms.addItem(cr)

        self.comboBoxPeriods = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxPeriods.setGeometry(QtCore.QRect(180, 10, 101, 22))
        for i in list(self.periods_list_to_query.keys()):
            self.comboBoxPeriods.addItem(i)

        self.labelChosenCount = QtWidgets.QLabel(self.centralwidget)
        self.labelChosenCount.setGeometry(QtCore.QRect(290, 10, 180, 21))
        self.labelChosenCount.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelChosenCount.setText("Выбрано для записи: 0 файлов")

        self.pushButtonStartBurning = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStartBurning.setGeometry(QtCore.QRect(583, 10, 91, 23))
        self.pushButtonStartBurning.setText("Начать запись")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        headerh = self.tableWidget.horizontalHeader()
        headerh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        headerv = self.tableWidget.verticalHeader()
        headerv.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setGeometry(QtCore.QRect(10, 40, 664, 501))
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setColumnCount(5)
        itemCase = QtWidgets.QTableWidgetItem("№ Дела")
        self.tableWidget.setHorizontalHeaderItem(0, itemCase)
        self.tableWidget.setColumnWidth(0,228)
        itemDate = QtWidgets.QTableWidgetItem("Дата")
        self.tableWidget.setHorizontalHeaderItem(1, itemDate)
        self.tableWidget.setColumnWidth(1, 90)
        itemDuration = QtWidgets.QTableWidgetItem("Длит")
        self.tableWidget.setHorizontalHeaderItem(2, itemDuration)
        self.tableWidget.setColumnWidth(2, 90)
        item = QtWidgets.QTableWidgetItem(' ')
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.setColumnWidth(3, 120)
        item = QtWidgets.QTableWidgetItem(' ')
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.setColumnWidth(4, 120)
        self.refill_table()
        self.comboBoxCourtrooms.currentTextChanged.connect(self.refill_table)
        self.comboBoxPeriods.currentTextChanged.connect(self.refill_table)
        self.show()

    def refill_table(self):
        self.tableWidget.setRowCount(0)
        current_cr = self.comboBoxCourtrooms.currentText()
        current_period = self.comboBoxPeriods.currentText()
        data_for_table = self.sqlite.get_courthearings_by_courtroom_and_date(current_cr, self.periods_list_to_query[current_period])
        self.tableWidget.setRowCount(len(data_for_table))
        for idx, row in data_for_table.iterrows():
            case = QtWidgets.QTableWidgetItem(row['case'].replace('$2F', '/'))
            self.tableWidget.setItem(idx, 0, case)

            date = QtWidgets.QTableWidgetItem(row['date'].strftime('%d-%m-%Y'))
            self.tableWidget.setItem(idx, 1, date)

            if row["mp3duration"] != '':
                duration_text = f'{int(int(row["mp3duration"]) / 60)}'
                btn_cell = QtWidgets.QPushButton('Прослушать',
                                                 clicked=lambda state, e=current_media_path + row['mp3path']: open_mp3(
                                                     e))
                self.tableWidget.setCellWidget(idx, 3, btn_cell)
            else:
                duration_text = 'нет mp3'
            duration = QtWidgets.QTableWidgetItem(duration_text)
            self.tableWidget.setItem(idx, 2, duration)


            # btn_add_remove = customtkinter.CTkButton(self.ch_frame_buttons, text='ДОБАВИТЬ ДЛЯ ЗАПИСИ',
            #                                          font=('roboto', 14), state=state)
            # btn_add_remove.configure(command=lambda b=btn_add_remove, e=row['mp3path']: add_remove_to_list(b, e))
            # if row['mp3path'] in self.cases_to_burn:
            #     btn_add_remove.configure(fg_color='red', hover_color='darkred', text=' В СПИСКЕ ДЛЯ ЗАПИСИ ')
            # btn_add_remove.grid(padx=5, pady=5, column=1, row=idx, sticky='e')


    def closeEvent(self, event):
        self.root.show()
        self.hide()
        event.ignore()

    def write_to_disk(self):
        print(self.cases_to_burn)
        if len(self.cases_to_burn) == 0:
            print('nothing to write')
            return
        # burn_mp3_files_to_disk(self.cases_to_burn)
        self.cases_to_burn = []
        self.count_to_burn_lb.configure(text=f'ВЫБРАНО ДЛЯ ЗАПИСИ: 0')
        self.create_ch_table(self.cr_list[0])
        return

