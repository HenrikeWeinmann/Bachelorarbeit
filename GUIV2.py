import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
from qtwidgets import AnimatedToggle
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap
import matplotlib.patches as patches
import pydicom as dcm
import math
from scipy.spatial import distance


app = QApplication(sys.argv)
qss = "Stylesheet.qss"

with open(qss, "r") as fh:
    app.setStyleSheet(fh.read())


class MainWindow (QMainWindow):
    validDataset = False
    study = ""  # /Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/
    current = 0  # current frame starting with 0
    running = False
    slice = 1  # slice the user currently sees starting at 1
    # paths
    slices = None  # list of all names of all slices
    current_slice = None  # path of the current slice on users OS
    frames = None  # list of all names from all frames of the current slice
    current_frame = None  # path of the current frame on users OS
    selection = []
    selectionMode = ''

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1300, 1000)
        self.setMaximumWidth(1300)
        self.setMaximumHeight(1000)
        self.centralWidget = QWidget()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setSpacing(2)
        self.dicom = Dicom(self)
        self.addToolBar(self.toolbar())

        self.menu = self.toolbar()
        self.background = QStackedWidget()
        self.background.setObjectName("MediaBarBackground")
        self.play = MediaBar(self)
        self.background.addWidget(self.play)
        self.dock = QDockWidget("Data", self)
        self.dock.setWidget(self.rightSide())
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.mainLayout.addWidget(self.dicom)
        if self.validDataset:
            self.mainLayout.addWidget(self.background)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.centralWidget.setLayout(self.mainLayout)
        self.centralWidget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setCentralWidget(self.centralWidget)


# reset the current slice and frame we are on
    def reset_after_changes(self):
        self.initialize_paths()
        if not self.validDataset:
            self.dicom.initCanvas()
        self.update_fig()
        self.data.info = Data.information(self.data)
        self.dock.setWidget(self.rightSide())

    def initialize_paths(self):
        self.slices = os.listdir(self.study)  # list of all names of all slices
        self.slices.sort()
        self.current_slice = os.path.join(self.study, self.slices[self.slice])
        self.frames = os.listdir(self.current_slice)
        self.frames.sort()
        self.current_frame = os.path.join(self.current_slice, self.frames[self.current])

    def toolbar(self):
        toolbar = QToolBar()
        toolbar.setObjectName("Toolbar")
        selectionMode = QComboBox()
        selectionMode.addItem("Single Point Selection")
        selectionMode.addItem("Multiple Point Selection")
        selectionMode.addItem("Polygon Selection")
        selectionMode.addItem("Freehand Selection") # to be implemented in the future
        selectionMode.activated.connect(lambda: Dicom.setSelectionMode(self.dicom, selectionMode.currentText(), self))
        self.selectionMode = selectionMode.currentText()
        imageMode = QComboBox()
        imageMode.addItem('bone')
        imageMode.addItem('gist_gray')
        imageMode.addItem('copper')
        imageMode.activated.connect(lambda: Dicom.changecmap(self.dicom, imageMode.currentText(), self))
        label = QLabel("eraser mode:")
        label.setObjectName("EraseMode")
        label.setToolTip("Click near a Point to erase it")
        eraseMode = AnimatedToggle(checked_color="#8DC1D8", pulse_checked_color="#55808080")
        eraseMode.clicked.connect(lambda: Dicom.erase(self.dicom, eraseMode.checkState(), self))
        clear = QPushButton("clear")
        clear.setObjectName("clear")
        clear.clicked.connect(lambda: Dicom.clear(self.dicom, self))
        showData = QPushButton("Show/Hide Data")
        showData.setObjectName("ShowData")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setObjectName("spacer")
        showData.clicked.connect(self.showRightSide)
        toolbar.addWidget(selectionMode)
        toolbar.addWidget(imageMode)
        toolbar.addWidget(spacer)
        toolbar.addWidget(label)
        toolbar.addWidget(eraseMode)
        toolbar.addWidget(clear)
        toolbar.addWidget(showData)
        return toolbar

    def rightSide(self):
        rightSide = QWidget()
        rightSide.setObjectName("right")
        self.data = Data(self)
        self.data.setObjectName("data")
        self.userInput = UserInput(self)
        self.userInput.setObjectName("userInput")
        layout = QVBoxLayout()
        layout.addWidget(self.data)
        layout.addWidget(self.userInput)
        layout.addStretch()
        rightSide.setLayout(layout)

        return rightSide

    def showRightSide(self):
        if self.dock.isVisible():
            self.dock.setVisible(False)
        else:
            self.dock.setVisible(True)


    def update_fig(self):
        plt.clf()
        self.dicom.dcmfile = dcm.dcmread(self.current_frame)
        self.dicom.imgarr = self.dicom.dcmfile.pixel_array
        self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap)
        self.cnv = plt.imshow(self.dicom.canvas, Dicom.customcmap(self.dicom))
        if self.selectionMode == 'Polygon Selection' and len(self.selection) >= 3:
            plt.subplot().add_patch(self.dicom.patch)
        self.dicom.draw()
        self.mainLayout.insertWidget(0,self.dicom)


