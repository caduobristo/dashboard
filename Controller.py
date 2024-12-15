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

                    self.view.Display(process_data, global_data)
            except Exception as e:
                print(f"Erro ao atualizar dados na View: {e}")

            # Agenda a atualização a cada 5seg sem bloquear a interface gráfica
            self.view.root.after(5000, update)

        update()

