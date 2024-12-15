import time
import queue
import threading
from GetProcessInfos import list_processes
from GetGlobalInfos import list_global_infos

class Model:
    def __init__(self):
        self.process_data = {}
        self.global_data = {}
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()

    def update_data(self):
        while True:
            try:
                # Garante que apenas um thread pode acessar a fila
                with self.lock:
                    process_data = list_processes()
                    global_data = list_global_infos()

                    self.data_queue.put((process_data, global_data))

            except Exception as e:
                print(f"Erro ao atualizar dados: {e}")
            
            time.sleep(5)
