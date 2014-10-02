import sys
from vtk import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ReadPointsCSV import *
 

# TEST comment
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(603, 553)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.vtkWidget.AddObserver('TimerEvent', self.execute)

    def execute(self,obj,event):
        print "hi"
 
class VTKView(QtGui.QMainWindow):
    
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove):
            pos = event.pos()
            print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
        elif (event.type() == QtCore.QEvent.KeyPress):
            print event.text()
        return QtGui.QWidget.eventFilter(self, source, event)

    def handleButton(self):
        for frame in range(1,100):
            locationSubset = vtkPoints();
            for i in range(self.prevPoints, self.numPoints):
              point = self.location.GetPoint(i)
              locationSubset.InsertNextPoint(point)
            self.data.SetPoints(locationSubset)
            self.data.GetPointData().SetScalars(self.magnitude)
            self.ui.vtkWidget.GetRenderWindow().Render()
            self.prevPoints = self.numPoints
            self.numPoints += 100

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.numPoints = 100
        self.prevPoints = 0

        # GUI
        action = QtGui.QAction(self)
        action.setText('Launch Animation')
        action.triggered.connect(self.handleButton)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(action)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(action)

 
        self.data=vtkUnstructuredGrid()
        filename = "events2014.csv"
        self.location, self.magnitude, time = readPoints(filename)

        # Test Code

        locationSubset = vtkPoints()
        locationData = []
        for i in range(1000):
          point = self.location.GetPoint(i)
          locationSubset.InsertNextPoint(point)
          locationData.append(point)

        self.data.SetPoints(locationSubset)
        self.data.GetPointData().SetScalars(self.magnitude)

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

        # Connect the self.data to glyph
        sphereGlyph.SetInput(self.data)
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
        outline.SetInput(self.data)
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

        self.ren.SetBackground(0.6, 0.6, 0.6)
        self.ren.AddActor(sphereActor)
        # self.ren.AddActor(outline_actor)
        self.ren.AddActor2D(text)
        self.ui.vtkWidget.installEventFilter(self)

if __name__ == "__main__":
 
    app = QApplication(sys.argv)
    window = VTKView()
    window.show()
    window.iren.Initialize() # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())