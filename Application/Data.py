from PyQt5.QtWidgets import *

# this class creates a widget that contains all necessary data about the current slice
'''
(0028, 0010) Rows
(0028, 0011) Columns
(0018, 0050) Slice Thickness
(0020, 1041) Slice Location 
'''
# ----------------------Data---------------------------------------------------------------------------------

class Data(QWidget):

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setObjectName("Data")
        self.BoxLayout = QVBoxLayout()
        self.info = self.information()
        self.info.setObjectName("info")
        self.BoxLayout.addWidget(self.info)
        self.setLayout(self.BoxLayout)

    def information(self):
        self.table = QTableWidget()

        if self.window.validDataset:
            self.table.setColumnCount(2)
            self.table.setRowCount(3)
            self.table.setItem(0, 0, QTableWidgetItem("This is the current slice: "))
            self.table.setItem(1, 0, QTableWidgetItem("This is the current frame: "))
            self.table.setItem(2, 0, QTableWidgetItem("The selected Point is : "))
            self.table.setItem(0, 1, QTableWidgetItem(str(self.window.slice)))
            self.table.setItem(1, 1, QTableWidgetItem(str(self.window.current)))
            self.table.setItem(2, 1, QTableWidgetItem(str(self.window.selection)))

            self.table.horizontalHeader().hide()
            self.table.verticalHeader().hide()
            self.table.setMaximumWidth(500)
            self.table.setShowGrid(False)
            self.table.resizeColumnsToContents()
            if self.window.selectionMode == 'Multiple Point Selection' or 'Polygon Selection':
                self.table.setItem(2, 0, QTableWidgetItem("The selected Points are : "))
                if len(self.window.selection) > 1:
                    self.table.setColumnWidth(1, 200)
                    for i in range(0, len(self.window.selection)):
                        self.table.insertRow(3+i)
                        self.table.setItem(2+i, 1, QTableWidgetItem(str(self.window.selection[i-1])))

        return self.table
