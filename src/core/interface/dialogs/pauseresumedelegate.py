from core.interface.dialogs.theme import _theme_colors, SVG_PLAY, SVG_PAUSE, SVG_FOLDER
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout
from core.interface.utils.svghelper import svg_icon
from PySide6.QtCore import Qt, QSize, Signal
from core.utils.data.state import state
from PySide6 import QtWidgets
import libtorrent as lt

class PauseResumeDelegate(QStyledItemDelegate):
    clicked = Signal(int)

    def paint(self, painter, option, index):
        from core.interface.gui import MainWindow

        opt = QtWidgets.QStyleOptionViewItem(option)
        option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus
        option.state &= ~QtWidgets.QStyle.StateFlag.State_Selected

        hovered_row = MainWindow._instance._hovered_row if MainWindow._instance else -1
        if index.row() == hovered_row:
            painter.save()
            painter.fillRect(option.rect, _theme_colors()["hover"])
            painter.restore()
        super().paint(painter, opt, index)

    def setEditorData(self, editor, index):
        button = editor.findChild(QtWidgets.QPushButton)
        if not button:
            return
        try:
            with state.downloads_lock:
                keys = list(state.active_downloads.keys())
                if index.row() >= len(keys):
                    return
                magnet_link = keys[index.row()]
                magnetdl = state.active_downloads[magnet_link]
            status = magnetdl.status()
        except (RuntimeError, IndexError, KeyError):
            return

        if status.state == lt.torrent_status.seeding:
            button.setIcon(svg_icon(SVG_FOLDER, 18))
            button.setText("")
        else:
            is_user_paused = status.paused and not status.auto_managed
            button.setIcon(svg_icon(SVG_PLAY if is_user_paused else SVG_PAUSE, 18))
            button.setText("")


    def createEditor(self, parent, option, index):
        try:
            with state.downloads_lock:
                keys = list(state.active_downloads.keys())
                if index.row() >= len(keys):
                    return QWidget(parent)
                magnet_link = keys[index.row()]
                magnetdl = state.active_downloads[magnet_link]
            status = magnetdl.status()
        except (RuntimeError, IndexError, KeyError):
            return QWidget(parent)

        widget = QWidget(parent)
        widget.setStyleSheet("border: none; background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        if status.state == lt.torrent_status.seeding:
            btnPause = QtWidgets.QPushButton()
            btnPause.setIcon(svg_icon(SVG_FOLDER, 18))
        else:
            btnPause = QtWidgets.QPushButton()
            is_user_paused = status.paused and not status.auto_managed
            btnPause.setIcon(svg_icon(SVG_PLAY if is_user_paused else SVG_PAUSE, 18))
        btnPause.setIconSize(QSize(18, 18))
        btnPause.setFixedSize(30, 30)
        btnPause.setCursor(Qt.CursorShape.PointingHandCursor)
        btnPause.setStyleSheet("QPushButton { border: none; background: transparent; padding: 0px; }")
        btnPause.clicked.connect(lambda: self.clicked.emit(index.row()))
        layout.addStretch()
        layout.addWidget(btnPause)
        layout.addStretch()
        widget.setLayout(layout)
        return widget


    def editorEvent(self, event, model, option, index):
        return False
