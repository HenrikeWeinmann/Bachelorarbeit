import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from Application.UserInput import UserInput
from Application.DicomViewer import Dicom
from Application.Animation import MediaBar
from Application.Data import Data
from Application.Meta import Meta
from Application.Help import Help

class MainWindow (QMainWindow):
    validDataset = False  # /Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/
    single_image = False
    current = 0  # current frame starting with 0
    running = False
    slice = 0  # slice the user currently sees starting at 1
    selection = []
    selectionMode = ''
    AIdisplayed = False

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(100, 100, 1300, 900)
        self.setWindowTitle("Dicom Viewer")
        self.centralWidget = QFrame()
        self.centralWidget.setFrameStyle(QFrame.StyledPanel)
        self.centralWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.dataArray = []
        self.aiArray = []
        self.toolbar = self.toolbar()
        self.dicom = Dicom(self)
        self.dicom.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addToolBar(self.toolbar)

        self.background = QStackedWidget()
        self.background.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        self.background.setObjectName("MediaBarBackground")
        self.background.addWidget(MediaBar(self))

        self.mediaBar = QHBoxLayout()
        self.mediaBar.addWidget(self.background)

        self.picturemenu = self.picture_menu()
        self.picturemenu.setObjectName("picturemenu")

        self.dock = QDockWidget("", self)
        self.dock.setWidget(self.rightSide())
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.input = UserInput(self)
        self.input.setObjectName("userInput")
        self.uI = QDockWidget("Input", self)
        self.uI.setWidget(self.input)
        self.uI.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.meta = Meta(self)
        self.meta.setObjectName("meta")
        self.meta.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.help = Help(self)
        self.help.setObjectName("meta")
        self.help.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.meta)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.uI)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.help)

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.dicom, 0, 1, 1, 1)
        if self.validDataset:
            self.mainLayout.addWidget(self.picturemenu, 0, 0, 2, 1, Qt.AlignmentFlag.AlignLeft)
            #self.mainLayout.addLayout(self.mediaBar, 1, 1, 1, 1)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

#this menu handles everything concerning the selection and labeling function
    def picture_menu(self):
        picturemenu = QFrame()
        picturemenu.setFrameStyle(QFrame.Box)
        outerlayout = QVBoxLayout()
        outerlayout.setContentsMargins(0, 0, 0, 0)
        contrastlayout = QHBoxLayout()
        layout = QGridLayout()
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
        self.contrast.setValue(30)
        self.contrast.setMaximum(100)
        self.contrast.setMinimum(10)
        self.con = QPixmap("Application/Icons/contrast.png")
        self.label = QLabel()
        self.label.setPixmap(self.con.scaled(30, 30))
        self.label.setObjectName("contrast")
        self.con_max = QPixmap("Application/Icons/contrast_max.png")
        self.label2 = QLabel()
        self.label2.setPixmap(self.con_max.scaled(30, 30))
        self.label2.setObjectName("contrast_max")

        imageMode = QComboBox()
        imageMode.addItem('bone')
        imageMode.addItem('gist_gray')
        imageMode.addItem('binary')
        imageMode.activated.connect(lambda: Dicom.changecmap(self.dicom, imageMode.currentText(), self))
        imageMode.setView(QListView())

        selectionBox = QComboBox()
        selectionBox.addItem("Single Point Selection")
        selectionBox.addItem("Multiple Point Selection")
        selectionBox.addItem("Polygon Selection")
        selectionBox.setView(QListView())
        # selectionMode.addItem("Freehand Selection")  # to be implemented in the future
        selectionBox.activated.connect(lambda: Dicom.setSelectionMode(self.dicom, selectionBox, self))
        self.selectionMode = selectionBox.currentText()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setObjectName("spacer")
        line1 = QWidget()
        line1.setObjectName("line1")
        line2 = QWidget()
        line2.setObjectName("line2")
        line3 = QWidget()
        line3.setObjectName("line3")
        analyze = QPushButton("Analyze")
        analyze.setObjectName("Analyze")
        analyze.clicked.connect(self.analyze)
        # layout
        contrastlayout.addWidget(self.label)
        contrastlayout.addWidget(self.contrast)
        contrastlayout.addWidget(self.label2)
        layout.addWidget(self.saveImage, 0, 0)
        layout.addWidget(self.eraseMode, 0, 1)
        layout.addWidget(self.moveMode, 1, 0)
        layout.addWidget(self.dontShow, 1, 1)
        layout.addWidget(clear, 2, 0)
        outerlayout.addWidget(selectionBox)
        outerlayout.addWidget(imageMode)
        outerlayout.addLayout(contrastlayout)
        outerlayout.addWidget(line1)
        outerlayout.addLayout(layout)
        outerlayout.addWidget(line2)
        outerlayout.addLayout(self.mediaBar)
        outerlayout.addWidget(line3)
        outerlayout.addWidget(analyze)
        outerlayout.addWidget(spacer)
        picturemenu.setLayout(outerlayout)

        return picturemenu

