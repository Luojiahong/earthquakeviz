# Thing Thing
import sys
from vtk import *
from ReadPointsCSV import *

data=vtkUnstructuredGrid()
location, magnitude, time = readPoints("events2.csv")
data.SetPoints(location)
data.GetPointData().SetScalars(magnitude)

ball = vtkSphereSource()
ball.SetRadius(5)
ball.SetThetaResolution(12)
ball.SetPhiResolution(12)

ballGlyph = vtkGlyph3D()
ballGlyph.SetSourceConnection(ball.GetOutputPort())

ballGlyph.SetInput(data)
ballGlyph.SetScaleModeToScaleByScalar()
ballGlyph.SetColorModeToColorByScalar()
# ballGlyph.SetScaleModeToDataScalingOff()

colorTransferFunction = vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(2.0, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(2.5, 0.0, 1.0, 1.0)
colorTransferFunction.AddRGBPoint(3.0, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(4.0, 1.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(5.0, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(6.0, 1.0, 0.0, 1.0)

myMapper = vtkPolyDataMapper()
myMapper.SetInputConnection(ballGlyph.GetOutputPort())
myMapper.SetLookupTable(colorTransferFunction)

myActor = vtkActor()
myActor.SetMapper(myMapper)
myActor.GetProperty().SetColor(0.9,0.9,0.1)

# Add an outline
outline = vtkOutlineFilter()
outline.SetInput(data)

outlineMapper = vtkPolyDataMapper()
outlineMapper.SetInput(outline.GetOutput())
outlineActor = vtkActor()

outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetDiffuseColor(0.0, 0.0, 0.0)
outlineActor.GetProperty().SetLineWidth(2)

# Create the RenderWindow, Renderer and Interator
ren = vtkRenderer()
ren.AddActor(outlineActor)
ren.AddActor(myActor)
ren.SetBackground(0.4, 0.4, 0.6)

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetWindowName("Earthquake")
renWin.SetSize(500,500)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.Initialize()
iren.Start()