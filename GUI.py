import sys
from PyQt6.QtWidgets import *
import vtk
app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(200,300,1000,600)
        # Box links
        box = QWidget(self)
        box.setObjectName("box")
        playbtn = QPushButton('', parent=box)
        playbtn.setObjectName("playbtn")
        innerLeft = QVBoxLayout()
        innerLeft.addStretch()
        center = QHBoxLayout()
        center.addWidget(playbtn)
        innerLeft.addLayout(center)
        box.setLayout(innerLeft)
        # Box oben rechts
        box2 = QWidget()
        box2.setObjectName("box2")

        # Box unten rechts
        box3 = QWidget()
        box3.setObjectName("box3")
        grid3 = QGridLayout()
        button2 = QPushButton('LOL')
        button2.setMaximumWidth(100)
        grid3.addWidget(button2)
        box3.setLayout(grid3)

        innerRight = QVBoxLayout()
        innerRight.addWidget(box2)
        innerRight.addWidget(box3)

        # Layout
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(box)
        mainLayout.addLayout(innerRight)

        self.setLayout(mainLayout)



window = Window()
window.show()

sys.exit(app.exec())
