from PyQt5.QtWidgets import QApplication
import sys, traceback, time
import form.main_window
from datetime import datetime

def ex(t, v, tb):
    print(traceback.print_exception(t, v, tb))
    with open("ERR.txt", "a") as file:
        file.write("\n---===Error===---\n")
        file.write("Time = %s" % datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        traceback.print_exception(t, v, tb, file=file)
    while 1:
        time.sleep(5)

sys.excepthook = ex

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = form.main_window.MainWindow()
    sys.exit(app.exec_())

