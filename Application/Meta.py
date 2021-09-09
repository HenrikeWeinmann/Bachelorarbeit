from PyQt5.QtWidgets import *

'''
(0028, 0010) Rows
(0028, 0011) Columns
(0018, 0050) Slice Thickness
(0020, 1041) Slice Location 
'''

class Meta (QDockWidget):

    def __init__(self, window):
        QDockWidget.__init__(self)
        self.window = window
        self.setWidget(self.readMetadata())
        self.setVisible(False)

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
            dataset = self.window.dataArray[0][0]
            string = ""
            for data_element in dataset:

                string = string + "\n" + str(data_element)
                print(string)
            return string

        else:
            return ""