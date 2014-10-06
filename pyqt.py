import sys
from vtk import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ReadPointsCSV import *
from numpy import *
from vtk.util.numpy_support import *
import datetime

debug = True
 
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(603, 553)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.gridlayout.addWidget(self.vtkWidget, 0, 1, 1, 12)
        MainWindow.setCentralWidget(self.centralWidget)

        self.date2 = QtGui.QDateTimeEdit()
        dateTime2 = QtCore.QDateTime(2012,1,1,00,00)
        self.date2.setDateTime(dateTime2)
        self.gridlayout.addWidget(self.date2,1,3,2,2)

        self.date1 = QtGui.QDateTimeEdit()
        dateTime1 = QtCore.QDateTime(2012,12,31,00,00)
        self.date1.setDateTime(dateTime1)
        self.gridlayout.addWidget(self.date1,1,5,2,2)

        # Magnitude upper limit filtering+submit
        magnitudeLabel = QtGui.QLabel("Magnitude:")
        magnitudeLabel.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(magnitudeLabel,5,3,2,2)
        self.magnitudeValue = QtGui.QLineEdit()

        # self.magnitudeValue.setMaxLength(3)

        # Use input mask for input validation, instead of setMaxLength
        # or other manual checks by using if to let input only numbers.
        self.magnitudeValue.setInputMask("0.0")
        self.magnitudeValue.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(self.magnitudeValue,5,5,2,2)
        self.submit= QtGui.QPushButton("submit")
        self.gridlayout.addWidget(self.submit,5,7,2,2)


        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        # sld.setFocusPolicy(QtCore.Qt.NoFocus)
        # sld.setGeometry(30, 40, 100, 30)
        # sld.valueChanged[int].connect(self.changeValue)
        self.gridlayout.addWidget(self.sld,7,3,1,6)
 
