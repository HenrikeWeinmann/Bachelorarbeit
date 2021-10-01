from PyQt5.QtWidgets import *
from PyQt5.QtCore import*

# ----------------Animation/Video---------------------------------------------------------------------------------
class MediaBar(QWidget):
    refresh = 100  # in fps

    def __init__(self, window):
        QWidget.__init__(self)
        self.setObjectName("MediaBar")
        self.window = window
        self.timer = QTimer()
        self.timer.setInterval(100)
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
        # layout
        self.layout = QHBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.Backwardbtn)
        # self.layout.addWidget(self.FBbtn)
        self.layout.addWidget(self.playbtn)
        self.layout.addWidget(self.stopbtn)
        # self.layout.addWidget(self.FFbtn)
        self.layout.addWidget(self.Forwardbtn)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def play(self):
        if self.window.running:
            self.window.running = False
            self.playbtn.setStyleSheet("image: url('Application/Icons/Play.png') ;")
            self.timer.stop()
            print('stop')
        else:
            self.window.running = True
            self.playbtn.setStyleSheet("image: url('Application/Icons/Pause.png') ;")
            self.timer.start(self.refresh)
            self.timer.timeout.connect(self.forward)
            print('start')

    def stop(self):
        if self.window.running:
            self.window.running = False
            self.playbtn.setStyleSheet("image: url('Application/Icons/Play.png') ;")
            self.timer.stop()
            self.window.current = 0
            self.window.reset_after_changes()
        else:
            pass

    def forward(self):
        if not self.window.aiArray == []:
            max = min(len(self.window.dataArray[self.window.slice])-1, len(self.window.aiArray)-1)
        else:
            max = len(self.window.dataArray[self.window.slice])-1

        if self.window.current < max:
            self.window.current += 1
            print(self.window.current)
        else:
            self.window.current = 0
        self.window.reset_after_changes()

    def backward(self):
        if not self.window.aiArray == []:
            max = min(len(self.window.dataArray[self.window.slice])-1, len(self.window.aiArray)-1)
        else:
            max = len(self.window.dataArray[self.window.slice])-1
        if self.window.current > 0:
            self.window.current -= 1
        else:
            self.window.current = max
        self.window.reset_after_changes()

# to be implemented
    def fastforward(self):
        pass

    def fastbackward(self):
        pass