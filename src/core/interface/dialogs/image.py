from PySide6.QtGui import QImage, QPixmap
from core.utils.data.state import state
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
import os

class Image():
    def __init__(self, parent):
        self.overlay_label = QLabel(parent)
        self.overlay_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        if state.image_path is not None and os.path.exists(state.image_path):
            self.image = QImage(state.image_path)
            self.image = self.image.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)

            self.pixmap = QPixmap.fromImage(self.image)
            self.overlay_label.setPixmap(self.pixmap)
            self.overlay_label.adjustSize()
            self.overlay_label.raise_()

            x = parent.width() - self.overlay_label.width()
            y = parent.height() - self.overlay_label.height()
            self.overlay_label.move(x, y)

    def update_image_overlay(self, new_image_path):
        self.image = QImage(new_image_path)
        self.pixmap = QPixmap.fromImage(self.image)
        self.overlay_label.setPixmap(self.pixmap)
        self.overlay_label.adjustSize()
