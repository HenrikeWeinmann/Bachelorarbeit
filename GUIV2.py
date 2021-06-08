import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pydicom as dcm


app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())


class MainWindow (QMainWindow):
    study = "/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/"
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
    selection = []

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1300, 1000)
        self.centralWidget = QFrame()

        self.mainLayout = QGridLayout()
        self.dicom = Dicom(self)

        self.data = Data()
        self.data.info.setText(self.information())
        self.data.setObjectName("data")

        self.play = Buttons(self)
        self.play.setObjectName("MediaBar")

        self.userInput = UserInput(self)
        self.userInput.setObjectName("userInput")

        self.mainLayout.addWidget(self.dicom, 0, 0)
        self.mainLayout.addWidget(self.play, 1, 0)
        self.mainLayout.addWidget(self.data, 0, 1)
        self.mainLayout.addWidget(self.userInput, 1, 1)

        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

# reset the current slice and frame we are on
    def reset_after_changes(self):
        self.slices = os.listdir(self.study)  # list of all names of all slices
        self.slices.sort()
        self.current_slice = os.path.join(Window.study, self.slices[self.slice])
        self.frames = os.listdir(self.current_slice)
        self.frames.sort()
        self.current_frame = os.path.join(self.current_slice, self.frames[self.current])
        print('reset')

    def information(self):
        return "This is the current slice: " + self.slices[self.slice] + "\n" \
                                                                         "This is the current frame: " + self.frames[
                   self.current] + "\n" \
                                   "The selected Point is : "


class Dicom (FigureCanvas):

    def __init__(self, window):
        fig, self.ax = plt.subplots()
        super().__init__(fig)
        self.setParent(window)
        self.dicom = dcm.dcmread(window.current_frame)
        self.imgarr = self.dicom.pixel_array
        plt.imshow(self.imgarr)


    # scroll wheel methods
    def selected_slice_forward(self):
        print(self.window.slice)
        if self.window.slice < len(self.window.slices) - 1:
            self.window.slice += 1
            self.window.reset_after_changes()
        else:
            pass

    def selected_slice_backward(self):
        print(self.window.slice)
        if self.window.slice > 1:
            self.window.slice -= 1
            self.window.reset_after_changes()
        else:
            pass

    def selection(self):
        pass



# this class handles user Input
class UserInput(QWidget):
    filepath = 'IM-13020-0001.dcm'

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.button2 = QPushButton('SUBMIT')
        self.button2.setObjectName("submit")
        self.button2.clicked.connect(self.set_filepath)
        self.label = QLabel("Please enter the filepath to a study directory")
        self.label.setObjectName("enterfilepath")
        self.input = QLineEdit('filepath')
        self.input.setMaxLength(100)
        self.input.editingFinished.connect(self.set_filepath)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.inner = QHBoxLayout()
        self.inner.addWidget(self.input)
        self.inner.addWidget(self.button2)
        self.layout.addLayout(self.inner)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def set_filepath(self):
        self.filepath = self.input.text()
        print(self.filepath)
        self.check_and_set_filepath()

    def check_and_set_filepath(self):
        if os.path.exists(self.filepath):
            self.window.study = self.filepath
            self.window.reset_after_changes()
            print("this ist the study path: " + self.window.study)


# Animation/Video
class Buttons(QWidget):
    refresh = 10000  # in fps (doesn't work because of VTK bug)

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.backward = QPushButton('')
        self.backward.setObjectName("backward")
        self.backward.clicked.connect(self.backward_button)
        self.playbtn = QPushButton('')
        self.playbtn.setObjectName("playbtn")
        self.playbtn.clicked.connect(self.play_button)
        self.forward = QPushButton('')
        self.forward.setObjectName("forward")
        self.forward.clicked.connect(self.forward_button)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.backward)
        self.layout.addWidget(self.playbtn)
        self.layout.addWidget(self.forward)
        self.setLayout(self.layout)

    def play_button(self):
        if self.window.running:
            self.window.running = False
            self.playbtn.setStyleSheet("image: url('playButton.png') ;")
        else:
            self.window.running = True
            self.playbtn.setStyleSheet("image: url('pauseButton.png') ;")

    def callback_func(self, caller, timer_event):
        self.forward_button()

    def forward_button(self):
        if self.window.current < 29:
            self.window.current += 1
        else:
            self.window.current = 0
        self.window.current_frame = os.path.join(self.window.current_slice, self.window.frames[self.window.current])
        self.window.reset_after_changes()

    def backward_button(self):
        if self.window.current > 0:
            self.window.current -= 1
        else:
            self.window.current = 29
        self.window.current_frame = os.path.join(self.window.current_slice, self.window.frames[self.window.current])
        self.window.reset_after_changes()


# this class creates a widget that contains all necessary data about the current slice
class Data(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("Data")
        self.BoxLayout = QVBoxLayout()
        self.label = QLabel('This is going to be information about the slice: ')
        self.info = QLabel("")
        self.info.setObjectName("info")
        self.BoxLayout.addWidget(self.label)
        self.BoxLayout.addWidget(self.info)
        self.BoxLayout.addStretch()
        self.setLayout(self.BoxLayout)


Window = MainWindow()
Window.show()
sys.exit(app.exec())