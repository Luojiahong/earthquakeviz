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
        dateTime2 = QtCore.QDateTime(2012,5,1,00,00)
        self.date2.setDateTime(dateTime2)
        self.gridlayout.addWidget(self.date2,1,3,2,2)

        self.date1 = QtGui.QDateTimeEdit()
        dateTime1 = QtCore.QDateTime(2012,5,31,00,00)
        self.date1.setDateTime(dateTime1)
        self.gridlayout.addWidget(self.date1,1,5,2,2)

        # Magnitude upper limit filtering+submit
        magnitudeLabel = QtGui.QLabel("Magnitude:")
        magnitudeLabel.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(magnitudeLabel,5,3,2,2)
        self.magnitudeValue = QtGui.QLineEdit()

        # Use input mask for input validation, instead of setMaxLength
        # or other manual checks by using if to let input only numbers.
        self.magnitudeValue.setInputMask("0.0")
        self.magnitudeValue.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(self.magnitudeValue,5,5,2,2)

        # Controls the planes opacity
        planeOpacityLabel = QtGui.QLabel("Plane Opacity:")
        planeOpacityLabel.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(planeOpacityLabel,7,3,2,2)
        self.opacityValue = QtGui.QLineEdit()

        # Use input mask for input validation, instead of setMaxLength
        # or other manual checks by using if to let input only numbers.
        self.opacityValue.setInputMask("0.0")
        self.opacityValue.setAlignment(QtCore.Qt.AlignRight)
        self.gridlayout.addWidget(self.opacityValue,7,5,2,2)
        

        self.submit= QtGui.QPushButton("submit")
        self.gridlayout.addWidget(self.submit,7,7,2,2)


        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sld.setTracking(False)
        self.sld.setDisabled(True)
        self.gridlayout.addWidget(self.sld,9,3,1,6)
 
