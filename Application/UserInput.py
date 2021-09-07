import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import*
import os
import pydicom as dcm
import numpy as np

# --------------------- User Input---------------------------------------------------------------------------------
'''
This class manages the process of opening and loading files into the app 
It creates an User Input Widget which always needs the window attribute in order to call some methods
'''
class UserInput(QFrame):
    filepath = ''  #option to hard code a file path

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setObjectName("UserInput")
        self.submitbtn = QPushButton('')
        self.submitbtn.setObjectName("submit")
        self.submitbtn.clicked.connect(self.set_filepath)
        self.openbtn = QPushButton('Open a CINE set from the file manager:             ')
        self.openbtn.setIcon(QIcon(QPixmap("Application/Icons/open.png")))
        self.openbtn.setIconSize(QSize(50,50))
        self.openbtn.setObjectName("Open")
        self.openbtn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.openbtn.clicked.connect(self.open)
        self.label = QLabel("Please enter the filepath to a study directory: ")
        self.label.setObjectName("enterfilepath")
        self.errorText = QLabel("This is not a valid file path")
        self.errorText.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.errorText.setObjectName("error")
        self.input = QLineEdit('')
        self.input.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, 0)  # get rid of ugly mac focus rect
        self.input.setPlaceholderText('file path')
        self.input.setMaxLength(150)
        self.input.editingFinished.connect(self.set_filepath)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.inner = QHBoxLayout()
        self.inner.addWidget(self.input)
        self.inner.addWidget(self.submitbtn)
        self.inner2 = QHBoxLayout()
        self.inner2.addWidget(self.openbtn)
        self.layout.addLayout(self.inner)
        self.layout.addLayout(self.inner2)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def set_filepath(self):
        self.filepath = self.input.text()
        self.check_and_set_filepath()

    '''
    this is the main method that starts the whole process of checking for the right data to display 
    and calling all necessary methods
    '''

    def check_and_set_filepath(self):
        if os.path.exists(self.filepath):
            if self.check_file(self.filepath):
                self.window.dataArray = self.loadData()
                self.layout.removeWidget(self.errorText)
                self.errorText.setText("")
                self.errorText.setFixedHeight(0)
                self.window.reset_after_changes()
                if not self.window.validDataset:
                    self.window.validDataset = True
                    if not self.window.single_image:
                        self.window.mainLayout.addLayout(self.window.mediaBar, 1, 1, 1, 1)
                    self.window.mainLayout.addWidget(self.window.picturemenu, 0, 0, 2, 1, Qt.AlignmentFlag.AlignLeft)
            else:
                self.layout.insertWidget(1, self.errorText)
        else:
            self.layout.insertWidget(1, self.errorText)
            #self.errorText.setText("not a valid path")
    '''
    check for DICOM file suffix as well as the structure of nested directories with up to 3 layers
    '''
    def check_file(self, file):
        if os.path.isdir(file):
            slices = os.listdir(file)  # list of all names of all slices
            slices.sort()
            file = os.path.join(file, slices[1])
            if os.path.isdir(file):
                slices = os.listdir(file)  # list of all names of all slices
                slices.sort()
                file = os.path.join(file, slices[1])
                if os.path.isdir(file):
                    self.errorText.setText("you can only load one dataset at a time.")
                    self.layout.insertWidget(1, self.errorText)
                    return False
                elif file.lower().endswith(('.dcm', '.dc3', '.dic')):
                    return True
            elif file.lower().endswith(('.dcm', '.dc3', '.dic')):
                return True
        elif file.lower().endswith(('.dcm', '.dc3', '.dic')):
            return True
        else:
            self.layout.insertWidget(1, self.errorText)
            self.errorText.setText("you can only load dicom images")
            return False

    def open(self):
        file_name = QFileDialog.getExistingDirectory(self, 'Open Source Folder', os.getcwd())
        self.filepath = file_name
        self.check_and_set_filepath()

    '''
    load all pixel Data into an array called data[slice][frame]
    '''
    def loadData(self):
        data = []
        if not os.path.isdir(self.filepath):
            print("single picture")
            self.window.single_image = True
            data.append([])
            dicom = dcm.dcmread(self.filepath)
            data[0].append(dicom)
            return data
        else:
            slices = os.listdir(self.filepath)  # list of all names of all slices
            slices.sort()

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
            return data
    '''
    assuming that only one slice will be analyzed
    loading the np arrays from path
    '''
    def load_calculations(self):
        aiData = []
        dir = "Application/masks"
        for filename in os.listdir(dir):
            arr = np.load(os.path.join(dir, filename))
            arr = arr[:, :, 0]

            aiData.append(arr)
            if filename == "0_0_mask.npy":
                print(arr)
                print(aiData[0])
        return aiData

