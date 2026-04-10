from interface.dialogs.notificationpopup import NotificationPopup
from utils.config.settings import save_settings 
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QMessageBox
from utils.logging.logs import consoleLog
from utils.data.state import state
import webbrowser
import re

class UIBridge(QObject):
    show_notification = Signal()

ui_bridge = UIBridge()

def show_megadb_notification():
    notification_popup = NotificationPopup(title="Opened MegaDB link in browser",
                                           text="Beware of malicious Ads. Make sure to have an adblocker installed.\n" '<br><a href="https://ublockorigin.com">Visit uBlock Origin</a>',
                                           darkmode=False if state.window_transparency else True
                                           )

    notification_popup.setTextFormat(Qt.TextFormat.RichText)
    notification_popup.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

    if state.window_transparency is True:
        notification_popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    button = notification_popup.addButton("Don't show again", QMessageBox.ButtonRole.AcceptRole)
    button.clicked.connect(lambda: setattr(state, "show_megadb_notification", False))
    
    save_settings(show_megadb_notification=state.show_megadb_notification)
    notification_popup.exec()

def scrape_megadb(url):
    match = re.search(r"megadb\.net/([a-zA-Z0-9]+)", url)
    if not match:
        consoleLog("MegaDB: Invalid URL")
        return None

    consoleLog("MegaDB: Captcha required, launching browser...")
    webbrowser.open(url)
    if state.show_megadb_notification is True:
        ui_bridge.show_notification.emit()
    return None
