errorcode = {
    "UNIQUE constraint failed: Courtrooms.diskdirectory": "Путь к залу должен быть уникален"}

from PyQt5.QtWidgets import QMessageBox


def popup_msg(title, message):
    QMessageBox.about(None, title, message)
