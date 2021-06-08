import vtk
import os

test = "/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/sax_10/IM-6507-0001.dcm"
directory ="/Users/Heni/OneDrive/Uni/Bachelorarbeit/second-annual-data-science-bowl/test/test/932/study/sax_10/"


# reader the dicom file
reader = vtk.vtkDICOMImageReader()
reader.SetDataByteOrderToLittleEndian()
reader.SetFileName("IM-13020-0001.dcm")
reader.Update()


# image data

imageData = reader.GetOutput()
imageData.SetOrigin(0,0,0)
print(imageData.GetExtent())
# imageData.SetScalarComponentFromDouble(10,10,0,0, 250)  # R


# rgb test image

image = vtk.vtkPNGReader()
image.SetFileName("rgb_test.png")
image.Update()
imageData2 = image.GetOutput()
print(imageData2.GetExtent())

# vtk image canvas source 2d

imageCanvas = vtk.vtkImageCanvasSource2D()
imageCanvas.InitializeCanvasVolume(imageData)
imageCanvas.SetExtent(imageData.GetExtent())
imageCanvas.SetDrawColor(255, 0, 0, 0.01)
imageCanvas.FillTriangle(0, 0, 100, 30, 10, 140)
imageCanvas.Update()



# show the dicom file 
# example from github

imageviewer = vtk.vtkImageViewer2()
imageviewer.SetInputData(imageCanvas.GetOutput())
renderwindowinteractor = vtk.vtkRenderWindowInteractor()
imageviewer.SetupInteractor(renderwindowinteractor)
imageviewer.Render()
imageviewer.GetRenderer(). ResetCamera()
imageviewer.Render()


'''
# look up table
lut = vtk.vtkLookupTable()
lut.SetHueRange(0, 1)
lut.SetSaturationRange(0, 0.2)
lut.SetValueRange(0, 2560)
lut.SetNumberOfColors(256)
lut.Build()
'''
# rgb version
color = vtk.vtkImageMapToColors()
color.SetInputConnection(imageCanvas.GetOutputPort())
#color.SetLookupTable(lut)
color.Update()


# black and white version
mapper = vtk.vtkImageMapper()
mapper.SetInputConnection(imageCanvas.GetOutputPort())
mapper.Update()

# black and white version
actor = vtk.vtkActor2D()
actor.SetMapper(mapper)

# rgb version
imageActor = vtk.vtkImageActor()
imageActor.GetMapper().SetInputConnection(color.GetOutputPort())

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Add the actor to the scene
renderer.AddActor(imageActor)
renderWindow.SetSize(1227, 1163)

renderWindow.SetWindowName('Actor2D')

# Render and interact
renderWindow.Render()
print(renderWindow.GetSize())
renderWindowInteractor.Start()

renderwindowinteractor.Start()
