from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*

class Help (QDockWidget):

    def __init__(self, window):
        QDockWidget.__init__(self)
        self.window = window
        self.setWidget(self.help())
        self.setVisible(False)
        self.setWindowTitle("Help")

    def help(self):
        helpwidget = QWidget()
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText('<a href="https://github.com/HenrikeWeinmann/Bachelorarbeit#readme">GitHub Instructions</a>')
        label.setOpenExternalLinks(True)
        layout = QHBoxLayout()
        layout.addWidget(label)
        helpwidget.setLayout(layout)
        return helpwidget