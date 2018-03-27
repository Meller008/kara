from PyQt5.QtWidgets import QApplication
import sys
import form.main_window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle(QStyleFactory().create("fusion"))
    main = form.main_window.MainWindow(sys.argv)
    sys.exit(app.exec_())