class VTKView(QtGui.QMainWindow):
    
    def eventFilter(self, source, event):
        # if (event.type() == QtCore.QEvent.MouseMove):
            # pos = event.pos()
            # print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
        if (event.type() == QtCore.QEvent.KeyPress):
            print event.text()
            if event.text() == "a":
                for i in range(1,100):
                    self.ui.sld.setValue(i)
            if event.text() == " ":
                exit(0)
        return QtGui.QWidget.eventFilter(self, source, event)

    def submitClicked(self):
        # GUI Items
        magnitudeMax = self.ui.magnitudeValue.text()
        if magnitudeMax == ".":
            magnitudeMax = 10.0
        opacityValue = self.ui.opacityValue.text()
        if opacityValue == ".":
            opacityValue = 0.3
        date2 = time.mktime(self.ui.date1.dateTime().toPyDateTime().timetuple())
        date1 = time.mktime(self.ui.date2.dateTime().toPyDateTime().timetuple())

        # Create the data subset (of the entire set)
        locationArray = vtk_to_numpy(self.location.GetData())
        magnitudeArray = vtk_to_numpy(self.magnitude)
        timeArray = vtk_to_numpy(self.time)
        dataSubset = [locationArray, magnitudeArray, timeArray]

        # Filter the data
        dataSubset = self.filter(dataSubset,location=(44.3333,45.3333,10.7833,11.8833),\
               magnitudeMax=magnitudeMax, time=(date1,date2))

        self.lastDataSubset = dataSubset

        # Reset Slider
        self.ui.sld.setDisabled(False)
        self.ui.sld.setValue(0);

        # Change Opacity
        self.planeActor.GetProperty().SetOpacity(float(opacityValue))
            
        # Lastly, rerender the widget
        self.ui.vtkWidget.GetRenderWindow().Render()

    def sliderChangeValue(self, value):
        if value != 0:
            location, magnitude = self.filterValues
            t1 = time.mktime(self.ui.date1.dateTime().toPyDateTime().timetuple())
            t2 = time.mktime(self.ui.date2.dateTime().toPyDateTime().timetuple())
            
            # Filter the data
            start = ((t1 - t2) * (float(value)/100)) + t2
            end = start + ((t1 - t2) * 0.2)
            dataSubset = self.filter(self.lastDataSubset,location=location,\
                   magnitudeMax=magnitude, time=(start,end))

            # Lastly, rerender the widget
            self.ui.vtkWidget.GetRenderWindow().Render()   

            if debug:
                print "Filtering " + str(datetime.date.fromtimestamp(start)) + " to " + str(datetime.date.fromtimestamp(end))
 

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

        data = vtkPoints()

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
                        if(timeSet[i] < t2 and timeSet[i] > t1):
                            locationSubset.append(locationSet[i])
                            magnitudeSubset.append(magnitudeSet[i])
                            timeSubset.append(timeSet[i])
                            data.InsertNextPoint(locationSet[i])
                            inRange += 1
                        else:
                            outRange += 1
                    else:
                        locationSubset.append(locationSet[i])
                        magnitudeSubset.append(magnitudeSet[i])
                        timeSubset.append(timeSet[i])
                        data.InsertNextPoint(locationSet[i])
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

        
        # Set current filter values
        self.filterValues = (location,magnitudeMax)


        displayStr = "Location: " + str(location) + "\n" +\
            "Maximum Magnitude: " + str(magnitudeMax)
        if (time):
            dateTime1 = datetime.date.fromtimestamp(t1)
            dateTime2 = datetime.date.fromtimestamp(t2)
            displayStr += "\nTime: " + dateTime1.strftime("%Y-%m-%d")\
                    + " to " + dateTime2.strftime("%Y-%m-%d")\
                    #+ "\n      " + dateTime1.strftime("%H:%M")\
                    #+ "    " + dateTime2.strftime("%H:%M")

        self.text.SetInput(displayStr)

        self.data.SetPoints(data)
        self.data.GetPointData().SetScalars(self.magnitude)

        return locationSubset, magnitudeSubset, timeSubset

    def __init__(self, parent = None):

        # UI Information
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.ui.submit.clicked.connect(self.submitClicked)
        self.ui.sld.valueChanged[int].connect(self.sliderChangeValue)

        # Input Data
        self.data=vtkUnstructuredGrid()
        filename = "events2014.csv"
        self.location, self.magnitude, self.time, self.latMin,\
        self.latMax, self.lonMin, self.lonMax, self.x1, self.x2,\
        self.y1, self.y2 = readPoints(filename)
        self.xmin, self.ymin, self.zmin,\
        self.xmax, self.ymax, self.zmax = (0,)*6

        # Create instructions text
        self.text = vtkTextActor()
        self.text.GetTextProperty().SetFontSize(12)
        self.text.GetTextProperty().BoldOn()
        self.text.GetTextProperty().SetColor(0.0,0.0,0.0)

        # Text adjustment
        tpc = self.text.GetPositionCoordinate()
        tpc.SetCoordinateSystemToNormalizedViewport()
        tpc.SetValue(0.01,0.8)

        # Create the data subset (of the entire set)
        locationArray = vtk_to_numpy(self.location.GetData())
        magnitudeArray = vtk_to_numpy(self.magnitude)
        timeArray = vtk_to_numpy(self.time)
        dataSubset = [locationArray, magnitudeArray, timeArray]
        self.lastDataSubset = dataSubset

        # Filter Data
        dataSubset = self.filter(dataSubset)

        # Set the magnitude colormap
        colorTransferFunction = vtkColorTransferFunction()
        #colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.7, 0.0)
        #colorTransferFunction.AddRGBPoint(3.0, 1.0, 1.0, 0.0)
        #colorTransferFunction.AddRGBPoint(6.0, 1.0, 0.0, 0.0)
        colorTransferFunction.AddRGBPoint(0.0,59.0/255.0,37.0/255.0,123.0/255.0)
        colorTransferFunction.AddRGBPoint(1.0,12.0/255.0,3.0/255.0,166.0/255.0)
        colorTransferFunction.AddRGBPoint(2.0,187.0/255.0,53.0/255.0,155.0/255.0)
        colorTransferFunction.AddRGBPoint(3.0,228.0/255.0,87.0/255.0,110.0/255.0)
        colorTransferFunction.AddRGBPoint(4.0,248.0/255.0,127.0/255.0,76.0/255.0)
        colorTransferFunction.AddRGBPoint(5.0,255.0/255.0,175.0/255.0,69.0/255.0)
        colorTransferFunction.AddRGBPoint(6.0,255.0/255.0,212.0/255.0,89.0/255.0)
        #colorTransferFunction.AddRGBPoint(7.0,245,241,171)
        

        # Create a Sphere Source
        sphere = vtkSphereSource()
        sphere.SetRadius(0.3)
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

        # Create the scalar bar
        scalarBar = vtk.vtkScalarBarActor()
        scalarBar.SetLookupTable(myMapper.GetLookupTable())
        scalarBar.SetTitle("Magnitude")
        scalarBar.GetLabelTextProperty().SetColor(0,0,0)
        scalarBar.GetTitleTextProperty().SetColor(0,0,0)
        scalarBar.SetWidth(.15)
        scalarBar.SetHeight(1.0)

        spc = scalarBar.GetPositionCoordinate()
        spc.SetCoordinateSystemToNormalizedViewport()
        spc.SetValue(0.85,0.05)

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
        reader  = vtk.vtkPNGReader()
        reader.SetFileName("bologna.png")

        texture = vtk.vtkTexture()
        texture.SetInputConnection(reader.GetOutputPort())
        texture.InterpolateOn()

        # origin = (self.xmax-self.xmin/2,self.ymax-self.ymin/2,self.zmin)

        # Create a plane
        self.plane = vtk.vtkPlaneSource()
        self.plane.SetOrigin(self.xmin,math.ceil(self.ymin),self.zmin)
        self.plane.SetPoint1(self.xmax,math.ceil(self.ymin),self.zmin)
        self.plane.SetPoint2(self.xmin,math.ceil(self.ymax),self.zmin)
        self.plane.Update()

        planeMapper = vtk.vtkPolyDataMapper()
        planeMapper.SetInputConnection(self.plane.GetOutputPort())
        self.planeActor = vtk.vtkActor()
        self.planeActor.SetMapper(planeMapper)
        self.planeActor.SetTexture(texture)
        self.planeActor.GetProperty().SetOpacity(.5)
        self.planeActor.RotateY(180)
        sphereActor.RotateY(180)
        outline_actor.RotateY(180)
        self.planeActor.RotateZ(90)
        sphereActor.RotateZ(90)
        outline_actor.RotateZ(90)
        #scalarBar.RotateY(180)
        #self.text.RotateY(180)

        self.ren.SetBackground(0.6, 0.6, 0.6)
        self.ren.AddActor(self.planeActor)
        self.ren.AddActor(sphereActor)
        self.ren.AddActor(outline_actor)
        self.ren.AddActor(scalarBar)
        self.ren.AddActor2D(self.text)
        self.ui.vtkWidget.installEventFilter(self)

if __name__ == "__main__":
 
    app = QApplication(sys.argv)
    window = VTKView()
    window.show()
    window.iren.Initialize() # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())
