import sys
from vtk import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ReadPointsCSV import *
import datetime
 
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(603, 553)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.gridlayout.addWidget(self.vtkWidget, 0, 1, 1, 12)
        MainWindow.setCentralWidget(self.centralWidget)

        exitAction = QtGui.QAction('_Quit', MainWindow)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = MainWindow.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(exitAction)

        date1 = QtGui.QDateTimeEdit()
        self.gridlayout.addWidget(date1,1,3,2,2)
        date2 = QtGui.QDateTimeEdit()
        self.gridlayout.addWidget(date2,1,5,2,2)
        submitDate = QtGui.QPushButton("submit")
        self.gridlayout.addWidget(submitDate,1,7,2,2)

        intensityLabel = QtGui.QLabel("Intensity:")
        intensityLabel.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(intensityLabel,3,3,2,2)
        intensity = QtGui.QLineEdit()
        self.gridlayout.addWidget(intensity,3,5,2,2)
        submitIntensity = QtGui.QPushButton("submit")
        self.gridlayout.addWidget(submitIntensity,3,7,2,2)

        sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        # sld.setFocusPolicy(QtCore.Qt.NoFocus)
        # sld.setGeometry(30, 40, 100, 30)
        # sld.valueChanged[int].connect(self.changeValue)
        self.gridlayout.addWidget(sld,5,3,1,6)
 
class VTKView(QtGui.QMainWindow):
    
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove):
            pos = event.pos()
            print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
        elif (event.type() == QtCore.QEvent.KeyPress):
            print event.text()
        return QtGui.QWidget.eventFilter(self, source, event)

    def handleButton(self):
        print "buttonPressed"
        # for frame in range(1,100):
        #     locationSubset = vtkPoints();
        #     for i in range(
        #         ):
        #       point = self.location.GetPoint(i)
        #       locationSubset.InsertNextPoint(point)
        #     self.data.SetPoints(locationSubset)
        #     self.data.GetPointData().SetScalars(self.magnitude)
        #     self.ui.vtkWidget.GetRenderWindow().Render()
        #     self.prevPoints = self.numPoints
        #     self.numPoints += 100

    def changeValue(self, value):
        print value
        # locationSubset = vtkPoints();
        # currentPoint = int(self.location.GetNumberOfPoints() * (float(value)/100))
        # # for i in range(currentPoint + 20):
        # point = self.location.GetPoint(currentPoint)
        # # print self.location.GetPoint(currentPoint)
        # currentTime = self.time.GetTuple(currentPoint)
        # for i in range(self.time.GetNumberOfTuples()):
        #     if(self.time.GetTuple(i)[0] == self.time.GetTuple(self.time.GetNumberOfTuples() - 1)[0]):
        #         formattedTime = (
        #             datetime.datetime.fromtimestamp(
        #                 self.time.GetTuple(i)[0]
        #             ).strftime('%Y-%m-%d %H:%M:%S')
        #         )
        #         print i
        #         print formattedTime
        # print currentTime

        # vtktonumpy
        # numpytovtk

        # # print self.location.GetNumberOfPoints()

        # locationSubset.InsertNextPoint(point)
        # self.text.SetInput(formattedTime)
        # self.data.SetPoints(locationSubset)
        # self.data.GetPointData().SetScalars(self.magnitude)
        # self.ui.vtkWidget.GetRenderWindow().Render()


    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        self.prevPoints = 0

        self.data=vtkUnstructuredGrid()
        filename = "events2014.csv"
        self.location, self.magnitude, self.time = readPoints(filename)

        # Subset of Data
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
        # sphereGlyph.SetScaleModeToDataScalingOff()

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
        self.text = vtkTextActor()
        self.text.GetTextProperty().SetFontSize(28)
        self.text.GetTextProperty().BoldOn()
        self.text.SetPosition2(10, 40)  
        self.text.SetInput("9. Screenshot")
        self.text.GetTextProperty().SetColor(0.0,0.0,0.0)

        # Text adjustment
        tpc = self.text.GetPositionCoordinate()
        tpc.SetCoordinateSystemToNormalizedViewport()
        tpc.SetValue(0.01,0.95)

        self.ren.SetBackground(0.6, 0.6, 0.6)
        self.ren.AddActor(sphereActor)
        self.ren.AddActor(outline_actor)
        self.ren.AddActor2D(self.text)
        self.ui.vtkWidget.installEventFilter(self)

if __name__ == "__main__":
 
    app = QApplication(sys.argv)
    window = VTKView()
    window.show()
    window.iren.Initialize() # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())