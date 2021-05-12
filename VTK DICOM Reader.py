import vtk


# reader the dicom file
reader = vtk.vtkDICOMImageReader()
reader.SetDataByteOrderToLittleEndian()
reader.SetFileName("IM-13020-0001.dcm")
reader.Update()

# show the dicom flie
imageviewer = vtk.vtkImageViewer2()
imageviewer.SetInputConnection(reader.GetOutputPort())
renderwindowinteractor = vtk.vtkRenderWindowInteractor()
imageviewer.SetupInteractor(renderwindowinteractor)
imageviewer.Render()
imageviewer.GetRenderer(). ResetCamera()
imageviewer.Render()

renderwindowinteractor.Start()
