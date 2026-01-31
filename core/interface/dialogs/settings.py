from core.utils.config.settings import save_settings
from core.utils.data.state import state
from core.utils.general.logs import consoleLog
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QLineEdit, 
    QPushButton, 
    QWidget, 
    QVBoxLayout, 
    QDialog, 
    QLabel, 
    QHBoxLayout,
    QSpinBox,
    QCheckBox,
    QFileDialog,
)
import platform


def settings_dialog(self):

        consoleLog("Settings dialog opened")
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedSize(800, 550)

        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(QLabel("Settings"))

        def close_settings():
            dialog.reject()

        update_checkbox_container = QWidget()
        update_checkbox_layout = QHBoxLayout()

        # ignore updates checkbox

        if platform.system() == "Windows":
            update_checkbox = QCheckBox()
            update_checkbox_container.setLayout(update_checkbox_layout)
            update_checkbox_layout.addWidget(QLabel("Ignore Updates: "))
            update_checkbox_layout.addStretch()
            update_checkbox.setChecked(state.ignore_updates)
            update_checkbox.toggled.connect(lambda checked: setattr(state, 'ignore_updates', checked))
            update_checkbox_layout.addWidget(update_checkbox)
            dialog.layout().addWidget(update_checkbox_container)

        # auto-resume downloads checkbox

        autoresume_container = QWidget()
        autoresume_layout = QHBoxLayout()

        autoresume_checkbox = QCheckBox()
        autoresume_container.setLayout(autoresume_layout)
        autoresume_layout.addWidget(QLabel("Auto-Resume Downloads: "))

        autoresume_layout.addStretch()
        autoresume_checkbox.setChecked(state.autoresume)
        autoresume_checkbox.toggled.connect(lambda checked: setattr(state, 'autoresume', checked))
        autoresume_layout.addWidget(autoresume_checkbox)
        dialog.layout().addWidget(autoresume_container)

        ##################
        # SERVER SETTING #
        ##################
        
        api_url_container = QWidget()
        api_url_layout = QHBoxLayout()

        api_url = QLineEdit()
        api_url_layout.addWidget(QLabel("API Server URL:"))
        api_url_layout.addWidget(api_url)
        api_url_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        api_url_container.setLayout(api_url_layout)
        api_url.setText(state.api_url)
        dialog.layout().addWidget(api_url_container)

        #################
        # DOWNLOAD PATH #
        #################

        download_path_container = QWidget()
        download_path_layout = QHBoxLayout()

        download_path = QLineEdit()
        download_path_layout.addWidget(QLabel("Download Path:"))
        download_path_layout.addWidget(download_path)
        download_path_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        download_path_container.setLayout(download_path_layout)
        download_path.setText(state.download_path)
        dialog.layout().addWidget(download_path_container)

        def browse_download_path():
            dir_path = QFileDialog.getExistingDirectory(dialog, "Select Download Directory", state.download_path)
            if dir_path:
                download_path.setText(dir_path)

        browse_button = QPushButton("📁")
        download_path_layout.addWidget(browse_button)
        browse_button.clicked.connect(browse_download_path)

        ###############
        # IMAGE PATH #
        ###############

        image_path_container = QWidget()
        image_path_layout = QHBoxLayout()

        image_path = QLineEdit()
        image_path_layout.addWidget(QLabel("Image Path (requires restart):"))
        image_path_layout.addWidget(image_path)
        image_path_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        image_path_container.setLayout(image_path_layout)
        image_path.setText(state.image_path)
        dialog.layout().addWidget(image_path_container)

        def browse_image_path():
            file_path = QFileDialog.getOpenFileName(dialog, "Select Image File", state.image_path, "Image Files (*.png *.jpg)")[0]
            if file_path:
                image_path.setText(file_path)

        browse_button = QPushButton("📁")
        image_path_layout.addWidget(browse_button)
        browse_button.clicked.connect(browse_image_path)

        ##################
        # SPEED LIMITING #
        ##################

        down_speed_limit_container = QWidget()
        down_speed_limit_layout = QHBoxLayout()

        down_speed_limit_layout.addWidget(QLabel("Max Download Speed (KiB, 0 for unlimited): "))
        down_speed_limit = QSpinBox()
        down_speed_limit.setMinimum(0)
        down_speed_limit.setMaximum(10000000)
        down_speed_limit.setValue(state.down_speed_limit)
        down_speed_limit_container.setLayout(down_speed_limit_layout)
        down_speed_limit_layout.addWidget(down_speed_limit)
        down_speed_limit.setFixedWidth(180)
        down_speed_limit.setFixedHeight(30)
        dialog.layout().addWidget(down_speed_limit_container)
        
        up_speed_limit_container = QWidget()
        up_speed_limit_layout = QHBoxLayout()

        up_speed_limit_layout.addWidget(QLabel("Max Upload Speed (KiB, 0 for unlimited): "))
        up_speed_limit = QSpinBox()
        up_speed_limit.setMinimum(0)
        up_speed_limit.setMaximum(10000000)
        up_speed_limit.setValue(state.up_speed_limit)
        up_speed_limit_container.setLayout(up_speed_limit_layout)
        up_speed_limit_layout.addWidget(up_speed_limit)
        up_speed_limit.setFixedWidth(180)
        up_speed_limit.setFixedHeight(30)
        dialog.layout().addWidget(up_speed_limit_container)

        ######################
        # CONNECTION CONFIGS #
        ######################

        max_connections_container = QWidget()
        max_connections_layout = QHBoxLayout()

        max_connections_layout.addWidget(QLabel("Max Connections: "))
        max_connections = QSpinBox()
        max_connections.setMinimum(0)
        max_connections.setMaximum(10000000)
        max_connections.setValue(state.max_connections)
        max_connections_container.setLayout(max_connections_layout)
        max_connections_layout.addWidget(max_connections)
        max_connections.setFixedWidth(180)
        max_connections.setFixedHeight(30)
        dialog.layout().addWidget(max_connections_container)

        ####################
        # DOWNLOAD CONFIGS #
        ####################

        max_downloads_container = QWidget()
        max_downloads_layout = QHBoxLayout()

        max_downloads_layout.addWidget(QLabel("Max Downloads: "))
        max_downloads = QSpinBox()
        max_downloads.setMinimum(0)
        max_downloads.setMaximum(10000000)
        max_downloads.setValue(state.max_downloads)
        max_downloads_container.setLayout(max_downloads_layout)
        max_downloads_layout.addWidget(max_downloads)
        max_downloads.setFixedWidth(180)
        max_downloads.setFixedHeight(30)
        dialog.layout().addWidget(max_downloads_container)

        ###############
        # SAVE/CANCEL #
        ###############

        layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(lambda: save_settings(close_settings, api_url.text(), download_path.text(), down_speed_limit.value(), up_speed_limit.value(), image_path.text(), None, max_connections.value(), max_downloads.value()))

        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)
        layout.addWidget(save_btn)

        dialog.layout().addLayout(layout)
        
        dialog.exec()
