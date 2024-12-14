import time

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.running = True

    def start(self):
        while self.running:
            with self.model.lock:
                process_data = self.model.process_data.copy()
                global_data = self.model.global_data.copy()  # Adiciona cópia correta do global_data
            
            # Certifique-se de que ambos os dados são passados para a View
            self.view.display(process_data, global_data)
            time.sleep(10)