class Dicom (FigureCanvas):

    def __init__(self, window):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(window)
        self.cmap = 'bone'
        try:
            self.initCanvas()
        except:
            self.img = self.ax.imshow(plt.imread("Default.jpg"))

        plt.tight_layout()


    def initCanvas(self):
        window = self.parent().parent()
        self.dcmfile = dcm.dcmread(window.current_frame)
        self.imgarr = self.dcmfile.pixel_array
        self.img = self.ax.imshow(self.imgarr, self.cmap)
        self.canvas = np.empty(self.imgarr.shape)
        self.canvas[:] = 0
        self.cnv = self.ax.imshow(self.canvas, cmap=self.customcmap())
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.selection)
        self.patch = patches.Circle([1, 1], 2)

    # scroll wheel
    def wheelEvent(self, event):
        window = self.parent().parent()
        change = event.angleDelta().y()/120
        if window.validDataset:

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
        x = event.xdata
        y = event.ydata
        if window.selectionMode == 'Single Point Selection':
            if x and y > 0:
                point = [int(x), int(y)]
                window.dicom.canvas[:] = 0
                window.dicom.canvas[int(y), int(x)] = 255
                window.selection = [point]
                window.reset_after_changes()
        elif window.selectionMode == 'Multiple Point Selection':
            if x and y > 0:
                point = [int(x), int(y)]
                window.dicom.canvas[int(y), int(x)] = 255
                window.selection.append(point)
                window.reset_after_changes()
        elif window.selectionMode == 'Polygon Selection':
            if x and y > 0:
                point = [int(x), int(y)]
                window.dicom.canvas[int(y), int(x)] = 255
                window.selection.append(point)
                self.sortSelection(window.selection)
                if len(window.selection) >= 3:
                    polygon = patches.Polygon(window.selection, color='red', alpha=0.2)
                    window.dicom.patch = polygon
                window.reset_after_changes()
        else:
            pass

    def sortSelection(self, selection):
        cent = (sum([p[0] for p in selection]) / len(selection), sum([p[1] for p in selection]) / len(selection))
        selection.sort(key=lambda p: math.atan2(p[1] - cent[1], p[0] - cent[0]))

    def setSelectionMode(self, selectionMode, window):
        print(selectionMode)
        window.selectionMode = selectionMode

    def clear(self, window):
        self.canvas[:] = 0
        window.selection = []
        window.reset_after_changes()

    def erase(self, state, window):
        if state == 2:
            window.dicom.cid = window.dicom.fig.canvas.mpl_disconnect(window.dicom.cid)
            window.dicom.cid = window.dicom.fig.canvas.mpl_connect('button_press_event', self.erasePoint)
        else:
            window.dicom.cid = window.dicom.fig.canvas.mpl_disconnect(window.dicom.cid)
            window.dicom.cid = window.dicom.fig.canvas.mpl_connect('button_press_event', self.selection)
        pass

    def erasePoint(self, event):
        print("erasing")
        window = self.parent().parent()
        x = event.xdata
        y = event.ydata
        point = [int(x), int(y)]
        closest_index = distance.cdist([point], window.selection).argmin()
        window.dicom.canvas[window.selection[closest_index]] = 0
        window.selection.pop(closest_index)
        #recalculating Polygon
        if window.selectionMode == 'Polygon Selection':
            polygon = patches.Polygon(window.selection, color='red', alpha=0.2)
            window.dicom.patch = polygon
        window.reset_after_changes()

    def zoom(self):  # to implement in the future
        pass


