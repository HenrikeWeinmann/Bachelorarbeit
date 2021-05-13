import sys
from PyQt5.QtWidgets import *
import vtk
from vtk.qt import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())

class VTKWidget (QMainWindow):

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1000, 600)
        self.frame = QFrame()

        self.mainLayout = QGridLayout()

        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        self.box = Data()

        self.play = PlayButton()

        self.userInput = UserInput()

        self.mainLayout.addWidget(self.vtkWidget, 0, 0)
        self.mainLayout.addWidget(self.play, 1, 0)
        self.mainLayout.addWidget(self.box, 0, 1)
        self.mainLayout.addWidget(self.userInput, 1, 1)

        # reader the dicom file
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName("IM-13020-0001.dcm")
        self.reader.Update()

        # show the dicom flie
        self.imageviewer = vtk.vtkImageViewer2()
        self.imageviewer.SetInputConnection(self.reader.GetOutputPort())
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.imageviewer.SetRenderer(self.ren)
        self.imageviewer.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.imageviewer.SetupInteractor(self.iren)
        self.imageviewer.Render()
        self.ren.ResetCamera()
        self.imageviewer.Render()

        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()

class Data(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.BoxLayout = QHBoxLayout()
        self.lable = QLabel('This is going to be information about the slice....')
        self.BoxLayout.addWidget(self.lable)
        self.setLayout(self.BoxLayout)


class UserInput(QWidget):
    filepath = 'IM-13020-0001.dcm'

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("box3")
        self.setGeometry(300, 300, 300, 300)

        self.button2 = QPushButton('LOL')
        self.button2.setMaximumWidth(100)

        self.input = QLineEdit('filepath')
        self.input.setMaxLength(25)
        self.input.editingFinished.connect(self.setFilepath)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)


    def setFilepath(self):
        print(self.input.text())
        UserInput.filepath = self.input.text()


class PlayButton(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.playbtn = QPushButton('')
        self.playbtn.setObjectName("playbtn")
        self.playbtn.clicked.connect(self.playButton)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.playbtn)
        self.setLayout(self.layout)


    def playButton(self):
        print('start')



Window = VTKWidget()
Window.show()

sys.exit(app.exec())
