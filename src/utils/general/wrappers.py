from utils.logging.logs import consoleLog

def run_thread(thread):
    target_name = thread._target.__name__
    try:
        thread.start()
        consoleLog(f"Started Thread: {target_name}")
    except Exception as e:
        consoleLog(f"Exception while starting thread {target_name}: {e}")