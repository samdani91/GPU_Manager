import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from window import MainWindow
from dependency_checker import DependencyChecker



def main():
    app = QApplication(sys.argv)


    checker = DependencyChecker()
    checker.show()


    def on_ready():
        checker.close() 
        win = MainWindow()
        win.show()
        app.main_window = win  

    checker.dependencies_ready.connect(on_ready)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
