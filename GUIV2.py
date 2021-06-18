import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap
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
        self.setMaximumWidth(1300)
        self.setMaximumHeight(1000)
        self.centralWidget = QFrame()

        self.mainLayout = QGridLayout()
        self.mainLayout.setSpacing(3)
        self.dicom = Dicom(self)

        self.menu = self.toolbar()
        self.play = MediaBar(self)

        self.right = self.rightSide()

        self.mainLayout.addWidget(self.menu, 0, 0, 1, 2)  # row, column , rowSpan, columnSpan
        self.mainLayout.addWidget(self.dicom, 1, 0, 2, 1)
        self.mainLayout.addWidget(self.play, 3, 0)
        self.mainLayout.addWidget(self.right, 1, 1, 3, 1)

        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

# reset the current slice and frame we are on
    def reset_after_changes(self):
        self.slices = os.listdir(self.study)  # list of all names of all slices
        self.slices.sort()
        self.current_slice = os.path.join(self.study, self.slices[self.slice])
        self.frames = os.listdir(self.current_slice)
        self.frames.sort()
        self.current_frame = os.path.join(self.current_slice, self.frames[self.current])
        self.update_fig()
        self.data.info.setText(self.information())

    def information(self):
        return "This is the current slice: " + self.slices[self.slice] + "\n" \
               "This is the current frame: " + self.frames[self.current] + "\n" \
               "The selected Point is : " + str(self.selection)

    def toolbar(self):
        toolbar = QToolBar()
        toolbar.setObjectName("Toolbar")
        self.selectionMode = QComboBox()
        self.selectionMode.addItem("Single Point Selection")
        self.selectionMode.addItem("Multiple Point Selection")
        imageMode = QComboBox()
        imageMode.addItem('bone')
        imageMode.addItem('gist_gray')
        imageMode.addItem('copper')
        imageMode.activated.connect(lambda: Dicom.changecmap(self.dicom, imageMode.currentText(), self))
        toolbar.addWidget(self.selectionMode)
        toolbar.addWidget(imageMode)
        clear = QPushButton("clear")
        clear.setObjectName("clear")
        clear.clicked.connect(lambda: Dicom.clear(self.dicom, self))
        toolbar.addWidget(clear)
        return toolbar

    def rightSide(self):
        rightSide = QWidget()
        rightSide.setObjectName("right")
        self.data = Data()
        self.data.info.setText(self.information())
        self.data.setObjectName("data")
        self.userInput = UserInput(self)
        self.userInput.setObjectName("userInput")
        layout = QVBoxLayout()
        layout.addWidget(self.data)
        layout.addWidget(self.userInput)
        layout.addStretch()
        rightSide.setLayout(layout)
        return rightSide

    def update_fig(self):
        plt.clf()
        self.dicom.dcmfile = dcm.dcmread(self.current_frame)
        self.dicom.imgarr = self.dicom.dcmfile.pixel_array
        self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap)
        self.cnv = plt.imshow(self.dicom.canvas, Dicom.customcmap(self.dicom))
        self.dicom.draw()
        self.mainLayout.addWidget(self.dicom, 1, 0, 2, 1)


class Dicom (FigureCanvas):

    def __init__(self, window):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(window)
        self.cmap = 'bone'
        self.dcmfile = dcm.dcmread(window.current_frame)
        self.imgarr = self.dcmfile.pixel_array
        self.canvas = np.empty(self.imgarr.shape)
        self.canvas[:] = 0
        self.img = plt.imshow(self.imgarr, self.cmap)
        self.cnv = plt.imshow(self.canvas, cmap=self.customcmap())
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.selection)

    # scroll wheel
    def wheelEvent(self, event):
        window = self.parent().parent()
        change = event.angleDelta().y()/120
        if change > 0:
            if window.slice < len(window.slices) - 1:
                window.slice += 1
                window.reset_after_changes()
            else:
                pass
        else:
            if window.slice > 1:
                window.slice -= 1
                window.reset_after_changes()
            else:
                pass

    def changecmap(self, color, window):
        self.cmap = color
        window.update_fig()
        print(window.dicom.cmap)

    def customcmap(self):
        # Choose colormap
        cmap = plt.cm.Reds

        # Get the colormap colors
        my_cmap = cmap(np.arange(cmap.N))

        # Set alpha
        my_cmap[:, -1] = np.linspace(0, 1, cmap.N)

        # Create new colormap
        my_cmap = ListedColormap(my_cmap)
        return my_cmap

    def selection(self, event):
        window = self.parent().parent()
        print(window.selectionMode.currentText())
        x = event.xdata
        y = event.ydata
        if window.selectionMode.currentText() == 'Single Point Selection':
            if x and y > 0:
                point = [int(x), int(y)]
                window.dicom.canvas[:] = 0
                window.dicom.canvas[int(y), int(x)] = 255
                window.selection = [point]
                window.reset_after_changes()
        elif window.selectionMode.currentText() == 'Multiple Point Selection':
            if x and y > 0:
                point = [int(x), int(y)]
                window.dicom.canvas[int(y), int(x)] = 255
                window.selection = [point]
                window.reset_after_changes()


    def clear(self, window):
        window.selection = []
        window.reset_after_changes()



# this class handles user Input
class UserInput(QWidget):
    filepath = 'IM-13020-0001.dcm'

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setObjectName("UserInput")
        self.button2 = QPushButton('SUBMIT')
        self.button2.setObjectName("submit")
        self.button2.clicked.connect(self.set_filepath)
        self.label = QLabel("Please enter the filepath to a study directory")
        self.label.setObjectName("enterfilepath")
        self.label2 = QLabel("")
        self.label2.setObjectName("error")
        self.input = QLineEdit('')
        self.input.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0) # get rid of ugly mac focus rect
        self.input.setPlaceholderText('file path')
        self.input.setMaxLength(100)
        self.input.editingFinished.connect(self.set_filepath)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label2)
        self.inner = QHBoxLayout()
        self.inner.addWidget(self.input)
        self.inner.addWidget(self.button2)
        self.layout.addLayout(self.inner)
        self.setLayout(self.layout)

    def set_filepath(self):
        self.filepath = self.input.text()
        self.check_and_set_filepath()

    def check_and_set_filepath(self):
        if os.path.exists(self.filepath):
            self.window.study = self.filepath
            self.window.reset_after_changes()
            print("this ist the study path: " + self.window.study)
            self.label2.setText("")
        else:
            self.label2.setText("This is not a valid file path")


# Animation/Video
class MediaBar(QWidget):
    refresh = 1  # in fps

    def __init__(self, window):
        QWidget.__init__(self)
        self.setObjectName("MediaBar")
        self.window = window
        self.timer = QTimer()
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
            self.timer.stop()
            print('start')
        else:
            self.window.running = True
            self.playbtn.setStyleSheet("image: url('pauseButton.png') ;")
            self.timer.start(self.refresh)
            self.timer.timeout.connect(self.forward_button)
            print('stop')


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
        self.setLayout(self.BoxLayout)


Window = MainWindow()
Window.show()
sys.exit(app.exec())
