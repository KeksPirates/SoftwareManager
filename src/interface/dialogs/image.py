from PySide6.QtCore import Qt, QSize, QEvent, QObject
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
from utils.data.state import state
import os


class Image(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.application = parent
        self.overlay_label = QLabel(parent)
        self.overlay_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._current_image_path = None

        parent.installEventFilter(self)

        if state.image_path and os.path.exists(state.image_path):
            self._load_and_display(state.image_path)

    def eventFilter(self, obj, event):
        if obj == self.application and event.type() == QEvent.Type.Resize:
            if self._current_image_path:
                self._load_and_display(self._current_image_path)
        return False

    def _load_and_display(self, image_path):
        if state.image_enabled is not True:
            return
        self._current_image_path = image_path
        parent = self.application
        image = QImage(image_path)
        if image.isNull():
            self.overlay_label.hide()
            return

        scaled_image = image.scaledToWidth(
            int(state.image_width), Qt.TransformationMode.SmoothTransformation
        )

        max_width = parent.width()
        max_height = parent.height()
        if scaled_image.width() > max_width or scaled_image.height() > max_height:
            scaled_image = scaled_image.scaled(
                QSize(max_width, max_height),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        pixmap = QPixmap.fromImage(scaled_image)
        self.overlay_label.setPixmap(pixmap)
        self.overlay_label.adjustSize()
        self.overlay_label.raise_()

        x = parent.width() - self.overlay_label.width() - int(state.image_offset)
        y = parent.height() - self.overlay_label.height() - int(state.image_offset)
        self.overlay_label.move(x, y)
        self.overlay_label.show()

    def update_image_overlay(self, new_image_path):
        self._load_and_display(new_image_path)
