import threading
import os

shutdown_event = threading.Event()

def closehelper():
    shutdown_event.set()

def force_exit():
    os._exit(0)