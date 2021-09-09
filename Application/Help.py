from PyQt5.QtWidgets import *


class Help (QDockWidget):

    def __init__(self, window):
        QDockWidget.__init__(self)
        self.window = window
        self.setWidget(self.help())
        self.setVisible(False)


    def help(self):
        helpwidget = QWidget()

        return helpwidget