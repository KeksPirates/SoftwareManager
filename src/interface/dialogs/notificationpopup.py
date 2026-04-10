from PySide6.QtWidgets import QMessageBox
import qdarktheme

class NotificationPopup(QMessageBox):
    def __init__(self, title, text, infotext=None, parent=None, darkmode=True):
        super().__init__(parent)

        if darkmode is True:
            qdarktheme.setup_theme("auto")

        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowTitle(title)
        self.setText(text)
        
        if infotext is not None:
            self.setInformativeText(infotext)
            
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
