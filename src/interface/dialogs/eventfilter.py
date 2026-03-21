from utils.logging.logs import consoleLog
from utils.data.state import state
from PySide6.QtCore import QEvent

def eventFilter(self, obj, event):
    try:
        if obj == state.trackertable.viewport():
            if event.type() == QEvent.Type.MouseMove:
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                idx = state.trackertable.indexAt(pos)
                new_row = idx.row() if idx.isValid() else -1
                if new_row != self._tracker_hovered_row or state.trackertable is not self._tracker_hovered_table:
                    self._tracker_hovered_row = new_row
                    self._tracker_hovered_table = state.trackertable
                    state.trackertable.viewport().update()
            elif event.type() == QEvent.Type.Leave:
                self._tracker_hovered_row = -1
                self._tracker_hovered_table = None
                state.trackertable.viewport().update()
        if obj == self.downloadList.viewport():
            if event.type() == QEvent.Type.MouseMove:
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                idx = self.downloadList.indexAt(pos)
                new_row = idx.row() if idx.isValid() else -1
                if new_row != self._hovered_row:
                    old_row = self._hovered_row
                    self._hovered_row = new_row
                    self._invalidate_hover_row(old_row)
                    self._invalidate_hover_row(new_row)
            elif event.type() == QEvent.Type.Leave:
                old_row = self._hovered_row
                self._hovered_row = -1
                self._invalidate_hover_row(old_row)
    except (RuntimeError, AttributeError) as e:
        consoleLog(f"Exception in EventFilter: {e}")
    return super(type(self), self).eventFilter(obj, event)
