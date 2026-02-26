import fuzzyfinder
from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit

class FuzzySearchWindow(QtWidgets.QWidget):
    """
    The dict should contain a:
    name : str
    THIS IS REQUIRED

    all other things will be displayed alphabetically after it.
    All elements should have the same Keys, eg when one element has "sources" : "buzzheavier" all other elements should as well have a key called "sources", though the value can be "MegaDB"
        
    All elements are strings, e.g. "count" : "1"

    The key will be at the Top of the Table
    The value will be listed for each element
    """
    def __init__(self, options: list[dict[str, str]]):
        super().__init__()

        self.opts: list[dict[str, str]] = options

        self.searchbox = QtWidgets.QLineEdit()
        self.searchbox.placeholderText = "Search for a game"

        self.table = QtWidgets.QTableWidget()
        headers = self.opts[1].keys()

        print(headers)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(self.opts))
        for row_index, row_data in enumerate(self.opts):
            for col_index, key in enumerate(headers):
                value = row_data.get(key, "")[1:-1].replace("-", " ")
                item = QtWidgets.QTableWidgetItem(value)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()

        self.searchbox.textChanged.connect(self.filter_table)



        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.searchbox, 0, 0)
        layout.addWidget(self.table, 1, 0)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)

    def filter_table(self):

        searchquery = self.searchbox.text()

        options = fuzzyfinder.main.fuzzyfinder(searchquery, self.opts, accessor=lambda x: x["name"])

        for row_index, row_data in enumerate(options):
            for col_index, key in enumerate(row_data.keys()):
                value = row_data.get(key, "")
                self.table.setItem(
                    row_index,
                    col_index,
                    QtWidgets.QTableWidgetItem(value)
                )

if __name__ == "__main__":

    import core.data.scrapers.steamrip as sr

    app = QtWidgets.QApplication([])
    widget = FuzzySearchWindow(sr.offline_scrape_steamrip_links())
    widget.resize(600,400)
    widget.show()


    exit(app.exec())