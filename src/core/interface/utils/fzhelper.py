import fuzzyfinder
from PySide6 import QtCore, QtWidgets, QtGui

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

        self.searchbox = QtWidgets.QTextEdit()
        self.searchbox.placeholderText = "Search for a game"

        self.table = QtWidgets.QTableWidget()
        self.table.setHorizontalHeader(self.opts[0].keys())

