from Model import Model
from View import View
from Controller import Controller
import tkinter as tk
import threading

if __name__ == "__main__":
    model = Model()
    root = tk.Tk()

    controller = Controller(model, None)
    view = View(root, controller)
    controller.view = view

    # Thread para coletar dados
    threading.Thread(target=model.update_data, daemon=True).start()
    # Thread para atualizar os dados na interface gráfica
    threading.Thread(target=controller.start, daemon=True).start()

    # Interface gráfica roda na thread principal
    root.mainloop()
