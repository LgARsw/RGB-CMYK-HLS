import sys
from PyQt5.QtWidgets import QApplication
from viewmodel.converter_vm import ConverterViewModel
from view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    view_model = ConverterViewModel()
    window = MainWindow(view_model)

    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
