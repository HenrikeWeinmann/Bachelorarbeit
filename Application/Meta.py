from PyQt5.QtWidgets import *


class Meta (QDockWidget):

    def __init__(self, window):
        QDockWidget.__init__(self)
        self.window = window
        self.setWidget(self.readMetadata())
        self.setVisible(False)
        self.setWindowTitle("Meta Data")

    def readMetadata(self):
        metawidget = QWidget()
        layout = QVBoxLayout()
        Text = QTextEdit()
        Text.setObjectName("MetaText")
        Text.setText(self.getMetadata())
        layout.addWidget(Text)
        metawidget.setLayout(layout)
        return metawidget

    def getMetadata(self):
        if self.window.validDataset:
            dataset = self.window.dataArray[self.window.slice][self.window.current]
            string = ""
            for data_element in dataset:
                string = string + "\n" + str(data_element)
            return string
        else:
            return ""