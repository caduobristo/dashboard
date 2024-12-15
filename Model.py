import threading
import time
import queue
from GetProcessInfos import list_processes
from GetGlobalInfos import list_global_infos

class Model:
    def __init__(self):
        self.process_data = {}
        self.global_data = {}  # Certifique-se de que isso está inicializado
        self.data_queue = queue.Queue()

    def update_data(self):
        while True:
            try:
                # Coleta de dados de processos
                process_data = list_processes()
                global_data = list_global_infos()

                # Atualiza os dados protegidos pelo lock
                self.data_queue.put((process_data, global_data))

            except Exception as e:
                print(f"Erro ao atualizar dados: {e}")
            
            time.sleep(5)
