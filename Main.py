from Model import Model
from View import SystemView
from Controller import SystemController

if __name__ == "__main__":
    model = Model()
    view = SystemView()
    controller = SystemController(model, view)

    controller.start()