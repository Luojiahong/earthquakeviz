# Python project for Scientific Visualization.
# Reading and ploting earthquake data.

import sys
from vtk import *
from ReadPointsCSV import *

filename = "events2014small.csv"

class KeyboardInterface(object):
    def __init__(self):
        self.screenshot_counter = 0
        self.render_window = None
        self.window2image_filter = None
        self.png_writer = None
        self.numPoints = 10

    def keypress(self, obj, event):
        """This function captures keypress events and defines actions for
        keyboard shortcuts."""
        key = obj.GetKeySym()
        if key == "9":
            self.render_window.Render()
            self.window2image_filter.Modified()
            screenshot_filename = ("screenshot%02d.png" %
                                   (self.screenshot_counter))
            self.png_writer.SetFileName(screenshot_filename)
            self.png_writer.Write()
            print("Saved %s" % (screenshot_filename))
            self.screenshot_counter += 1
        # Add your keyboard shortcuts here. If you modify any of the
        # actors or change some other parts or properties of the
        # scene, don't forget to call the render window's Render()
        # function to update the rendering.
        # elif key == ...
        if key == "1":
          for frame in range(1,100,1):
            location2 = vtkPoints();
            for i in range(self.numPoints):
              point = location.GetPoint(i)
              pointx = location.GetPoint(i)[0]
              pointy = location.GetPoint(i)[1]
              pointz = location.GetPoint(i)[2]
              location2.InsertNextPoint(pointx, pointy, pointz)
            data.SetPoints(location2)
            data.GetPointData().SetScalars(magnitude)
            render_window.Render()
            self.numPoints += 100

# Read the data points from the external file
data=vtkUnstructuredGrid()
location, magnitude, time = readPoints(filename)

# Test Code

location2 = vtkPoints()

locationData = []
for i in range(10):
  point = location.GetPoint(i)
  pointx = location.GetPoint(i)[0]
  pointy = location.GetPoint(i)[1]
  pointz = location.GetPoint(i)[2]
  location2.InsertNextPoint(pointx, pointy, pointz)
  locationData.append(point)
print locationData
# exit(0)
# print location.GetPoints(idList,location)

data.SetPoints(location2)
data.GetPointData().SetScalars(magnitude)

# Set the magnitude colormap
colorTransferFunction = vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(2.0, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(2.5, 0.0, 1.0, 1.0)
colorTransferFunction.AddRGBPoint(3.0, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(4.0, 1.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(5.0, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(6.0, 1.0, 0.0, 1.0)

# Create a Sphere Source
sphere = vtkSphereSource()
sphere.SetRadius(5)
sphere.SetThetaResolution(12)
sphere.SetPhiResolution(12)

# Connect the sphere to the glyph
sphereGlyph = vtkGlyph3D()
sphereGlyph.SetSourceConnection(sphere.GetOutputPort())

# Connect the data to glyph
sphereGlyph.SetInput(data)
sphereGlyph.SetScaleModeToScaleByScalar()
sphereGlyph.SetColorModeToColorByScalar()
sphereGlyph.SetScaleModeToDataScalingOff()

# Create a mapper
myMapper = vtkPolyDataMapper()
myMapper.SetInputConnection(sphereGlyph.GetOutputPort())
myMapper.SetLookupTable(colorTransferFunction)

# Create an actor
sphereActor = vtkActor()
sphereActor.SetMapper(myMapper)

# Create an outline of the volume
outline = vtkOutlineFilter()
outline.SetInput(data)
outline_mapper = vtkPolyDataMapper()
outline_mapper.SetInput(outline.GetOutput())
outline_actor = vtkActor()
outline_actor.SetMapper(outline_mapper)

# Define actor properties (color, shading, line width, etc)
outline_actor.GetProperty().SetColor(0.0, 0.0, 0.0)
outline_actor.GetProperty().SetLineWidth(2.0)

# Create instructions text
text = vtkTextActor()
text.GetTextProperty().SetFontSize(28)
text.GetTextProperty().BoldOn()
text.SetPosition2(10, 40)  
text.SetInput("9. Screenshot")
text.GetTextProperty().SetColor(0.0,0.0,0.0)

# Text adjustment
tpc = text.GetPositionCoordinate()
tpc.SetCoordinateSystemToNormalizedViewport()
tpc.SetValue(0.01,0.95)

# Create a renderer and add the actors to it
renderer = vtkRenderer()
renderer.SetBackground(0.6, 0.6, 0.6)
renderer.AddActor(sphereActor)
renderer.AddActor(outline_actor)
renderer.AddActor2D(text)

# Create a render window
render_window = vtkRenderWindow()
render_window.SetWindowName("Italy erthquake")
render_window.SetSize(800, 600)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a window-to-image filter and a PNG writer that can be used
# to take screenshots
window2image_filter = vtk.vtkWindowToImageFilter()
window2image_filter.SetInput(render_window)
png_writer = vtk.vtkPNGWriter()
png_writer.SetInput(window2image_filter.GetOutput())

# Set up the keyboard interface
keyboard_interface = KeyboardInterface()
keyboard_interface.render_window = render_window
keyboard_interface.window2image_filter = window2image_filter
keyboard_interface.png_writer = png_writer
keyboard_interface.numPoints = 10

# Connect the keyboard interface to the interactor
interactor.AddObserver("KeyPressEvent", keyboard_interface.keypress)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()