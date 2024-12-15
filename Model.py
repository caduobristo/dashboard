import threading
import time
import queue
from GetProcessInfos import list_processes
from GetGlobalInfos import get_cpu_infos, get_memory_info, get_disk_info

class Model:
    def __init__(self):
        self.process_data = {}
        self.global_data = {}  # Certifique-se de que isso está inicializado
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()

    def update_data(self):
        while True:
            try:
                # Coleta de dados de processos
                process_data = list_processes()

                # Coleta dados globais
                cpu_infos = get_cpu_infos()
                memory_infos = get_memory_info()
                disk_infos = get_disk_info()

                global_data = {
                    "cpu_usage": cpu_infos['cpu_usage'],
                    "idle": cpu_infos.get('idle', 'N/A'),
                    "kernel": cpu_infos.get('kernel', 'N/A'),
                    "user": cpu_infos.get('user', 'N/A'),
                    "n_processors": cpu_infos.get('n_processors', 'N/A'),
                    "page_size": cpu_infos.get('page_size', 'N/A'),
                    "memory_used": memory_infos.get('used', 'N/A'),
                    "memory_total": memory_infos.get('total', 'N/A'),
                    "memory_percent": memory_infos.get('percent', 'N/A'),
                    "disk_used": disk_infos.get('used', 'N/A'),
                    "disk_total": disk_infos.get('total', 'N/A'),
                    "disk_percent": disk_infos.get('percent', 'N/A')
                }

                # Atualiza os dados protegidos pelo lock
                self.data_queue.put((process_data, global_data))

            except Exception as e:
                print(f"Erro ao atualizar dados: {e}")
            
            time.sleep(5)
