from Model import Model
from View import View
from Controller import Controller
import tkinter as tk
import threading

if __name__ == "__main__":
    model = Model()
    root = tk.Tk()

    view = View(root)
    view.create_dashboard()
    controller = Controller(model, view)

    threading.Thread(target=model.update_data, daemon=True).start()
    threading.Thread(target=controller.start, daemon=True).start()

    root.mainloop()