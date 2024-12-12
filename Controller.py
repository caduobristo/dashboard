import time

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.running = True

    def start(self):
        while self.running:
            with self.model.lock:
                process_data = self.model.process_data.copy()  # Copia os dados para evitar conflitos
            self.view.display(process_data)
            time.sleep(2)  # Atualiza a cada 2 segundos   