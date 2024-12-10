import threading
import time

class SystemController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def start(self):
        # Cria uma thread para atualização dos dados
        data_thread = threading.Thread(target=self.model.update_data, daemon=True)
        data_thread.start()

        # Exibe as informações periodicamente
        while True:
            with self.model.lock:
                process_data = self.model.process_data.copy()  # Copia os dados para evitar conflitos
            self.view.display(process_data)
            time.sleep(2)  # Atualiza a cada 2 segundos