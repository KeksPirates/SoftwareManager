from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect, QStackedWidget
from PySide6.QtCore import Qt, QSize, QEvent, QObject
from PySide6.QtGui import QImage, QPixmap
from utils.data.state import state
import darkdetect
import os


class Image(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.application = parent
        self.overlay_label = QLabel(parent)
        self.overlay_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.overlay_label.setGraphicsEffect(self.opacity_effect)

        self._current_image_path = None
        self._wallpaper_active = False
        self._original_stylesheets = {}
        parent.installEventFilter(self)
        state.image_changed.connect(self.update_image_overlay)

        if state.image_path and os.path.exists(state.image_path):
            self._load_and_display(state.image_path)

    def eventFilter(self, obj, event):
        if obj == self.application and event.type() == QEvent.Type.Resize:
            if self._current_image_path:
                self._load_and_display(self._current_image_path)
        return False

    def _set_wallpaper_transparency(self, enabled):
        if self._wallpaper_active == enabled:
            return
        self._wallpaper_active = enabled
        parent = self.application

        central = parent.centralWidget()
        if central:
            central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

        for attr in ['tab_wrapper', 'corner_widget', 'titlebar']:
            w = getattr(parent, attr, None)
            if w:
                w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

        if hasattr(parent, 'tabs'):
            tabs = parent.tabs
            tabs.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

            for i in range(tabs.count()):
                page = tabs.widget(i)
                if page:
                    page.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

            stack = tabs.findChild(QStackedWidget)
            if stack:
                stack.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

            tab_bar = tabs.tabBar()
            if tab_bar:
                tab_bar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

            if 'tabs' not in self._original_stylesheets:
                self._original_stylesheets['tabs'] = tabs.styleSheet()
            if enabled:
                tabs.setStyleSheet(
                    self._original_stylesheets['tabs']
                    + "\nQTabWidget::pane { background: transparent; }"
                    + "\nQTabBar { background: transparent; }"
                    + "\nQTabBar::tab { background: transparent; }"
                )
            else:
                tabs.setStyleSheet(self._original_stylesheets['tabs'])

        # Searchbar
        if hasattr(parent, 'searchbar'):
            if 'searchbar' not in self._original_stylesheets:
                self._original_stylesheets['searchbar'] = parent.searchbar.styleSheet()
            if enabled:
                parent.searchbar.setStyleSheet("QLineEdit { background-color: transparent; }")
            else:
                parent.searchbar.setStyleSheet(self._original_stylesheets['searchbar'])

        # Download button
        if hasattr(parent, 'dlbutton'):
            if 'dlbutton' not in self._original_stylesheets:
                self._original_stylesheets['dlbutton'] = parent.dlbutton.styleSheet()
            if enabled:
                parent.dlbutton.setStyleSheet("QPushButton { background-color: transparent; }")
            else:
                parent.dlbutton.setStyleSheet(self._original_stylesheets['dlbutton'])

        # Labels
        for attr in ['emptyResults', 'emptyDownload']:
            w = getattr(parent, attr, None)
            if w:
                w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)

        if hasattr(parent, 'tracker_list'):
            if 'tracker_list' not in self._original_stylesheets:
                self._original_stylesheets['tracker_list'] = parent.tracker_list.styleSheet()
            if enabled:
                popup_bg = '#1e1e1e' if darkdetect.isDark() else '#ffffff'
                parent.tracker_list.setStyleSheet(
                    "QComboBox { background-color: transparent; }"
                    f" QComboBox QAbstractItemView {{ background-color: {popup_bg}; }}"
                )
            else:
                parent.tracker_list.setStyleSheet(self._original_stylesheets['tracker_list'])

    def _load_and_display(self, image_path):
        if state.image_enabled is not True:
            self.overlay_label.hide()
            self._set_wallpaper_transparency(False)
            return
        self._current_image_path = image_path
        parent = self.application
        image = QImage(image_path)
        if image.isNull():
            self.overlay_label.hide()
            return

        if getattr(state, "image_as_wallpaper", False):
            scaled_image = image.scaled(
                parent.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            crop_x = (scaled_image.width() - parent.width()) // 2
            crop_y = (scaled_image.height() - parent.height()) // 2
            scaled_image = scaled_image.copy(crop_x, crop_y, parent.width(), parent.height())

            pixmap = QPixmap.fromImage(scaled_image)
            self.overlay_label.setPixmap(pixmap)

            self.overlay_label.setGeometry(0, 0, parent.width(), parent.height())
            self.overlay_label.lower()

            self.opacity_effect.setOpacity(state.image_opacity / 100)
            self._set_wallpaper_transparency(True)

        else:
            self._set_wallpaper_transparency(False)
            scaled_image = image.scaledToWidth(
                state.image_width, Qt.TransformationMode.SmoothTransformation
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

            pos = state.image_position
            off = int(state.image_offset)
            w = self.overlay_label.width()
            h = self.overlay_label.height()
            if pos == "top-left":
                x, y = off, off
            elif pos == "top-right":
                x, y = parent.width() - w - off, off
            elif pos == "bottom-left":
                x, y = off, parent.height() - h - off
            elif pos == "center":
                x, y = (parent.width() - w) // 2, (parent.height() - h) // 2
            else:  # bottom-right (default)
                x, y = parent.width() - w - off, parent.height() - h - off

            self.opacity_effect.setOpacity(state.image_opacity / 100)

            self.overlay_label.move(x, y)
        self.overlay_label.show()

    def update_image_overlay(self, new_image_path):
        self._load_and_display(new_image_path)