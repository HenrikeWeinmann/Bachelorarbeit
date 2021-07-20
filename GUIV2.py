import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap
from matplotlib.backend_bases import MouseButton
import matplotlib.patches as patches
import pydicom as dcm
import math
from scipy.spatial import distance


class MainWindow (QMainWindow):
    validDataset = False  # /Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/
    current = 0  # current frame starting with 0
    running = False
    slice = 0  # slice the user currently sees starting at 1
    selection = []
    selectionMode = ''

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1300, 1000)
        self.setFixedWidth(1300)
        self.setFixedHeight(1000)
        self.centralWidget = QWidget()
        self.dataArray = []

        self.dicom = Dicom(self)
        self.addToolBar(self.toolbar())

        self.menu = self.toolbar()
        self.picturemenu = self.picturemenu()
        self.picturemenu.setFixedWidth(self.centralWidget.width())

        self.background = QStackedWidget()
        self.background.setObjectName("MediaBarBackground")
        self.play = MediaBar(self)
        self.background.addWidget(self.play)
        self.dock = QDockWidget("Data", self)
        self.dock.setWidget(self.rightSide())
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.dicom)
        if self.validDataset:
            self.mainLayout.insertWidget(0, self.picturemenu)
            self.mainLayout.addWidget(self.background)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.centralWidget.setLayout(self.mainLayout)
        self.centralWidget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setCentralWidget(self.centralWidget)

    def picturemenu(self):
        picturemenu = QWidget()
        picturemenu.setObjectName("picturemenu")
        layout = QHBoxLayout()
        self.eraseMode = QPushButton()
        self.eraseMode.setObjectName("eraseMode")
        self.eraseMode.setCheckable(True)
        self.eraseMode.clicked.connect(lambda: Dicom.erase(self.dicom, self))
        self.eraseMode.setToolTip("Click near a Point to erase it")
        self.moveMode = QPushButton()
        self.moveMode.setObjectName("moveMode")
        self.moveMode.setCheckable(True)
        self.moveMode.clicked.connect(lambda: Dicom.move(self.dicom, self))
        self.moveMode.setToolTip("Click near a Point to move it")
        self.dontShow = QPushButton()
        self.dontShow.setObjectName("DS")
        self.dontShow.setCheckable(True)
        self.dontShow.clicked.connect(lambda: Dicom.hide(self.dicom, self))
        clear = QPushButton()
        clear.setObjectName("clear")
        clear.clicked.connect(lambda: Dicom.clear(self.dicom, self))
        self.contrast = QSlider(Qt.Horizontal)
        self.contrast.sliderMoved.connect(lambda: Dicom.change_contrast(self.dicom, self.contrast.value(), self))
        self.contrast.setValue(255)
        self.contrast.setMaximum(500)
        self.contrast.setMinimum(1)
        layout.addWidget(self.contrast)
        layout.addWidget(self.eraseMode)
        layout.addWidget(self.moveMode)
        layout.addWidget(self.dontShow)
        layout.addWidget(clear)
        picturemenu.setLayout(layout)
        return picturemenu

    def toolbar(self):
        toolbar = QToolBar()
        toolbar.setObjectName("Toolbar")
        selectionMode = QComboBox()
        selectionMode.addItem("Single Point Selection")
        selectionMode.addItem("Multiple Point Selection")
        selectionMode.addItem("Polygon Selection")
        #selectionMode.addItem("Freehand Selection")  # to be implemented in the future
        selectionMode.activated.connect(lambda: Dicom.setSelectionMode(self.dicom, selectionMode.currentText(), self))
        self.selectionMode = selectionMode.currentText()
        imageMode = QComboBox()
        imageMode.addItem('bone')
        imageMode.addItem('gist_gray')
        imageMode.addItem('binary')
        imageMode.activated.connect(lambda: Dicom.changecmap(self.dicom, imageMode.currentText(), self))
        showData = QPushButton("Show/Hide Data")
        showData.setObjectName("ShowData")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setObjectName("spacer")
        showData.clicked.connect(self.showRightSide)
        toolbar.addWidget(selectionMode)
        toolbar.addWidget(imageMode)
        toolbar.addWidget(spacer)
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

    # reset the current slice and frame we are on
    def reset_after_changes(self):
        if not self.validDataset:
            self.dicom.initCanvas()
        self.update_fig()
        self.data.info = Data.information(self.data)
        self.dock.setWidget(self.rightSide())

    def update_fig(self):
        plt.clf()
        self.dicom.imgarr = self.dataArray[self.slice][self.current].pixel_array
        self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap, vmin=self.dicom.vmin, vmax=self.dicom.vmax)
        self.cnv = plt.imshow(self.dicom.canvas, Dicom.customcmap(self.dicom))
        if self.selectionMode == 'Polygon Selection' and len(self.selection) >= 3:
            Dicom.draw_polygon(self.dicom, patches.Polygon(self.selection, color='red', alpha=0.2))
            '''used to be: plt.gca().add_patch(polygon)... but somehow wont work anymore'''
        self.dicom.draw()
        self.mainLayout.insertWidget(1, self.dicom)


