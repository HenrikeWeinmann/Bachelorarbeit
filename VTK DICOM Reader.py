import vtk
import os

test = "/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/sax_10/IM-6507-0001.dcm"
directory ="/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/sax_10/"

fnames = os.listdir(directory)
fnames.sort()
curr = 1




# reader the dicom file
reader = vtk.vtkDICOMImageReader()
reader.SetDataByteOrderToLittleEndian()
reader.SetFileName(directory + fnames[curr])
reader.Update()

# show the dicom flie
imageviewer = vtk.vtkImageViewer2()
imageviewer.SetInputConnection(reader.GetOutputPort())
renderwindowinteractor = vtk.vtkRenderWindowInteractor()
imageviewer.SetupInteractor(renderwindowinteractor)
imageviewer.Render()
imageviewer.GetRenderer(). ResetCamera()
imageviewer.Render()


#animation
renderwindowinteractor.CreateRepeatingTimer(int(1/60))
renderwindowinteractor.AddObserver("TimerEvent", callback_func)


renderwindowinteractor.Start()