#main toolbar with all major settings
    def toolbar(self):
        toolbar = QToolBar()
        toolbar.setFixedHeight(50)
        toolbar.setObjectName("Toolbar")
        showData = QPushButton("Information")
        showData.setObjectName("ShowData")
        showData.setCheckable(True)
        showData.setChecked(True)
        showData.clicked.connect(lambda: self.showDockwidget(self.dock))
        File = QPushButton("Open File")
        File.setObjectName("File")
        File.clicked.connect(lambda: self.showDockwidget(self.uI))
        File.setCheckable(True)
        File.setChecked(True)
        Help = QPushButton("Help")
        Help.setObjectName("Help")
        Help.setCheckable(True)
        Help.clicked.connect(lambda: self.showDockwidget(self.help))
        MetaData = QPushButton("Meta Data")
        MetaData.setObjectName("MetaData")
        MetaData.setCheckable(True)
        MetaData.setChecked(False)
        MetaData.clicked.connect(lambda: self.showDockwidget(self.meta))
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setObjectName("spacer")

        toolbar.addWidget(File)
        toolbar.addWidget(MetaData)
        toolbar.addWidget(spacer)
        toolbar.addWidget(showData)
        toolbar.addWidget(Help)
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
            self.dock.setWindowTitle("Data")
        else:
            self.RSlayout.addWidget(self.welcome)
            self.dock.setWindowTitle("Welcome")

        self.RSlayout.addStretch()
        rightSide.setLayout(self.RSlayout)

        return rightSide

    def showDockwidget(self, widget):
        if widget.isVisible():
            widget.setVisible(False)
            if self.isFullScreen():
                self.setGeometry(0,0, self.width(),self.height())
            else:
                self.setGeometry(100, 100, self.width(), self.height()-widget.height())
        else:
            widget.setVisible(True)

    # reset the current slice and frame we are on
    def reset_after_changes(self):
        if not self.validDataset:
            self.dicom.initCanvas()
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.update_fig()
        self.data.info = Data.information(self.data)
        self.dock.setWidget(self.rightSide())
        self.meta.setWidget(Meta.readMetadata(self.meta))


    #update the matplotlib canvas with the current data stored in the DICOM object
    def update_fig(self):
        plt.clf()
        self.init_imgarrays()
        plt.xlim(self.dicom.xlim)
        plt.ylim(self.dicom.ylim)
        self.dicom.draw()
        self.mainLayout.addWidget(self.dicom, 0, 1)

    def init_imgarrays(self):
        if isinstance(self.dataArray[self.slice][self.current], np.ndarray):
            self.dicom.imgarr = self.dataArray[self.slice][self.current]
            self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap, vmin=0, vmax=1)
        else:
            self.dicom.imgarr = self.dataArray[self.slice][self.current].pixel_array
            self.dicom.img = plt.imshow(self.dicom.imgarr, self.dicom.cmap, vmin=self.dicom.vmin, vmax=self.dicom.vmax)
        self.cnv = plt.imshow(self.dicom.canvas, Dicom.customcmap(self.dicom))
        if self.selectionMode == 'Polygon Selection' and len(self.selection) >= 3:
            Dicom.draw_polygon(self.dicom, patches.Polygon(self.selection, color='red', alpha=0.2))
            '''used to be: plt.gca().add_patch(polygon)... but somehow wont work anymore'''
        if self.AIdisplayed:
            self.aicanvas = plt.imshow(self.aiArray[self.current], alpha=0.5)

        return self.dicom.imgarr

    '''
    update fig will add the image to the display as an overlay
    at the moment it runs out of bounds as it will always display the current slices calculation
    and everything is hard coded
    '''
    def analyze(self):
        print("please write code here (line 230)")
        self.AIdisplayed = True
        self.aiArray = UserInput.load_calculations(self.uI)
        self.update_fig()


if __name__=='__main__':
    app = QApplication(sys.argv)
    qss = "Application/Stylesheet.qss"

    with open(qss, "r") as fh:
        app.setStyleSheet(fh.read())

    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())

