import re
from datetime import datetime, timedelta
from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QDate, QDateTime, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QCompleter,
    QDateTimeEdit,
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from qt_material import apply_stylesheet

import DownloadLinks


class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(CustomTableWidget, self).__init__()
        self.editable_column_indexes = []

    def edit(self, index, trigger, event):
        """
        This function checks if a column is editable and allows editing if it is, otherwise it returns
        False.

        Args:
          index: The index of the item in the model that is being edited.
          trigger: The trigger parameter is an event that causes the editor to be opened for editing the
        cell. It can be one of the following values:
          event: The event parameter in the edit() method is an instance of QEvent class. It represents
        an event that occurred on the widget. The event parameter is used to determine the type of event
        that occurred, such as a mouse click or a key press, and to handle the event accordingly.

        Returns:
          If the column index of the given index is in the list of editable_column_indexes, then the
        super().edit() method is called and its return value is returned. Otherwise, False is returned.
        """
        if index.column() in self.editable_column_indexes:
            return super(CustomTableWidget, self).edit(index, trigger, event)
        else:
            return False

    def set_editable_column_index(self, columns):
        """
        This function sets the indexes of columns that are editable in a table.

        Args:
          columns (list[int]): A list of integers representing the indexes of the columns that should be
        editable in a table or spreadsheet.
        """
        self.editable_column_indexes = columns


