import sys
from PyQt5.QtWidgets import *
import vtk
from vtk.qt import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os

app = QApplication(sys.argv)
qss = "Stylesheet.qss"
study = "/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/"


with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())


class VTKWidget (QMainWindow):
    current = 0  # current frame starting with 0
    running = False
    slice = 1  # slice the user currently sees starting at 1
    # paths
    slices = os.listdir(study)  # list of all names of all slices
    slices.sort()
    current_slice = os.path.join(study, slices[slice])  # path of the current slice on users OS
    frames = os.listdir(current_slice)  # list of all names from all frames of the current slice
    frames.sort()
    current_frame = os.path.join(current_slice, frames[current])  # path of the current frame on users OS

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1300, 1000)
        self.frame = QFrame()

        self.mainLayout = QGridLayout()

        self.vtkWidget = MyQVTKRenderWindowInteractor(self.frame)

        self.box = Data()
        # self.box.setObjectName('Data')

        self.play = Buttons()
        self.play.setObjectName("MediaBar")

        self.userInput = UserInput()

        self.mainLayout.addWidget(self.vtkWidget, 0, 0)
        self.mainLayout.addWidget(self.play, 1, 0)
        self.mainLayout.addWidget(self.box, 0, 1)
        self.mainLayout.addWidget(self.userInput, 1, 1)

        # reader the DICOM file
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(self.current_frame)
        self.reader.Update()

        # show the DICOM file
        self.imageviewer = vtk.vtkImageViewer2()
        self.imageviewer.SetInputConnection(self.reader.GetOutputPort())
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.imageviewer.SetRenderer(self.ren)
        self.imageviewer.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.imageviewer.SetupInteractor(self.interactor)
        self.imageviewer.Render()
        self.ren.ResetCamera()
        self.imageviewer.Render()

        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)

        self.show()
        self.interactor.Initialize()
        self.interactor.RemoveObservers('MouseWheelForwardEvent')
        self.interactor.AddObserver('MouseWheelForwardEvent', self.selected_slice_forward, 1.0)  # why 1.0?
        self.interactor.RemoveObservers('MouseWheelBackwardEvent')
        self.interactor.AddObserver('MouseWheelBackwardEvent', self.selected_slice_backward, 1.0)

# reset the current slice and frame we are on

    def reset_after_changes(self):
        self.current_slice = os.path.join(study, self.slices[self.slice])
        self.frames = os.listdir(self.current_slice)
        self.frames.sort()
        self.current_frame = os.path.join(self.current_slice, self.frames[self.current])
        self.reader.SetFileName(self.current_frame)
        self.imageviewer.Render()

# scroll wheel methods
    def selected_slice_forward(self, caller, event):
        print(self.slice)
        if self.slice < 12:
            self.slice += 1
            self.reset_after_changes()
        else:
            pass

    def selected_slice_backward(self, caller, event):
        print(self.slice)
        if self.slice > 1:
            self.slice -= 1
            self.reset_after_changes()
        else:
            pass


# this class creates a widget that contains all necessary data about the current slice
class Data(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("Data")
        self.BoxLayout = QHBoxLayout()
        self.lable = QLabel('This is going to be information about the slice....')
        self.BoxLayout.addWidget(self.lable)
        self.setLayout(self.BoxLayout)


# this class handles user Input

class UserInput(QWidget):
    filepath = 'IM-13020-0001.dcm'

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("UserInput")
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


# Animation/Video


class Buttons(QWidget):
    refresh = 10000  # in fps (doesn't work because of VTK bug)

    def __init__(self):
        QWidget.__init__(self)
        self.backward = QPushButton('')
        self.backward.setObjectName("backward")
        self.backward.clicked.connect(self.backwardButton)
        self.playbtn = QPushButton('')
        self.playbtn.setObjectName("playbtn")
        self.playbtn.clicked.connect(self.playButton)
        self.forward = QPushButton('')
        self.forward.setObjectName("forward")
        self.forward.clicked.connect(self.forwardButton)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.backward)
        self.layout.addWidget(self.playbtn)
        self.layout.addWidget(self.forward)
        self.setLayout(self.layout)

    def playButton(self):
        if  Window.running:
            Window.running = False
            Window.interactor.DestroyTimer()
            self.playbtn.setStyleSheet("image: url('playButton.png') ;")
        else:
            Window.running = True
            Window.interactor.CreateRepeatingTimer(int(self.refresh))
            Window.interactor.AddObserver("TimerEvent", self.callback_func)
            self.playbtn.setStyleSheet("image: url('pauseButton.png') ;")

    def callback_func(self, caller, timer_event):
        self.forwardButton()

    def forwardButton(self):
        if Window.current < 29:
            Window.current += 1
        else:
            Window.current = 0
        Window.current_frame = os.path.join(Window.current_slice, Window.frames[Window.current])
        Window.reset_after_changes()

    def backwardButton(self):
        if Window.current > 0:
            Window.current -= 1
        else:
            Window.current = 29
        Window.current_frame = os.path.join(Window.current_slice, Window.frames[Window.current])
        Window.reset_after_changes()

# since QVTK Timer is bugged
class MyQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    def __init__(self, *arg):
        super(MyQVTKRenderWindowInteractor, self).__init__(*arg)
        self._TimerDuration = 20  # default value

    def CreateTimer(self, obj, event):
        self._Timer.start(self._TimerDuration)  # self._Timer.start(10) in orginal

    def CreateRepeatingTimer(self, duration):
        self._TimerDuration = duration
        super(MyQVTKRenderWindowInteractor, self).GetRenderWindow().GetInteractor().CreateRepeatingTimer(duration)
        self._TimeDuration = 20


Window = VTKWidget()
Window.show()
sys.exit(app.exec())
