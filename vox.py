from core.engine import VoxEngine
from ui.widget import VoxWidget

def main():
    engine = VoxEngine()
    print("Started")
    ui = VoxWidget(engine)
    engine.start()

    engine.attach_ui(ui)
    ui.mainloop()

if __name__ == "__main__":
    main()

