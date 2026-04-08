from interface.utils.tabhelper import create_tab
from interface.dialogs.theme import _accent_selection_color
from utils.config.settings import save_settings
from interface.utils.svghelper import svg_icon
from utils.logging.logs import consoleLog
from PySide6.QtCore import Qt, QSize
from utils.data.state import state
from PySide6.QtGui import QColor
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QLineEdit, 
    QPushButton, 
    QWidget, 
    QVBoxLayout, 
    QDialog, 
    QLabel, 
    QHBoxLayout,
    QSpinBox, QSlider, QCheckBox,
    QFileDialog,
    QComboBox,
    QColorDialog
)

import platform

SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 6c0-1.1.9-2 2-2h5l2 2h7c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6z" fill="{color}"/></svg>'


def settings_dialog(self):
    temp_image_path = state.image_path
    temp_image_width = state.image_width
    temp_image_offset = state.image_offset
    temp_image_opacity = state.image_opacity
    temp_image_enabled = state.image_enabled
    temp_image_as_wallpaper = state.image_as_wallpaper
    temp_image_position = state.image_position

    def create_widget(widget_type, label_text, **kwargs):
        container = QWidget()
        layout = QHBoxLayout()
        container.setLayout(layout)
        layout.addWidget(QLabel(label_text))

        widget = widget_type()

        if widget_type in (QSpinBox,):
            layout.addWidget(widget)
            widget.setMinimum(kwargs.get("minimum", 0))
            widget.setMaximum(kwargs.get("maximum", 10000000))
            widget.setFixedWidth(kwargs.get("width", 180))
            widget.setFixedHeight(kwargs.get("height", 30))
        elif widget_type in (QCheckBox,):
            layout.addStretch()
            layout.addWidget(widget)
        elif widget_type in (QLineEdit,):
            layout.addWidget(widget)
            container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
            if "width" in kwargs:
                widget.setFixedWidth(kwargs["width"])
            if "height" in kwargs:
                widget.setFixedHeight(kwargs["height"])
        elif widget_type in (QComboBox,):
            layout.addWidget(widget)
            widget.setFixedWidth(kwargs.get("width", 180))
            widget.setFixedHeight(kwargs.get("height", 30))

        return container, widget

    consoleLog("Settings dialog opened")
    dialog = QDialog(self)
    dialog.setWindowTitle("Settings")
    dialog.setFixedSize(580, 400)

    dialog_layout = QVBoxLayout()
    dialog.setLayout(dialog_layout)

    if state.window_transparency and platform.system() != "Windows" and dialog:
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # Ignore Updates checkbox
    update_checkbox_container, update_checkbox = create_widget(QCheckBox, "Ignore Updates: ")
    if platform.system() == "Windows":
        update_checkbox.setChecked(state.ignore_updates)
        update_checkbox.toggled.connect(lambda checked: setattr(state, 'ignore_updates', checked))

    # Autoresume Container Checkbox
    autoresume_container, autoresume_checkbox = create_widget(QCheckBox, "Auto-Resume Downloads: ")
    autoresume_checkbox.setChecked(state.autoresume)
    autoresume_checkbox.toggled.connect(lambda checked: setattr(state, 'autoresume', checked))

    # Transparent Window Checkbox
    transparent_window_container, transparent_window_checkbox = create_widget(QCheckBox, "Window Transparency (requires restart) (Linux/MacOS only): ")
    transparent_window_checkbox.setChecked(state.window_transparency)
    transparent_window_checkbox.toggled.connect(lambda checked: setattr(state, 'window_transparency', checked))

    # Accent Color
    accent_color_container, accent_color_input = create_widget(QLineEdit, "Accent Color: ", width=180, height=30)
    accent_color_button = QPushButton("")
    accent_color_button.setFixedSize(21, 21)
    accent_color_button.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_accent_button_color(color_str):
        c = color_str.strip()
        accent_color_button.setStyleSheet(
            f"QPushButton {{ background-color: {c if c else 'transparent'}; border: 1px solid palette(mid); border-radius: 3px; }}"
        )

    def browse_accent_color():
        current = accent_color_input.text().strip()
        initial = QColor(current) if current else QColor()
        color = QColorDialog.getColor(initial, dialog, "Select Accent Color")
        if color.isValid():
            accent_color_input.setText(color.name())

    accent_color_input.textChanged.connect(update_accent_button_color)
    accent_color_button.clicked.connect(browse_accent_color)
    accent_color_input.setPlaceholderText("e.g. #fca7d7")
    accent_color_input.setText(state.accent_color)
    update_accent_button_color(state.accent_color)
    accent_color_container.layout().insertWidget(1, accent_color_button)

    
    # API URL Widget
    api_url_container, api_url = create_widget(QLineEdit, "API Server URL: ", width=180, height=30)
    api_url.setText(state.api_url)

    # Download Path Widget
    download_path_container, download_path = create_widget(QLineEdit, "Download Path: ")
    download_path.setText(state.download_path)
    download_path_layout = download_path_container.layout()

    def browse_download_path():
        dir_path = QFileDialog.getExistingDirectory(dialog, "Select Download Directory", state.download_path)
        if dir_path:
            download_path.setText(dir_path)

    browse_button = create_widget(QPushButton, "", width=36, height=36)[1]
    browse_button.setIconSize(QSize(24, 24))
    browse_button.setIcon(svg_icon(SVG_FOLDER, 24))
    browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
    browse_button.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
            padding: 0px;
        }
    """)

    download_path_layout.addWidget(browse_button)
    browse_button.clicked.connect(browse_download_path)


    # Image Path
    image_path_container, image_path = create_widget(QLineEdit, "Image Path: ")
    image_path.setText(state.image_path)
    image_path_layout = image_path_container.layout()
    image_path.textChanged.connect(lambda text: setattr(state, 'image_path', text))

    def browse_image_path():
        file_path = QFileDialog.getOpenFileName(dialog, "Select Image File", state.image_path, "Image Files (*.png *.jpg)")[0]
        if file_path:
            image_path.setText(file_path)

    browse_button = create_widget(QPushButton, "", width=36, height=36)[1]
    browse_button.setIconSize(QSize(24, 24))
    browse_button.setIcon(svg_icon(SVG_FOLDER, 24))
    browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
    browse_button.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
            padding: 0px;
        }
    """)
    image_path_layout.addWidget(browse_button)
    browse_button.clicked.connect(browse_image_path)

    # Enable Image Checkbox
    enable_image_container, enable_image_checkbox = create_widget(QCheckBox, "Enable Image (requires image path): ", width=180, height=30)
    enable_image_checkbox.setChecked(state.image_enabled)
    enable_image_checkbox.toggled.connect(lambda checked: setattr(state, 'image_enabled', checked))

    # Image Mode Checkbox
    image_mode_container, image_mode_checkbox = create_widget(QCheckBox, "Wallpaper Mode: ")
    image_mode_checkbox.setChecked(state.image_as_wallpaper)
    image_mode_checkbox.toggled.connect(lambda checked: setattr(state, 'image_as_wallpaper', checked))

    # Image Position Preset
    positions = ["bottom-right", "bottom-left", "top-right", "top-left", "center"]
    image_position_container, image_position_combo = create_widget(QComboBox, "Position: ", width=180, height=30)
    image_position_combo.addItems(positions)
    idx = image_position_combo.findText(state.image_position)
    image_position_combo.setCurrentIndex(idx if idx >= 0 else 0)
    image_position_combo.currentTextChanged.connect(lambda val: setattr(state, 'image_position', val))

    _slider_style = """
        QSlider::groove:horizontal {
            height: 3px;
            background: palette(mid);
            border-radius: 1px;
        }
        QSlider::handle:horizontal {
            width: 10px;
            height: 10px;
            margin: -4px 0;
            border-radius: 5px;
        }
    """

    # Image Width Slider
    image_width_container = QWidget()
    image_width_layout = QHBoxLayout(image_width_container)
    image_width_layout.addWidget(QLabel("Image Width: "))
    image_width = QSlider(Qt.Orientation.Horizontal)
    image_width.setFixedWidth(180)
    image_width.setStyleSheet(_slider_style)
    image_width.setMinimum(0)
    image_width.setMaximum(2500)
    image_width.setValue(state.image_width)
    image_width_val = QLabel(str(state.image_width))
    image_width_val.setFixedWidth(36)
    image_width.valueChanged.connect(lambda val: (setattr(state, 'image_width', val), image_width_val.setText(str(val))))
    image_width_layout.addWidget(image_width_val)
    image_width_layout.addWidget(image_width)

    # Image Offset Slider
    image_offset_container = QWidget()
    image_offset_layout = QHBoxLayout(image_offset_container)
    image_offset_layout.addWidget(QLabel("Corner Offset: "))
    image_offset = QSlider(Qt.Orientation.Horizontal)
    image_offset.setFixedWidth(180)
    image_offset.setStyleSheet(_slider_style)
    image_offset.setMinimum(0)
    image_offset.setMaximum(500)
    image_offset.setValue(state.image_offset)
    image_offset_val = QLabel(str(state.image_offset))
    image_offset_val.setFixedWidth(36)
    image_offset.valueChanged.connect(lambda val: (setattr(state, 'image_offset', val), image_offset_val.setText(str(val))))
    image_offset_layout.addWidget(image_offset_val)
    image_offset_layout.addWidget(image_offset)

    # Image Opacity Slider
    image_opacity_container = QWidget()
    image_opacity_layout = QHBoxLayout(image_opacity_container)
    image_opacity_layout.addWidget(QLabel("Image Opacity: "))
    image_opacity = QSlider(Qt.Orientation.Horizontal)
    image_opacity.setFixedWidth(180)
    image_opacity.setStyleSheet(_slider_style)
    image_opacity.setMinimum(0)
    image_opacity.setMaximum(100)
    image_opacity.setValue(state.image_opacity)
    image_opacity_val = QLabel(str(state.image_opacity))
    image_opacity_val.setFixedWidth(36)
    image_opacity.valueChanged.connect(lambda val: (setattr(state, 'image_opacity', val), image_opacity_val.setText(str(val))))
    image_opacity_layout.addWidget(image_opacity_val)
    image_opacity_layout.addWidget(image_opacity)

    # Speed Limiting
    down_speed_limit_container, down_speed_limit = create_widget(QSpinBox, "Max Download Speed (KiB, 0 for unlimited): ", width=180, height=30)
    down_speed_limit.setMinimum(0)
    down_speed_limit.setValue(state.down_speed_limit)

    up_speed_limit_container, up_speed_limit = create_widget(QSpinBox, "Max Upload Speed (KiB, 0 for unlimited): ", width=180, height=30)
    up_speed_limit.setMinimum(0)
    up_speed_limit.setValue(state.up_speed_limit)

    # Connection Configs
    max_connections_container, max_connections = create_widget(QSpinBox, "Max Connections: ", width=180, height=30)
    max_connections.setMinimum(0)
    max_connections.setValue(state.max_connections)


    # Download Configs
    max_downloads_container, max_downloads = create_widget(QSpinBox, "Max Downloads: ", width=180, height=30)
    max_downloads.setMinimum(0)
    max_downloads.setValue(state.max_downloads)

    # Interface Binding
    interface_container = QWidget()
    interface_layout = QHBoxLayout()

    interface_label = QLabel("Network Interface:")
    interface_layout.addWidget(interface_label)
    interface_select = QComboBox()
    interface_select.addItems(["None"] + state.interfaces)

    target = state.bound_interface if state.bound_interface else "None"

    index = interface_select.findText(target)
    if index >= 0:
        interface_select.setCurrentIndex(index)
    else:
        interface_select.setCurrentIndex(0)

    interface_select.setFixedWidth(180)
    interface_select.setFixedHeight(30)
    interface_layout.addWidget(interface_select)
    interface_container.setLayout(interface_layout)


    # Save / Cancel buttons
    layout = QHBoxLayout()

    save_btn = QPushButton("Save")
    cancel_btn = QPushButton("Cancel")
    save_btn.clicked.connect(lambda: handle_save())

    def handle_save():
        save_settings(
            dialog.accept, 
            api_url.text(), 
            download_path.text(), 
            down_speed_limit.value(),
            up_speed_limit.value(), 
            image_path.text(), 
            autoresume_checkbox.isChecked(), 
            max_connections.value(), 
            max_downloads.value(), 
            interface_select.currentText(),
            image_width.value(),
            image_offset.value(),
            image_opacity.value(),
            image_as_wallpaper=image_mode_checkbox.isChecked(),
            image_position=image_position_combo.currentText(),
            accent_color=accent_color_input.text().strip()
            )
        color = _accent_selection_color()
        if color:
            self.tracker_list.setStyleSheet(
                f"QComboBox QAbstractItemView::item:selected {{ background: {color}; }}"
            )
        else:
            self.tracker_list.setStyleSheet("")

    cancel_btn.clicked.connect(dialog.reject)
    layout.addWidget(cancel_btn)
    layout.addWidget(save_btn)

    tabs = QtWidgets.QTabWidget()
    create_tab("General", [autoresume_container, update_checkbox_container, transparent_window_container, accent_color_container], tabs=tabs, stretch=True)
    create_tab("Image", [enable_image_container, image_mode_container, image_position_container, image_width_container, image_offset_container, image_opacity_container], tabs=tabs, stretch=True)
    create_tab("Paths", [download_path_container, image_path_container], tabs=tabs, stretch=True)
    create_tab("Network", [interface_container, max_connections_container, max_downloads_container, up_speed_limit_container, down_speed_limit_container, api_url_container], tabs=tabs, stretch=True)


    dialog_layout.addWidget(tabs)
    dialog_layout.addLayout(layout)

    def on_dialog_finished(result): # Undo Image changes if "Save" button is not pressed
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            state.image_path = temp_image_path
            state.image_width = temp_image_width
            state.image_offset = temp_image_offset
            state.image_opacity = temp_image_opacity
            state.image_enabled = temp_image_enabled
            state.image_as_wallpaper = temp_image_as_wallpaper
            state.image_position = temp_image_position

    dialog.finished.connect(on_dialog_finished)
    dialog.exec()