class Dicom (FigureCanvas):
    pressed = False
    pos = []
    def __init__(self, window):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        super().__init__(self.fig)
        self.setParent(window)
        self.cmap = 'bone'
        self.vmin = 0
        self.vmax = 255
        try:
            self.initCanvas()
        except:
            self.img = self.ax.imshow(plt.imread("Default.jpg"))
            plt.axis("off")

        plt.tight_layout()

    def initCanvas(self):
        window = self.parent().parent()
        self.imgarr = window.dataArray[window.slice][window.current].pixel_array
        self.img = self.ax.imshow(self.imgarr, self.cmap)
        self.canvas = np.empty(self.imgarr.shape)
        self.canvas[:] = 0
        self.cnv = self.ax.imshow(self.canvas, cmap=self.customcmap())
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.selection)
        self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.release)
        self.cid3 = self.fig.canvas.mpl_connect('motion_notify_event', self.set_contrast)
        self.patch = patches.Circle([1, 1], 2)

    # scroll wheel
    def wheelEvent(self, event):
        window = self.parent().parent()
        change = event.angleDelta().y()/120
        if window.validDataset:
            if change > 0:
                if window.slice < (len(window.dataArray) - 1):
                    window.slice += 1
                    window.reset_after_changes()
            elif window.slice > 1:
                    window.slice -= 1
                    window.reset_after_changes()

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
        if event.dblclick:
            self.zoom(1.5, event)
        self.pressed = True
        self.pos = [int(event.xdata), int(event.ydata)]
        if event.button == MouseButton.LEFT:
            window = self.parent().parent()
            x = event.xdata
            y = event.ydata
            if window.selectionMode == 'Single Point Selection':
                if x and y > 0:
                    window.dicom.canvas[:] = 0
                    window.dicom.canvas[int(y), int(x)] = 255
                    window.selection = [self.pos]
                    window.reset_after_changes()
            elif window.selectionMode == 'Multiple Point Selection':
                if x and y > 0:
                    window.dicom.canvas[int(y), int(x)] = 255
                    window.selection.append(self.pos)
                    window.reset_after_changes()
            elif window.selectionMode == 'Polygon Selection':
                if x and y > 0:
                    window.dicom.canvas[int(y), int(x)] = 255
                    window.selection.append(self.pos)
                    self.sortSelection(window.selection)
                    window.reset_after_changes()

    def draw_polygon(self, polygon):
        plt.gca().add_patch(polygon)

    def sortSelection(self, selection):
        cent = (sum([p[0] for p in selection]) / len(selection), sum([p[1] for p in selection]) / len(selection))
        selection.sort(key=lambda p: math.atan2(p[1] - cent[1], p[0] - cent[0]))

    def setSelectionMode(self, selectionMode, window):
        print(selectionMode)
        window.selectionMode = selectionMode

    def set_contrast(self, event):
        window = self.parent().parent()
        if self.pressed and event.button == MouseButton.RIGHT:
            diff = int(self.pos[1] - event.ydata)
            value = window.contrast.value() + diff

            self.change_contrast(value, window)

    def change_contrast(self, value, window):
        self.vmax = value
        window.update_fig()

    #on mouse release
    def release(self, event):
        self.pressed = False
        self.pos = []
        window = self.parent().parent()
        window.contrast.setValue(self.vmax)

    #reconnect the standard on click actions
    def reconnect_cids(self, window):
        self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.erasePoint)
        self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
        self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.movePoint)

    def clear(self, window):
        self.canvas[:] = 0
        window.selection = []
        window.reset_after_changes()

    def erase(self, window):
        if window.moveMode.isChecked():
            window.moveMode.toggle()
            window.moveMode.setStyleSheet("background-color : #D8EAF3")
            self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
            self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.release)
        if window.eraseMode.isChecked():
            window.eraseMode.setStyleSheet("background-color : #B2D6E6")
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.erase_and_redraw)
        else:
            window.eraseMode.setStyleSheet("background-color : #D8EAF3")
            self.reconnect_cids(window)

    def erasePoint(self, event):
        print("erasing")
        window = self.parent().parent()
        x = event.xdata
        y = event.ydata
        point = [int(x), int(y)]
        closest_index = distance.cdist([point], window.selection).argmin()
        self.canvas[window.selection[closest_index]] = 0
        window.selection.pop(closest_index)


    def erase_and_redraw(self, event):
        window = self.parent().parent()
        self.erasePoint(event)
        print(window.selection)
        window.reset_after_changes()

    def zoom(self, value, event):  # to implement in the future
        x, y = event.xdata, event.ydata
        self.ax.set_xlim(x - 0.1, x + 0.1)
        self.ax.set_ylim(y - 0.1, y + 0.1)
        self.draw()
        print("zoom")

    def move(self, window):
        if window.eraseMode.isChecked():
            window.eraseMode.toggle()
            window.eraseMode.setStyleSheet("background-color : #D8EAF3")
        if window.moveMode.isChecked():
            window.moveMode.setStyleSheet("background-color : #B2D6E6")
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.erasePoint)
            self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
            self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.movePoint)
        else:
            window.moveMode.setStyleSheet("background-color : #D8EAF3")
            self.reconnect_cids(window)

    def movePoint(self, event):
        window = self.parent().parent()
        self.selection(event)
        self.pressed = False
        self.pos = []
        window.reset_after_changes()

    def hide(self, window):
        if window.dontShow.isChecked():
            window.dontShow.setStyleSheet("background-color : #B2D6E6;")
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            print("hide")
            print(self.cnv)
            self.cnv.set_visible(False)
            window.update_fig()
        else:
            window.dontShow.setStyleSheet("background-color : #D8EAF3;")
            self.reconnect_cids(window)

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
            print("this ist the study path: " + self.filepath)
            self.window.dataArray = self.loadData()
            self.window.reset_after_changes()
            self.errorText.setText("")
            if not self.window.validDataset:
                self.window.validDataset = True
                self.window.mainLayout.addWidget(self.window.background)
                self.window.mainLayout.insertWidget(0, self.window.picturemenu)
        else:
            self.errorText.setText("This is not a valid file path")

    def open(self):
        file_name = QFileDialog.getExistingDirectory(self, 'Open Source Folder', os.getcwd())
        self.filepath = file_name
        self.check_and_set_filepath()

    def loadData(self):
        slices = os.listdir(self.filepath)  # list of all names of all slices
        slices.sort()
        data = []

        if os.path.isdir(os.path.join(self.filepath, slices[1])):
            for i in range(1, len(slices)):
                current_slice = os.path.join(self.filepath, slices[i])
                frames = os.listdir(current_slice)
                frames.sort()
                data.append([])
                for j in range(len(frames)):
                    current_frame = os.path.join(current_slice, frames[j])
                    dicom = dcm.dcmread(current_frame)
                    data[i - 1].append(dicom)

        elif not os.path.isdir(os.path.join(self.filepath, slices[1])):
            data.append([])
            for i in range(len(slices)):
                current_slice = os.path.join(self.filepath, slices[i])
                dicom = dcm.dcmread(current_slice)
                data[0].append(dicom)
                print(data)

        return data


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
            self.window.reset_after_changes()
        else:
            pass

    def forward(self):
        if self.window.current < len(self.window.dataArray[self.window.slice])-1:
            self.window.current += 1
        else:
            self.window.current = 0
        self.window.reset_after_changes()

    def backward(self):
        if self.window.current > 0:
            self.window.current -= 1
        else:
            self.window.current = len(self.window.dataArray[self.window.slice])-1
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

if __name__== '__main__':
    app = QApplication(sys.argv)
    qss = "Stylesheet.qss"

    with open(qss, "r") as fh:
        app.setStyleSheet(fh.read())

    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())

