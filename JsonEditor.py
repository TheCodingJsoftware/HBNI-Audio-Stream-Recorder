from datetime import datetime, timedelta
from functools import partial

import qdarktheme
from PyQt5 import uic
from PyQt5.QtCore import QRegExp, Qt, QTimer
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QInputDialog,
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
        """
        I'm trying to make a dialog box that will allow the user to add a new entry to a JSON file

        Args:
          parent: The parent widget.
        """
        QDialog.__init__(self, parent)
        uic.loadUi("UI/add_json_dialog.ui", self)
        self.setStyleSheet(qdarktheme.load_stylesheet())
        data = DownloadLinks.loadJson()
        self.inputID.setValue(len(data))
        self.inputDate.setText(datetime.now().strftime("%B %d %A %Y %I_%M %p"))
        self.inputHost.setText("/")
        reg_ex = QRegExp("(\/(\/\/)?[a-z]+)")
        input_validator = QRegExpValidator(reg_ex, self.inputHost)
        self.inputHost.setValidator(input_validator)
        self.inputHost.textChanged.connect(self.inputTextChanged)
        self.inputDescription.textChanged.connect(self.inputTextChanged)
        self.inputLength.valueChanged.connect(self.inputTextChanged)
        self.inputTextChanged()

    def inputTextChanged(self):
        """
        It takes the text from the inputHost, inputDescription, inputDate, and inputLength fields and
        combines them into a filename.
        """
        timeDelta = timedelta(minutes=self.inputLength.value())
        finalDeltatime: str = self.convertDeltatime(duration=timeDelta)
        try:
            if self.inputHost.text()[0] != "/":
                self.inputHost.setText("/" + self.inputHost.text().replace("/", ""))
        except IndexError:
            self.inputHost.setText("/")

        self.inputFileName.setText(
            self.inputHost.text().replace("/", "").title()
            + " - "
            + self.inputDescription.text()
            + " - "
            + self.inputDate.text()
            + " - "
            + finalDeltatime
            + ".mp3"
        )

    def convertDeltatime(self, duration) -> str:
        """Converts minutes to a pretty format

        Args:
            duration (deltatime): file length

        Returns:
            output (str): final format
        """
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return (
            f"{minutes}m {seconds}s" if hours == 0 else f"{hours}h {minutes}m {seconds}s"
        )

    def accept(self):
        """
        It takes the text from the text boxes and adds it to a database.
        """
        DownloadLinks.addDownloadLink(
            fileName=self.inputFileName.text(),
            downloadLink=self.inputDownloadLink.text(),
            date=self.inputDate.text(),
            host=self.inputHost.text(),
            description=self.inputDescription.text(),
            length=self.inputLength.value(),
            commit=False,
        )
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        """
        It loads the json file, and then it loads the contents of the json file into the GUI.
        """
        super().__init__()
        uic.loadUi("UI/json_editor.ui", self)
        self.setStyleSheet(qdarktheme.load_stylesheet())
        self.jsonContent = {}
        self.index = 0
        # self.loadContents()
        self.inputSearch.returnPressed.connect(self.startTimer)
        self.btnPushToGithub.clicked.connect(
            partial(DownloadLinks.uploadDatabase, "Updated downloadLinks.json file.")
        )
        self.btnAdd.clicked.connect(self.addJson)
        self.startTimer()
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def startTimer(self) -> None:
        """
        It clears the layout, clears the jsonContent, loads the json, sets the index to 0, sets the iter
        to the length of the json, and starts the timer.
        """
        self.clearLayout(self.layoutContent)
        self.jsonContent.clear()
        json = DownloadLinks.loadJson()
        self.index = 0
        self._iter = iter(range(len(json)))
        self._timer = QTimer(interval=0, timeout=self.loadContents)
        self._timer.start()

    def loadContents(self) -> None:
        """
        It loads the contents of a json file into a QGroupBox.
        """
        json = DownloadLinks.loadJson()
        try:
            i = next(self._iter)
        except StopIteration:
            self._timer.stop()
        else:
            name = list(json.keys())[i]
            if self.inputSearch.text() in name.lower() or self.inputSearch.text() == "":
                self.jsonContent.update({name: {}})
                vBoxLayout = QVBoxLayout(self)
                groupbox = QGroupBox(self, title=name, checkable=False)
                self.layoutContent.addWidget(groupbox)
                gridLayout = QGridLayout(self)
                btnEdit = QPushButton(self, text="Edit Title")
                btnEdit.clicked.connect(partial(self.editTitle, name))
                vBoxLayout.addWidget(btnEdit)
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
                        edit.setMaximum(999999)
                        edit.setFocusPolicy(Qt.ClickFocus)
                        edit.setValue(int(json[name][data]))
                    elif data == "length":
                        edit = QDoubleSpinBox(self)
                        edit.setDecimals(15)
                        edit.setSuffix(" minutes")
                        edit.setFocusPolicy(Qt.ClickFocus)
                        edit.setMaximum(999.9999999999)
                        edit.setValue(float(json[name][data]))
                    else:
                        edit = QLineEdit(self)
                        if data == "host":
                            reg_ex = QRegExp("(\/(\/\/)?[a-z]+)")
                            input_validator = QRegExpValidator(reg_ex, edit)
                            edit.setValidator(input_validator)
                        edit.setText(f"{json[name][data]}")
                    self.jsonContent[name].update({data: []})
                    self.jsonContent[name][data].append(edit)
                    gridLayout.addWidget(edit, self.index, 1)
                self.index += 1

    def addJson(self):
        """
        If the dialog is accepted or rejected, start the timer.
        """
        dialog = QDialogClass()
        if dialog.exec_() in [QDialog.Accepted, QDialog.Rejected]:
            self.startTimer()
        dialog.deleteLater()

    def clearLayout(self, layout) -> None:
        """
        If the layout is not None, while the layout has items, take the first item, get the widget, if
        the widget is not None, delete it, otherwise, clear the layout

        Args:
          layout: The layout to be cleared
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def editTitle(self, oldTitle: str) -> None:
        """
        It opens a dialog box that allows the user to change the title of a download link

        Args:
          oldTitle (str): str
        """
        InputDialog = QInputDialog(self)
        newTitle, okPressed = InputDialog.getText(
            self,
            "Edit title",
            "New title:",
            QLineEdit.Normal,
            oldTitle,
        )

        if okPressed:
            DownloadLinks.changeTitle(oldTitle, newTitle)
            self.startTimer()

    def applyEdit(self, name: str) -> None:
        """
        It takes the values from the QLineEdits and QSpinBoxes and passes them to a function that edits
        the JSON file

        Args:
          name (str): str = The name of the file
        """
        DownloadLinks.editDownloadLink(
            fileName=name,
            downloadLink=self.jsonContent[name]["downloadLink"][0].text(),
            date=self.jsonContent[name]["date"][0].text(),
            host=self.jsonContent[name]["host"][0].text(),
            description=self.jsonContent[name]["description"][0].text(),
            length=self.jsonContent[name]["length"][0].value(),
            id=self.jsonContent[name]["id"][0].value(),
        )
        self.startTimer()

    def deleteJson(self, name: str) -> None:
        """
        It removes a download link from the database and then starts the timer again

        Args:
          name (str): The name of the file to be deleted
        """
        DownloadLinks.removeDownloadLink(filename=name)
        self.startTimer()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
