#Converting NC drill procedure to EDM drill file
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QPushButton,QLabel,QFileDialog,QLineEdit,QDoubleSpinBox,QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt
import sys, re, os


class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        
        # Load the ui file
        uic.loadUi("ncPost.ui", self)
        
        self.fname=''
        
        self.setWindowIcon(QtGui.QIcon('SPARK.png'))
        
        # Define widgets
        self.openFileButton=self.findChild(QPushButton, "openFileButton")
        self.openFileLabel=self.findChild(QLabel, "openFileLabel")
        self.outputFileLabel=self.findChild(QLabel, "outputFileLabel")
        self.outputFileLine=self.findChild(QLineEdit, "outputFileLine")
        self.convertDataLabel=self.findChild(QLabel, "convertDataLabel")
        self.convertButton=self.findChild(QPushButton, "convertButton")
        self.diameterLabel=self.findChild(QLabel, "diameterLabel")
        self.diammDoubleSpinBox=self.findChild(QDoubleSpinBox , "diammDoubleSpinBox")
        self.graphicsView=self.findChild(QGraphicsView, "graphicsView")
        
        self.openFileButton.setDefault(True)      
        self.openFileButton.setFocus()
        
        # Open file conection
        self.openFileButton.clicked.connect(self.openFile)               
        # Convert file
        self.convertButton.clicked.connect(self.checkName)        
        
        self.scene=QGraphicsScene()
        # Show app
        
        self.setFixedWidth(932)
        self.setFixedHeight(551)
        self.show()
        
    # Open file dialog
    def openFile(self):
        self.convertButton.setText("Convert")  
        self.convertButton.setStyleSheet("color: black")
        self.fname=QFileDialog.getOpenFileName(self,"NC file","H:\IGES","Text files(*.igs)")
        if self.fname:
            self.openFileLabel.setText(self.fname[0])
        self.convertButton.setEnabled(True)
        
        
    # Check output file name
    def checkName(self):
        goodName="^\d{4,4}$"
        outName=self.outputFileLine.text()
        self.outName=self.outputFileLine.text()
        if  re.search(goodName,outName):
            
            self.convert()
        else:           
            self.outputFileLine.setText("")
            
    # Plot on graphview witget
    def plot_point(self,points,d):
        
            x_min,y_min,x_max,y_max=min(points[0]),min(points[1]),max(points[0]),max(points[1])
            w=(abs(x_max)+abs(x_min))/2
            h=(abs(y_max)+abs(y_min))/2
            sc=1
            if abs(max(w,h)):
                sc=240/abs(max(w,h))
            else:
                pass
            self.scene.clear()
            pen = QtGui.QPen(Qt.green)
            pen.setWidth(2)
            center_pen=QtGui.QPen(Qt.white)
            center_pen.setWidth(1)
            for i in range(len(points[1])):
                x=points[0][i]*sc
                y=points[1][i]*sc
                fi=d*sc*0.7
                self.scene.addEllipse(x, y, fi, fi,pen)
            self.scene.addLine(-fi, 0, fi, 0,center_pen)
            self.scene.addLine(0,-fi, 0, fi,center_pen)
            
            self.graphicsView.setScene(self.scene)
            self.graphicsView.show()
        
        
    def convert(self):   
        # X,Y float patern
        circle ='100,0.,'
        output_code=[]
        data_list=[]
        
        # In and Out file names edit
        in_file=self.openFileLabel.text()
        out_file=self.outputFileLine.text()
        
        
        
        

        # Search for matches and filling in output_code list
        with open(in_file,'r',encoding='utf-8') as source_file:
  
            # Removing old rows and rechanging with news based on ; and put them to list
            raw_data=(source_file.read()).replace("\n",",").split(";")   

            # Check for arks in line 100 in IGES   
            for row in raw_data:
                edited_data=[]
                if circle in row:
                    data_list=row.split(",")  
                    
                    # Extracting just x,y start and end point
                    for d in range(len(data_list)):
                        try:
                            edited_data.append(round(float(data_list[d]),2)) 
                        except ValueError:
                            continue
                        
                    # Slicing unused data
                    points=edited_data[2:]
                    
                    # Check if its full cirkle start point equal to end point
                    if  points[2]==points[4] and points[3]==points[5]:
                        output_code.append(points)                
    
            
        # Writing post file with header and footer 
        conv_dir=os.path.dirname(in_file)
        conv_file=conv_dir+"/O"+out_file+".txt"
        needed_diam=round(float(self.diammDoubleSpinBox.value()),1)
        with open(conv_file,'w',encoding='utf-8') as post_file:
            hole_counter=0
            hole_list=[[],[]]
            post_file.writelines("%\nG90 G54 X0 Y0\nG92 X0 Y0 \n") 
            for w_line in output_code:          
                hole_diam=round(float(abs(w_line[2]-w_line[0])*2),1)
                x=w_line[0]
                y=w_line[1]
                
                if hole_diam==needed_diam :
                    post_file.write(f"X{x} Y{y} M20 \n")               
                    hole_list[0].append(x)
                    hole_list[1].append(y)
                    
                    hole_counter+=1
            
            post_file.write("M00\n%")
            
            # Draw tje circles
            if hole_counter:
                self.plot_point(hole_list,hole_diam)
            else:
                self.scene.clear()
            
        self.convertButton.setText("Converted")  
        self.convertButton.setStyleSheet("color: green")
        self.convertDataLabel.setText(f"Found {len(output_code)} holes \nSend {hole_counter} holes  Ø{needed_diam}")
       
        # Open NC file with Notepad
        open_file=os.startfile(conv_file)
        
# Initialize The App
app=QApplication(sys.argv)
UIWindow = UI()
app.exec_()


        
 
   
       
