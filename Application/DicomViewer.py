
from PyQt5.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap
from matplotlib.backend_bases import MouseButton
import matplotlib.patches as patches
import math
from scipy.spatial import distance

#----------------------Image viewer---------------------------------------------------------------------------------

class Dicom (FigureCanvas):
    pressed = False
    pos = []

    def __init__(self, window):
        self.dpi = 100
        self.fig = plt.figure(figsize=(700 / self.dpi, 900 / self.dpi), dpi=self.dpi, facecolor="#808080")
        self.ax = self.fig.add_subplot(1, 1, 1)
        super().__init__(self.fig)
        window.centralWidget.setFixedWidth(700)
        window.centralWidget.setFixedHeight(900 - window.menu.height())
        self.setParent(window)
        self.cmap = 'bone'
        self.vmin = 0
        self.vmax = 255
        try:
            self.initCanvas()
        except:
            self.img = self.ax.imshow(plt.imread("Application/Default.jpg"), aspect='auto')
            self.fig.subplots_adjust(bottom=0, top=1, left=0, right=1)
            plt.axis("off")



    def initCanvas(self):
        window = self.parent().parent()
        self.imgarr = window.dataArray[window.slice][window.current].pixel_array
        #  print(window.dataArray[window.slice][window.current])  #print meta data
        self.img = self.ax.imshow(self.imgarr, self.cmap)
        self.canvas = np.empty(self.imgarr.shape)
        self.canvas[:] = 0
        self.cnv = self.ax.imshow(self.canvas, cmap=self.customcmap())
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.selection)
        self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.release)
        self.cid3 = self.fig.canvas.mpl_connect('motion_notify_event', self.set_contrast)
        self.patch = patches.Circle([1, 1], 2)
        self.xlim = [0, self.imgarr.shape[1]-1]
        self.ylim = [self.imgarr.shape[0]-1, 0]
        plt.xlim(self.xlim)
        plt.ylim(self.ylim)
        plt.tight_layout(pad=3)
        plt.tight_layout(pad=3)  # some bug in matplotlib version so it needs to be called twice
        window.update_fig()
        #  print(self.fig.get_size_inches() * self.fig.dpi)

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
        cmap = plt.cm.Reds
        my_cmap = cmap(np.arange(cmap.N))
        # Set alpha
        my_cmap[:, -1] = np.linspace(0, 1, cmap.N)
        # Create new colormap
        my_cmap = ListedColormap(my_cmap)
        return my_cmap

    def selection(self, event):
        if event.dblclick:
            self.zoom(event)
        else:
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
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.selection)
        self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
        self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.release)

    '''
    picture menu methods
    '''
    def clear(self, window):
        self.canvas[:] = 0
        window.selection = []
        self.xlim = [0, self.imgarr.shape[1]]
        self.ylim = [self.imgarr.shape[0], 0]
        window.reset_after_changes()

    def erase(self, window):
        if window.moveMode.isChecked():
            window.moveMode.toggle()
            self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
            self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.release)
        if window.eraseMode.isChecked():
            window.eraseMode.setStyleSheet("image: url('Application/Icons/erase_clicked.png') ;")
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.erase_and_redraw)
        else:
            self.reconnect_cids(window)
            window.eraseMode.setStyleSheet("image: url('Application/Icons/erase.png') ;")

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

    def zoom(self, event):  # to implement in the future
        window = self.parent().parent()
        x, y = event.xdata, event.ydata
        # calculate the new ax limits
        xlength = ((abs(self.xlim[0] - self.xlim[1]) * 0.8) / 2)
        ylength = ((abs(self.ylim[0] - self.ylim[1]) * 0.8) / 2)
        xmin = x - xlength
        xmax = x + xlength
        ymin = x - ylength
        ymax = x + ylength
        # set new limits
        self.xlim = [xmin, xmax]
        self.ylim = [ymax, ymin]
        window.update_fig()

    def move(self, window):
        if window.eraseMode.isChecked():
            window.eraseMode.toggle()
        if window.moveMode.isChecked():
            window.moveMode.setStyleSheet("image: url('Application/Icons/move_clicked.png') ;")
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            self.cid = self.fig.canvas.mpl_connect('button_press_event', self.erasePoint)
            self.cid2 = self.fig.canvas.mpl_disconnect(window.dicom.cid2)
            self.cid2 = self.fig.canvas.mpl_connect('button_release_event', self.movePoint)
        else:
            self.reconnect_cids(window)
            window.moveMode.setStyleSheet("image: url('Application/Icons/move.png') ;")

    def movePoint(self, event):
        window = self.parent().parent()
        self.selection(event)
        self.pressed = False
        self.pos = []
        window.reset_after_changes()

    def hide(self, window):
        if window.dontShow.isChecked():
            self.cid = self.fig.canvas.mpl_disconnect(window.dicom.cid)
            window.dontShow.setStyleSheet("image: url('Application/Icons/ds.png') ;")
            print("hide")
            plt.clf()
            window.dicom.img = plt.imshow(self.imgarr, self.cmap, vmin=self.vmin, vmax=self.vmax)
            window.dicom.draw()
            window.mainLayout.insertWidget(1, window.dicom)

        elif not window.dontShow.isChecked():
            self.reconnect_cids(window)
            window.update_fig()
            window.dontShow.setStyleSheet("image: url('Application/Icons/visible.png') ;")
            print("unhide")

    def save(self):
        test = QFileDialog.getSaveFileName(self, "Save File", filter="Images (*.png *.jpg)")
        plt.savefig(test[0])
