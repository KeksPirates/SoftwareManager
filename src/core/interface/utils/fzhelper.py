from typing import Generator
import fuzzyfinder
from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit
from copy import deepcopy

class FuzzySearchWindow(QtWidgets.QWidget): # should work everywhere
    """
    The dict should contain a:
    $(keytosortby) : str
    THIS IS REQUIRED

    all other things will be displayed alphabetically after it.
    All elements should have the same Keys, eg when one element has "sources" : "buzzheavier" all other elements should as well have a key called "sources", though the value can be "MegaDB"
        
    All elements are strings, e.g. "count" : "1"

    The key will be at the Top of the Table
    The value will be listed for each element

    keys in ignorekeys will be ignored and not displayed, e.g. if oyu have links in the database which arent relevant
    """
    def __init__(self, options: list[dict[str, str]], ignorekeys: list[str] = [], columnClicklShouldReturn = 1, keytosortby = "name"):
        super().__init__()

        self.opts: list[dict[str, str]] = options
        self.filtered_opts = deepcopy(self.opts)
        self.ignorekeys = ignorekeys
        self.returncolumn = columnClicklShouldReturn
        self.sortkey = keytosortby

        self.searchbox = QtWidgets.QLineEdit()
        self.searchbox.setPlaceholderText("Search for a game on Steamrip")

        self.table = QtWidgets.QTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # disable editing
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)     # no selection highlight
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.searchbox.setFocus()

        headers = []
        for key in self.opts[1].keys():
            if key not in self.ignorekeys:
                headers.append(key)



        print(headers)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(self.opts))
        for row_index, row_data in enumerate(self.opts):
            for col_index, key in enumerate(headers):
                if key in self.ignorekeys:
                    continue
                value = row_data.get(key, "")
                item = QtWidgets.QTableWidgetItem(value)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()

        self.searchbox.textChanged.connect(self.filter_table)

        self.table.cellClicked.connect(self.cellClick)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.searchbox, 0, 0)
        layout.addWidget(self.table, 1, 0)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)

    def filter_table(self):

        searchquery = self.searchbox.text()

        options: Generator = fuzzyfinder.main.fuzzyfinder(searchquery, self.opts, accessor=lambda x: x[self.sortkey])

        self.filtered_opts = []

        for row_index, row_data in enumerate(options):
            self.filtered_opts.append(row_data)
            for col_index, key in enumerate(row_data.keys()):
                if key in self.ignorekeys:
                    continue
                value = row_data.get(key, "")
                self.table.setItem(
                    row_index,
                    col_index,
                    QtWidgets.QTableWidgetItem(value)
                )

    def cellClick(self, row: int, _: int):
        item = self.table.item(row, self.returncolumn)

        if item is not None:
            value = item.text()
            print(value)


if __name__ == "__main__":

    import core.data.scrapers.steamrip as sr

    app = QtWidgets.QApplication([])
    widget = FuzzySearchWindow(sr.scrape_steamrip_links())
    widget.resize(600,400)
    widget.show()


    exit(app.exec())
