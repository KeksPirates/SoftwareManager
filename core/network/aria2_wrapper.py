from .aria2_integration import run_aria2p
from core.utils.data.state import state
from core.utils.general.logs import consoleLog

def start_client():
    global aria2
    aria2 = run_aria2p()
    consoleLog("Started Aria2p")

def add_magnet(uri):
    aria2.add_magnet(uri)
    consoleLog("Magnet URI added to Aria2")



