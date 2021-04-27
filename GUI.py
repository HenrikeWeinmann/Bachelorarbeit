import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
#this is a test
app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss,"r") as fh:
    app.setStyleSheet(fh.read())


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.createButton()



    def createButton(self):
        button = QPushButton('hahahaha BUTTON',self)







window = Window()
window.show()

sys.exit(app.exec())
