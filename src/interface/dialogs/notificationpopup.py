from PySide6.QtWidgets import QMessageBox
import qdarktheme

class NotificationPopup(QMessageBox):
    def __init__(self, title, text, infotext=None, parent=None):
        super().__init__(parent)

        qdarktheme.setup_theme("auto")

        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowTitle(title)
        self.setText(text)
        
        if infotext is not None:
            self.setInformativeText(infotext)
            
        self.setStandardButtons(QMessageBox.StandardButton.Ok)