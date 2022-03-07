from datetime import datetime
from functools import partial

import qdarktheme
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
)

import DownloadLinks


class QDialogClass(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi("add_json_dialog.ui", self)
        self.setStyleSheet(qdarktheme.load_stylesheet())
        data = DownloadLinks.loadJson()
        self.inputID.setValue(len(data))
        self.inputDate.setText(datetime.now().strftime("%B %d %A %Y %I_%M %p"))

    def accept(self):
        DownloadLinks.addDownloadLink(
            fileName=self.inputFileName.text(),
            downloadLink=self.inputDownloadLink.text(),
            date=self.inputDate.text(),
            length=self.inputLength.value(),
            commit=False,
        )
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("json_editor.ui", self)
        self.setStyleSheet(qdarktheme.load_stylesheet())
        self.jsonContent = {}
        self.index = 0
        # self.loadContents()
        self.inputSearch.returnPressed.connect(self.loadContents)
        self.btnAdd.clicked.connect(self.addJson)
        self.startTimer()
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def startTimer(self) -> None:
        self.clearLayout(self.layoutContent)
        self.jsonContent.clear()
        json = DownloadLinks.loadJson()
        self.index = 0
        self._iter = iter(range(len(json)))
        self._timer = QTimer(interval=10, timeout=self.loadContents)
        self._timer.start()

    def loadContents(self) -> None:
        json = DownloadLinks.loadJson()
        try:
            i = next(self._iter)
        except StopIteration:
            self._timer.stop()
        else:
            # btn = QPushButton(self, text=f"{i}")
            # for name in json:
            name = list(json.keys())[i]
            if self.inputSearch.text() in name.lower() or self.inputSearch.text() == "":
                self.jsonContent.update({name: {}})
                vBoxLayout = QVBoxLayout(self)
                groupbox = QGroupBox(self, title=name, checkable=False)
                self.layoutContent.addWidget(groupbox)
                gridLayout = QGridLayout(self)
                groupbox.setLayout(vBoxLayout)
                vBoxLayout.addLayout(gridLayout)
                vBoxLayout.addWidget(groupbox)
                btnApplyEdit = QPushButton(self, text="Apply Edit")
                btnApplyEdit.clicked.connect(partial(self.applyEdit, name))
                vBoxLayout.addWidget(btnApplyEdit)
                btnDelete = QPushButton(self, text="Delete")
                btnDelete.clicked.connect(partial(self.deleteJson, name))
                vBoxLayout.addWidget(btnDelete)
                for data in json[name]:
                    self.index += 1
                    label = QLabel(self, text=data)
                    gridLayout.addWidget(label, self.index, 0)
                    if data == "id":
                        edit = QSpinBox(self)
                        edit.setValue(int(json[name][data]))
                    elif data == "length":
                        edit = QDoubleSpinBox(self)
                        edit.setDecimals(15)
                        edit.setSuffix(" minutes")
                        edit.setValue(float(json[name][data]))
                    else:
                        edit = QLineEdit(self)
                        edit.setText(f"{json[name][data]}")
                    self.jsonContent[name].update({data: []})
                    self.jsonContent[name][data].append(edit)
                    gridLayout.addWidget(edit, self.index, 1)
                self.index += 1

    def addJson(self):
        dialog = QDialogClass()
        if dialog.exec_() in [QDialog.Rejected, QDialog.Accepted]:
            self.startTimer()
        dialog.deleteLater()
        # dialog.exec_()

    def clearLayout(self, layout) -> None:
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def applyEdit(self, name: str) -> None:
        DownloadLinks.editDownloadLink(
            fileName=name,
            downloadLink=self.jsonContent[name]["downloadLink"][0].text(),
            date=self.jsonContent[name]["date"][0].text(),
            length=self.jsonContent[name]["length"][0].value(),
            id=self.jsonContent[name]["id"][0].value(),
        )
        self.startTimer()

    def deleteJson(self, name: str) -> None:
        DownloadLinks.removeDownloadLink(filename=name)
        self.startTimer()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
