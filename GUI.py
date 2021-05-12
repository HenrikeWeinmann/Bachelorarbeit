import sys
from PyQt6.QtWidgets import *
import vtk
app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())


class Window(QWidget):
    filepath = ''

    def __init__(self):
        super().__init__()

        self.setGeometry(200,300,1000,600)
        # Box links
        self.box = QWidget()
        self.box.setObjectName("box")

        self.playbtn = QPushButton('', parent=self.box)
        self.playbtn.setObjectName("playbtn")
        self.playbtn.clicked.connect(self.playButton)

        self.innerLeft = QVBoxLayout()
        self.innerLeft.addStretch()

        self.center = QHBoxLayout()
        self.center.addWidget(self.playbtn)

        self.innerLeft.addLayout(self.center)
        self.box.setLayout(self.innerLeft)

        # Box oben rechts
        self.box2 = QWidget()
        self.box2.setObjectName("box2")

        # Box unten rechts
        self.box3 = QWidget()
        self.box3.setObjectName("box3")
        self.box3.setMaximumWidth(200)
        self.bottomRight = QHBoxLayout()
        self.button2 = QPushButton('LOL')
        self.button2.setMaximumWidth(100)

        self.input = QLineEdit('filepath')
        self.input.setMaxLength(25)
        self.input.editingFinished.connect(self.setFilepath)

        self.bottomRight.addWidget(self.button2)
        self.bottomRight.addWidget(self.input)
        self.box3.setLayout(self.bottomRight)

        self.innerRight = QVBoxLayout()
        self.innerRight.addWidget(self.box2)
        self.innerRight.addWidget(self.box3)

        # Layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.box)
        self.mainLayout.addLayout(self.innerRight)

        self.setLayout(self.mainLayout)

    def playButton(self):
        print('start')


    def setFilepath(self):
        print(self.input.text())
        Window.filepath = self.input.text()




window = Window()
window.show()

sys.exit(app.exec())
