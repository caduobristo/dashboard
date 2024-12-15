import time
import threading

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.running = True

    def start(self):
        def update():
            try:
                if not self.model.data_queue.empty():
                    process_data, global_data = self.model.data_queue.get()

                    self.view.display(process_data, global_data)
            except Exception as e:
                print(f"Erro ao atualizar dados na View: {e}")

            self.view.root.after(5000, update)

        update()