# this class handles user Input
class UserInput(QWidget):
    filepath = ''  # IM-13020-0001.dcm

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setObjectName("UserInput")
        self.submitbtn = QPushButton('SUBMIT')
        self.submitbtn.setObjectName("submit")
        self.submitbtn.clicked.connect(self.set_filepath)
        self.openbtn = QPushButton('Open')
        self.openbtn.setObjectName("Open")
        self.openbtn.clicked.connect(self.open)
        self.label = QLabel("Please enter the filepath to a study directory: ")
        self.label.setObjectName("enterfilepath")
        self.label2 = QLabel("Open a study folder from the file manager: ")
        self.label2.setObjectName("label2")
        self.errorText = QLabel("")
        self.errorText.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.errorText.setObjectName("error")
        self.input = QLineEdit('')
        self.input.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)  # get rid of ugly mac focus rect
        self.input.setPlaceholderText('file path')
        self.input.setMaxLength(100)
        self.input.editingFinished.connect(self.set_filepath)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.errorText)
        self.inner = QHBoxLayout()
        self.inner.addWidget(self.input)
        self.inner.addWidget(self.submitbtn)
        self.inner2 = QHBoxLayout()
        self.inner2.addWidget(self.label2)
        self.inner2.addWidget(self.openbtn)
        self.layout.addLayout(self.inner)
        self.layout.addLayout(self.inner2)
        self.setLayout(self.layout)

    def set_filepath(self):
        self.filepath = self.input.text()
        self.check_and_set_filepath()

    def check_and_set_filepath(self):
        if os.path.exists(self.filepath):
            self.window.study = self.filepath
            self.window.reset_after_changes()
            if not self.window.validDataset:
                self.window.validDataset = True
                self.window.mainLayout.addWidget(self.window.background)
            print("this ist the study path: " + self.window.study)
            self.errorText.setText("")
        else:
            self.errorText.setText("This is not a valid file path")

    def open(self):
        file_name = QFileDialog.getExistingDirectory(self, 'Open Source Folder', os.getcwd())
        self.filepath = file_name
        self.check_and_set_filepath()


# Animation/Video
class MediaBar(QWidget):
    refresh = 1  # in fps

    def __init__(self, window):
        QWidget.__init__(self)
        self.setObjectName("MediaBar")
        self.window = window
        self.timer = QTimer()
        self.Backwardbtn = QPushButton('')
        self.Backwardbtn.setObjectName("backward")
        self.Backwardbtn.clicked.connect(self.backward)
        self.playbtn = QPushButton('')
        self.playbtn.setObjectName("playbtn")
        self.playbtn.clicked.connect(self.play)
        self.stopbtn = QPushButton('')
        self.stopbtn.setObjectName("stopbtn")
        self.stopbtn.clicked.connect(self.stop)
        self.Forwardbtn = QPushButton('')
        self.Forwardbtn.setObjectName("forward")
        self.Forwardbtn.clicked.connect(self.forward)
        self.FFbtn = QPushButton('')
        self.FFbtn.setObjectName("fastforward")
        self.FFbtn.clicked.connect(self.fastforward)
        self.FBbtn = QPushButton('')
        self.FBbtn.setObjectName("fastbackward")
        self.FBbtn.clicked.connect(self.fastbackward)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.Backwardbtn)
        self.layout.addWidget(self.FBbtn)
        self.layout.addWidget(self.playbtn)
        self.layout.addWidget(self.stopbtn)
        self.layout.addWidget(self.FFbtn)
        self.layout.addWidget(self.Forwardbtn)
        self.setLayout(self.layout)

    def play(self):
        if self.window.running:
            self.window.running = False
            self.playbtn.setStyleSheet("image: url('Icons/Play.png') ;")
            self.timer.stop()
            print('start')
        else:
            self.window.running = True
            self.playbtn.setStyleSheet("image: url('Icons/Pause.png') ;")
            self.timer.start(self.refresh)
            self.timer.timeout.connect(self.forward)
            print('stop')

    def stop(self):
        if self.window.running:
            self.window.running = False
            self.playbtn.setStyleSheet("image: url('Icons/Play.png') ;")
            self.timer.stop()
            self.window.current = 0
            self.window.current_frame = os.path.join(self.window.current_slice, self.window.frames[self.window.current])
            self.window.reset_after_changes()
        else:
            pass

    def forward(self):
        if self.window.current < 29:
            self.window.current += 1
        else:
            self.window.current = 0
        self.window.current_frame = os.path.join(self.window.current_slice, self.window.frames[self.window.current])
        self.window.reset_after_changes()

    def backward(self):
        if self.window.current > 0:
            self.window.current -= 1
        else:
            self.window.current = 29
        self.window.current_frame = os.path.join(self.window.current_slice, self.window.frames[self.window.current])
        self.window.reset_after_changes()

# to be implemented
    def fastforward(self):
        pass

    def fastbackward(self):
        pass


# this class creates a widget that contains all necessary data about the current slice
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
            self.table.setItem(0, 1, QTableWidgetItem(self.window.slices[self.window.slice]))
            self.table.setItem(1, 1, QTableWidgetItem(self.window.frames[self.window.current]))
            self.table.setItem(2, 1, QTableWidgetItem(str(self.window.selection)))

            self.table.horizontalHeader().hide()
            self.table.verticalHeader().hide()
            self.table.setMaximumWidth(500)
            self.table.setShowGrid(False)
            self.table.resizeColumnsToContents()
            if self.window.selectionMode == 'Multiple Point Selection' or 'Polygon Selection':
                self.table.setItem(2, 0, QTableWidgetItem("The selected Points are : "))
                if len(self.window.selection) > 2:
                    self.table.setColumnWidth(1, 200)

        return self.table


Window = MainWindow()
Window.show()
sys.exit(app.exec())