class AddStreamDialog(QDialog):
    def __init__(self, parent=None):
        """
        I'm trying to make a dialog box that will allow the user to add a new entry to a JSON file

        Args:
          parent: The parent widget.
        """
        QDialog.__init__(self, parent)
        uic.loadUi("UI/add_json_dialog.ui", self)
        data = DownloadLinks.loadJson()
        self.inputID.setValue(len(data))
        self.inputDate.setDate(QDate().currentDate())
        self.inputDate.dateTimeChanged.connect(self.inputTextChanged)
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
            + self.inputDate.dateTime().toString("MMMM d dddd yyyy hh_mm AP")
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
            date=self.inputDate.dateTime().toString("MMMM d dddd yyyy hh_mm AP"),
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
        self.selected_item: str = ""
        self.jsonContent = {}
        self.index = 0
        self.showMaximized()
        # self.loadContents()
        self.inputSearch.textChanged.connect(self.loadData)

        autofill_search_options = DownloadLinks.getAllHosts()
        completer = QCompleter(autofill_search_options)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.inputSearch.setCompleter(completer)
        self.btnPushToGithub.clicked.connect(
            partial(DownloadLinks.uploadDatabase, "Updated downloadLinks.json file.")
        )
        self.btnAdd.clicked.connect(self.addBroadcast)
        self.tableWidget = CustomTableWidget(self)
        self.tableWidget.set_editable_column_index([1, 2, 3, 4, 5, 6, 7])
        self.tableWidget.itemChanged.connect(self.cellChanged)
        self.tableWidget.itemSelectionChanged.connect(self.selectionChanged)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "Name",
                "Host",
                "Description",
                "Date",
                "Length (min)",
                "Part",
                "ID",
                "Download Link",
                "DEL",
            ]
        )
        self.tableWidget.setColumnWidth(0, 400)  # Name
        self.tableWidget.setColumnWidth(1, 140)  # Host
        self.tableWidget.setColumnWidth(2, 320)  # Description
        self.tableWidget.setColumnWidth(3, 200)  # Date
        self.tableWidget.setColumnWidth(4, 200)  # Length
        self.tableWidget.setColumnWidth(5, 120)  # Part
        self.tableWidget.setColumnWidth(6, 60)  # Id
        self.tableWidget.setColumnWidth(7, 300)  # Download Link
        self.tableWidget.setColumnWidth(8, 70)  # DEL
        self.layoutContent.addWidget(self.tableWidget)
        self.loadData()

    def convertDeltatime(self, minutes) -> str:
        """Converts minutes to a pretty format

        Args:
            duration (deltatime): file length

        Returns:
            output (str): final format
        """
        duration = timedelta(minutes=minutes)
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return (
            f"{minutes}m {seconds}s" if hours == 0 else f"{hours}h {minutes}m {seconds}s"
        )

    def generateNewTitle(self, selected_row) -> str:
        host = self.tableWidget.item(selected_row, 1).text()
        description = self.tableWidget.item(selected_row, 2).text()
        date = self.tableWidget.cellWidget(selected_row, 3).dateTime()
        length = float(self.tableWidget.item(selected_row, 4).text().replace(' ','').replace('minutes', ''))
        combo_part: str = self.tableWidget.cellWidget(selected_row, 5).currentText()
        part_text: str = '' if combo_part == 'None' else f' - ({combo_part})'

        return f"{host.replace('/', '').title()} - {description} - {date.toString('MMMM d dddd yyyy hh_mm AP')} - {self.convertDeltatime(length)}{part_text}.mp3"

    def cellChanged(self, item: QTableWidgetItem):
        selected_row = item.row()

        data = DownloadLinks.loadJson()
        changed_column = item.column()
        if changed_column == 1: # Host
            new_host = item.text().replace(" ", '').replace('_', '')
            if new_host[0] != '/':
                new_host = f'/{new_host}'

            self.tableWidget.blockSignals(True)
            self.tableWidget.item(selected_row, 1).setText(new_host)
            self.tableWidget.blockSignals(False)

            self.editBroadcast(
                fileName=self.selected_item,
                downloadLink=data[self.selected_item]["downloadLink"],
                host=new_host,
                description=data[self.selected_item]["description"],
                date=data[self.selected_item]["date"],
                length=data[self.selected_item]["length"],
                id=data[self.selected_item]["id"],
            )

        elif changed_column == 2: # Description
            new_description = item.text()

            self.editBroadcast(
                fileName=self.selected_item,
                downloadLink=data[self.selected_item]["downloadLink"],
                host=data[self.selected_item]["host"],
                description=new_description,
                date=data[self.selected_item]["date"],
                length=data[self.selected_item]["length"],
                id=data[self.selected_item]["id"],
            )

        elif changed_column == 4: # Length
            new_length = float(item.text().replace(' ', '').replace('minutes', ''))

            self.tableWidget.blockSignals(True)
            self.tableWidget.item(selected_row, 4).setText(f'{new_length} minutes')
            self.tableWidget.blockSignals(False)

            self.editBroadcast(
                fileName=self.selected_item,
                downloadLink=data[self.selected_item]["downloadLink"],
                host=data[self.selected_item]["host"],
                description=data[self.selected_item]["description"],
                date=data[self.selected_item]["date"],
                length=new_length,
                id=data[self.selected_item]["id"],
            )
        elif changed_column == 6: # id
            new_id = int(item.text())

            self.editBroadcast(
                fileName=self.selected_item,
                downloadLink=data[self.selected_item]["downloadLink"],
                host=data[self.selected_item]["host"],
                description=data[self.selected_item]["description"],
                date=data[self.selected_item]["date"],
                length=data[self.selected_item]["length"],
                id=new_id,
            )
            DownloadLinks.sortJsonFile()
        elif changed_column == 7: # Download Link
            new_download_link = item.text()

            self.editBroadcast(
                fileName=self.selected_item,
                downloadLink=new_download_link,
                host=data[self.selected_item]["host"],
                description=data[self.selected_item]["description"],
                date=data[self.selected_item]["date"],
                length=data[self.selected_item]["length"],
                id=data[self.selected_item]["id"],
            )

        DownloadLinks.changeTitle(self.selected_item, self.generateNewTitle(selected_row=selected_row))

        self.tableWidget.blockSignals(True)
        self.tableWidget.item(selected_row, 0).setText(self.generateNewTitle(selected_row=selected_row))
        self.tableWidget.blockSignals(False)
        self.selected_item = self.tableWidget.item(selected_row, 0).text()
        self.refreshAllDeleteButtons()
        # self.loadData()

    def selectionChanged(self):
        selected_row = self.tableWidget.selectedItems()[0].row()
        self.selected_item = self.tableWidget.item(selected_row, 0).text()

    def loadData(self):
        self.tableWidget.blockSignals(True)
        self.tableWidget.setRowCount(0)
        data = dict(reversed(list(DownloadLinks.loadJson().items())))
        row_count: int = 0
        for stream_name, stream_data in data.items():
            if self.inputSearch.text() not in stream_data["host"]:
                continue
            col_count: int = 0
            self.tableWidget.insertRow(row_count)
            self.tableWidget.setRowHeight(row_count, 40)
            self.tableWidget.setItem(row_count, col_count, QTableWidgetItem(stream_name))
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            col_count += 1
            self.tableWidget.setItem(
                row_count, col_count, QTableWidgetItem(stream_data["host"])
            )
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            col_count += 1
            self.tableWidget.setItem(
                row_count, col_count, QTableWidgetItem(stream_data["description"])
            )
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            col_count += 1
            datetime = QDateTime.fromString(
                stream_data["date"], "MMMM d dddd yyyy hh_mm AP"
            )
            datetime_edit = QDateTimeEdit()
            datetime_edit.wheelEvent = lambda event: event.ignore()
            datetime_edit.setToolTip(stream_data["date"])
            datetime_edit.setCalendarPopup(True)
            datetime_edit.setDateTime(datetime)
            datetime_edit.dateTimeChanged.connect(
                partial(self.onDateChange, datetime_edit)
            )
            self.tableWidget.setCellWidget(row_count, col_count, datetime_edit)

            col_count += 1
            self.tableWidget.setItem(
                row_count,
                col_count,
                QTableWidgetItem(str(stream_data["length"]) + " minutes"),
            )
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            col_count += 1
            combo_part = QComboBox()
            combo_part.wheelEvent = lambda event: event.ignore()
            combo_part.addItems(['None', 'Part 1', 'Part 2', 'Part 3', 'Part 4','Part 5', "Part 6", "Part 7", 'Final Part'])
            if 'Final Part' in stream_name:
                combo_part.setCurrentText("Final Part")
            elif 'Part' in stream_name:
                match = re.search(r'\(Part (\d)\)', stream_name)
                combo_part.setCurrentText(f"Part {match.group(1)}")
            combo_part.currentTextChanged.connect(partial(self.onPartChange, combo_part))
            self.tableWidget.setCellWidget(row_count, col_count, combo_part)


            col_count += 1
            self.tableWidget.setItem(
                row_count, col_count, QTableWidgetItem(str(stream_data["id"]))
            )
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignHCenter
            )

            col_count += 1
            self.tableWidget.setItem(
                row_count, col_count, QTableWidgetItem(stream_data["downloadLink"])
            )
            self.tableWidget.item(row_count, col_count).setTextAlignment(
                Qt.AlignLeft | Qt.AlignVCenter
            )

            col_count += 1
            delete_button = QPushButton("DEL")
            delete_button.clicked.connect(partial(self.deleteBroadcast, stream_name, row_count))
            self.tableWidget.setCellWidget(row_count, col_count, delete_button)

            row_count += 1
        self.tableWidget.blockSignals(False)

    def addBroadcast(self):
        """
        If the dialog is accepted or rejected, start the timer.
        """
        dialog = AddStreamDialog()
        if dialog.exec_() in [QDialog.Accepted, QDialog.Rejected]:
            dialog.deleteLater()

    def onPartChange(self, combo_part: QComboBox):
        selected_row = self.tableWidget.selectedItems()[0].row()

        DownloadLinks.loadJson()
        DownloadLinks.changeTitle(self.selected_item, self.generateNewTitle(selected_row=selected_row))

        self.tableWidget.blockSignals(True)
        self.tableWidget.item(selected_row, 0).setText(self.generateNewTitle(selected_row=selected_row))
        self.tableWidget.blockSignals(False)
        self.selected_item = self.tableWidget.item(selected_row, 0).text()
        self.refreshAllDeleteButtons()

    def onDateChange(self, datetime: QDateTimeEdit):
        selected_row = self.tableWidget.selectedItems()[0].row()

        date_string = datetime.dateTime().toString("MMMM d dddd yyyy hh_mm AP")
        data = DownloadLinks.loadJson()
        self.editBroadcast(
            fileName=self.selected_item,
            downloadLink=data[self.selected_item]["downloadLink"],
            host=data[self.selected_item]["host"],
            description=data[self.selected_item]["description"],
            date=date_string,
            length=data[self.selected_item]["length"],
            id=data[self.selected_item]["id"],
        )
        DownloadLinks.changeTitle(self.selected_item, self.generateNewTitle(selected_row=selected_row))

        self.tableWidget.blockSignals(True)
        self.tableWidget.item(selected_row, 0).setText(self.generateNewTitle(selected_row=selected_row))
        self.tableWidget.blockSignals(False)
        self.selected_item = self.tableWidget.item(selected_row, 0).text()
        self.refreshAllDeleteButtons()

    def editBroadcast(
        self,
        fileName: str,
        downloadLink: str,
        host: str,
        description: str,
        date: str,
        length: float,
        id: int,
    ):
        DownloadLinks.editDownloadLink(
            fileName=fileName,
            downloadLink=downloadLink,
            host=host,
            description=description,
            date=date,
            length=length,
            id=id,
        )

    def deleteBroadcast(self, name: str, row_index: int):
        DownloadLinks.removeDownloadLink(name)
        self.tableWidget.removeRow(row_index)
        self.refreshAllDeleteButtons()

    def refreshAllDeleteButtons(self):
        for row_count in range(self.tableWidget.rowCount()):
            delete_button = self.tableWidget.cellWidget(row_count, 8)
            delete_button.disconnect()
            delete_button.clicked.connect(partial(self.deleteBroadcast, self.tableWidget.item(row_count, 0).text(), row_count))


if __name__ == "__main__":
    app = QApplication([])
    apply_stylesheet(app, theme="theme.xml")
    window = MainWindow()
    window.show()
    app.exec_()