class VTKView(QtGui.QMainWindow):
    
    def eventFilter(self, source, event):
        # if (event.type() == QtCore.QEvent.MouseMove):
            # pos = event.pos()
            # print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
        if (event.type() == QtCore.QEvent.KeyPress):
            print event.text()
            self.plane.SetPoint1(500,500,0)
        return QtGui.QWidget.eventFilter(self, source, event)

    def submitClicked(self):
        # GUI Items
        magnitudeMax = self.ui.magnitudeValue.text()
        if magnitudeMax == ".":
            magnitudeMax = 10.0
        date1 = time.mktime(self.ui.date1.dateTime().toPyDateTime().timetuple())
        date2 = time.mktime(self.ui.date2.dateTime().toPyDateTime().timetuple())

        # Create the data subset (of the entire set)
        locationArray = vtk_to_numpy(self.location.GetData())
        magnitudeArray = vtk_to_numpy(self.magnitude)
        timeArray = vtk_to_numpy(self.time)
        dataSubset = [locationArray, magnitudeArray, timeArray]

        # First, filter all the data by location
        # dataSubset = self.filterByLocation(dataSubset,44.3333,45.3333,10.7833,11.8833)

        # # Then, filter the resulting set by magnitude
        # dataSubset = self.filterByMagnitude(dataSubset, 0.0, magnitudeMax)

        # # Next, filter the resulting set by time
        # dataSubset = self.filterByTime(dataSubset, date1, date2)

        dataSubset = self.filter(dataSubset,location=(44.3333,45.3333,10.7833,11.8833),\
               magnitudeMax=magnitudeMax, time=(date1,date2))

        # Set the data
        self.setData(dataSubset)

        # Lastly, rerender the widget
        self.ui.vtkWidget.GetRenderWindow().Render()

    def changeValue(self, value):
        print value

    def pointsToGPS(self, point0,point1):
        # Translate back to longitude and latitude
        lat = ((point0 / self.x1) * (self.latMax - self.latMin)) + self.latMin
        u = (lat-self.latMin)/(self.latMax-self.latMin)
        yy = (1-u)*self.y1+u*self.y2
        lon = ((point1 / yy) * (self.lonMax - self.lonMin)) + self.lonMin
        return (lat,lon)

    def GPSToPoints(self,x,y):
        u=(x-self.latMin)/(self.latMax-self.latMin)
        x=(x-self.latMin)/(self.latMax-self.latMin)*self.x1
        yy=(1-u)*self.y1+u*self.y2
        y=(y-self.lonMin)/(self.lonMax-self.lonMin)*yy
        return (x,y)

    def filter(self,dataSubset,location=(44.3333,45.3333,10.7833,11.8833),\
               magnitudeMax=10.0, time=None):
        locationSet, magnitudeSet, timeSet = dataSubset
        latInputMin,latInputMax,lonInputMin,lonInputMax = location
        if time:
            t1,t2 = time

        locationSubset = []
        magnitudeSubset = []
        timeSubset = []
        inRange = 0
        outRange = 0

        if debug:
            print "Filtering..."

        for i in range(len(locationSet)):
            # First Check if location is in bounds
            lat, lon = self.pointsToGPS(locationSet[i][0],locationSet[i][1])
            if lat > latInputMin and lat < latInputMax and lon > lonInputMin and lon < lonInputMax:
                # Next Check if magnitude is in bounds
                if magnitudeSet[i]<=float(magnitudeMax):
                    # Lastly, if time is set, check if time is in bounds
                    if(time):
                        if(timeSet[i] < t1 and timeSet[i] > t2):
                            locationSubset.append(locationSet[i])
                            magnitudeSubset.append(magnitudeSet[i])
                            timeSubset.append(timeSet[i])
                            inRange += 1
                        else:
                            outRange += 1
                    else:
                        locationSubset.append(locationSet[i])
                        magnitudeSubset.append(magnitudeSet[i])
                        timeSubset.append(timeSet[i])
                        inRange += 1
                else:
                    outRange += 1
            else:
                outRange += 1

        if debug:
            print str(inRange) + " points out of " + str(inRange+outRange)

        locationSubset = numpy.copy(locationSubset)
        magnitudeSubset = numpy.copy(magnitudeSubset)
        timeSubset = numpy.copy(timeSubset)

        # Set Bounding Box
        self.xmin,self.ymin = self.GPSToPoints(latInputMin,lonInputMin)
        self.xmax,self.ymax = self.GPSToPoints(latInputMax,lonInputMax)
        self.zmin = 0
        self.zmax = self.zmin + 100

        return locationSubset, magnitudeSubset, timeSubset

    def setData(self,dataSubset):
        locationSubset, magnitudeSubset, timeSubset = dataSubset
        lo = vtkPoints()
        for i in range(len(locationSubset)):
            lo.InsertNextPoint(locationSubset[i])
        self.data.SetPoints(lo)
        self.data.GetPointData().SetScalars(self.magnitude)

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.ui.submit.clicked.connect(self.submitClicked)

        self.data=vtkUnstructuredGrid()
        filename = "events2014.csv"
        self.location, self.magnitude, self.time, self.latMin,\
        self.latMax, self.lonMin, self.lonMax, self.x1, self.x2,\
        self.y1, self.y2 = readPoints(filename)
        self.xmin, self.ymin, self.zmin,\
        self.xmax, self.ymax, self.zmax = (0,)*6

        # Create the data subset (of the entire set)
        locationArray = vtk_to_numpy(self.location.GetData())
        magnitudeArray = vtk_to_numpy(self.magnitude)
        timeArray = vtk_to_numpy(self.time)
        dataSubset = [locationArray, magnitudeArray, timeArray]

        # dataSubset = self.filter(dataSubset,location=(44.3333,45.3333,10.7833,11.8833))
        dataSubset = self.filter(dataSubset,location=(35.073,47.898,6.02,18.989))
        self.setData(dataSubset)

        # Set the magnitude colormap
        colorTransferFunction = vtkColorTransferFunction()
        # colorTransferFunction = vtkLookupTable()
        # colorTransferFunction.SetHueRange(0.667, 0.0)
        # colorTransferFunction.SetValueRange(1.0, 1.0)
        # colorTransferFunction.SetSaturationRange(1.0, 1.0)
        # colorTransferFunction.SetTableRange(0.0,b)
        colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
        colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 1.0)
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

        outline = vtkOutlineSource()

        # Create an outline of the volume
        bounds = self.xmin,self.xmax,self.ymin,self.ymax,self.zmin,self.zmax

        outline = vtkOutlineSource()
        outline.SetBounds(self.xmin,self.xmax,self.ymin,self.ymax,self.zmin,self.zmax)
        outline_mapper = vtkPolyDataMapper()
        outline_mapper.SetInput(outline.GetOutput())
        outline_actor = vtkActor()
        outline_actor.SetMapper(outline_mapper)

        # print outline_mapper.GetBounds()

        # Define actor properties (color, shading, line width, etc)
        outline_actor.GetProperty().SetColor(0.0, 0.0, 0.0)
        outline_actor.GetProperty().SetLineWidth(2.0)

        # Read the image data from a file
        reader  = vtk.vtkJPEGReader()
        reader.SetFileName("italy.jpeg")

        texture = vtk.vtkTexture()
        texture.SetInputConnection(reader.GetOutputPort())
        texture.InterpolateOn()

        origin = (self.xmax-self.xmin/2,self.ymax-self.ymin/2,self.zmin)

        self.plane = vtk.vtkPlaneSource()
        self.plane.SetXResolution(1)
        self.plane.SetYResolution(1)
        self.plane.SetOrigin(origin)
        self.plane.SetPoint1(self.xmax,self.ymin,self.zmin)
        self.plane.SetPoint2(self.xmin,self.ymax,self.zmin)

        planeMapper = vtk.vtkPolyDataMapper()
        planeMapper.SetInputConnection(self.plane.GetOutputPort())
        planeActor = vtk.vtkActor()
        planeActor.SetMapper(planeMapper)
        planeActor.SetTexture(texture)
        planeActor.GetProperty().SetOpacity(.5)
        self.ren.AddActor(planeActor)

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
