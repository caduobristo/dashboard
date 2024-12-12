import threading
import time
from GetProcessInfos import list_processes, get_cpu_usage, get_memory_info, get_disk_info

class Model:
    def __init__(self):
        self.process_data = {}
        self.global_data = {}  # Certifique-se de que isso está inicializado
        self.lock = threading.Lock()

    def update_data(self):
        while True:
            try:
                # Coleta de dados de processos e globais
                process_data = list_processes()
                global_data = {
                    "cpu_usage": get_cpu_usage(),
                    "memory": get_memory_info(),
                    "disk": get_disk_info(),
                }

                # Atualiza os dados protegidos pelo lock
                with self.lock:
                    self.process_data = process_data
                    self.global_data = global_data
            except Exception as e:
                print(f"Erro ao atualizar dados: {e}")
            
            time.sleep(5)
