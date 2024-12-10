import threading
import time
from GetProcessInfos import list_processes

class Model:
    def __init__(self):
        self.process_data = {}
        self.lock = threading.Lock()

    def update_data(self):
        while True:
            data = list_processes()

            with self.lock:
                self.process_data = data

    time.sleep(5)
