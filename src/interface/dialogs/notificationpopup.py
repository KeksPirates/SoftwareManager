from PySide6.QtWidgets import QMessageBox
from utils.data.state import state
import qdarktheme

class NotificationPopup(QMessageBox):
    def __init__(self, title, text, infotext=None, parent=None, darkmode=True):
        super().__init__(parent)

        if darkmode is True:
            custom_colors = {}
            if state.accent_color:
                custom_colors["primary"] = state.accent_color
            qdarktheme.setup_theme("auto", custom_colors=custom_colors if custom_colors else None)

        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowTitle(title)
        self.setText(text)
        
        if infotext is not None:
            self.setInformativeText(infotext)
            
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
