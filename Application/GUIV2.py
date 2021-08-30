import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from Application.UserInput import UserInput
from Application.DicomViewer import Dicom
from Application.Animation import MediaBar
from Application.Data import Data


class MainWindow (QMainWindow):
    validDataset = False  # /Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/
    single_image = False
    current = 0  # current frame starting with 0
    running = False
    slice = 0  # slice the user currently sees starting at 1
    selection = []
    selectionMode = ''

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(200, 300, 1300, 1000)
        self.setFixedWidth(1300)
        self.setFixedHeight(900)
        self.centralWidget = QFrame()
        self.centralWidget.setFrameStyle(QFrame.StyledPanel)
        self.dataArray = []
        self.menu = self.toolbar()
        self.dicom = Dicom(self)
        self.dicom.setObjectName("dicom")
        self.addToolBar(self.toolbar())

        self.picturemenu = self.selection_menu()
        self.picturemenu.setMaximumWidth(self.centralWidget.width())

        self.background = QStackedWidget()
        self.background.setObjectName("MediaBarBackground")
        self.background.addWidget(MediaBar(self))

        self.mediaBar = QHBoxLayout()
        self.mediaBar.addWidget(self.background)

        self.dock = QDockWidget("Data", self)
        self.dock.setWidget(self.rightSide())
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        self.input = UserInput(self)
        self.input.setObjectName("userInput")
        self.uI = QDockWidget("Input", self)
        self.uI.setWidget(self.input)
        self.uI.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.uI)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.dicom)
        if self.validDataset:
            self.mainLayout.insertWidget(0, self.picturemenu)
            self.mainLayout.addLayout(self.mediaBar)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.setAlignment(self.background, Qt.AlignmentFlag.AlignHCenter)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

#this menu handles everything concerning the selection and labeling function
    def selection_menu(self):
        picturemenu = QWidget()
        picturemenu.setObjectName("picturemenu")
        layout = QHBoxLayout()
        self.saveImage = QPushButton()
        self.saveImage.setObjectName("saveImage")
        self.saveImage.clicked.connect(lambda: Dicom.save(self.dicom))
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
        self.con = QPixmap("Application/Icons/contrast.png")
        self.label = QLabel()
        self.label.setPixmap(self.con.scaled(30, 30))
        self.label.setObjectName("contrast")
        self.con_max = QPixmap("Application/Icons/contrast_max.png")
        self.label2 = QLabel()
        self.label2.setPixmap(self.con_max.scaled(30, 30))
        self.label2.setObjectName("contrast_max")
        layout.addWidget(self.label)
        layout.addWidget(self.contrast)
        layout.addWidget(self.label2)
        layout.addWidget(self.saveImage)
        layout.addWidget(self.eraseMode)
        layout.addWidget(self.moveMode)
        layout.addWidget(self.dontShow)
        layout.addWidget(clear)
        picturemenu.setLayout(layout)
        return picturemenu

#main toolbar with all major settings
    def toolbar(self):
        toolbar = QToolBar()
        toolbar.setFixedHeight(50)
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

    def rightSide(self):  # exists only for styling purposes and displays welcome text when no data set is loaded
        rightSide = QWidget()
        rightSide.setObjectName("right")
        self.data = Data(self)
        self.data.setObjectName("data")
        with open('Application/welcome.txt', 'r') as file:
            text = file.read()
        self.welcome = QTextEdit()
        self.welcome.setReadOnly(True)
        self.welcome.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.welcome.setHtml(text)
        self.welcome.adjustSize()
        self.RSlayout = QVBoxLayout()
        if self.validDataset:
            self.RSlayout.addWidget(self.data)
        else:
            self.RSlayout.addWidget(self.welcome)
        self.RSlayout.addStretch()
        rightSide.setLayout(self.RSlayout)

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
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.update_fig()
        self.data.info = Data.information(self.data)
        self.dock.setWidget(self.rightSide())

    #update the matplotlib canvas with the current data stored in the DICOM object
    def update_fig(self):
        plt.clf()
        self.dicom.imgarr = self.dataArray[self.slice][self.current].pixel_array
        self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap, vmin=self.dicom.vmin, vmax=self.dicom.vmax)
        self.cnv = plt.imshow(self.dicom.canvas, Dicom.customcmap(self.dicom))
        if self.selectionMode == 'Polygon Selection' and len(self.selection) >= 3:
            Dicom.draw_polygon(self.dicom, patches.Polygon(self.selection, color='red', alpha=0.2))
            '''used to be: plt.gca().add_patch(polygon)... but somehow wont work anymore'''
        self.dicom.xlim = [0, self.dicom.imgarr.shape[1]-1]
        self.dicom.ylim = [self.dicom.imgarr.shape[0]-1, 0]
        plt.xlim(self.dicom.xlim)
        plt.ylim(self.dicom.ylim)
        self.dicom.draw()
        self.mainLayout.insertWidget(1, self.dicom)


if __name__== '__main__':
    app = QApplication(sys.argv)
    qss = "Application/Stylesheet.qss"

    with open(qss, "r") as fh:
        app.setStyleSheet(fh.read())

    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())

