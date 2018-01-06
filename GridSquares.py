import numpy as np
import cv2
import sys
import glob
from operator import attrgetter
import math

def dot(a,b):#a.b
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def dot2(a,b):
	return a[0]*b[0]+a[1]*b[1]
def vecsub(a,b):#a-b
	return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]
def vecsub2(a,b):
	return [a[0]-b[0],a[1]-b[1]]
def vecadd(a,b): #a+b
	return [a[0]+b[0],a[1]+b[1],a[2]+b[2]]
def distance(a): #magnitude a
	return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
def distance2(a): #magnitude a
	return math.sqrt(a[0]*a[0]+a[1]*a[1])
def scalarmult(a,b): #Multiply vector a by number b
	return([a[0]*b,a[1]*b,a[2]*b])
def sign(a,b): #Are a and b in the same direction or opposite?
	return(dot(a,b)/abs(dot(a,b)))
def vectordiv(a,b):
	return((a[0]/b[0]+a[1]/b[1]+a[2]/b[2])/3)
def cross(a,b): #a cross b
	return([a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]])
def cross2D(a, b): #a cross b
	return(a[0]*b[1]-a[1]*b[0])
def proj(a,b): #Projection of b onto unit vector a
	return(scalarmult(a,dot(a,b)/(distance(a)*distance(a))))

def computeFrameSquares(image):
	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	try:
		cv2.imshow('Threshold',ret) #Display the thresholded image
	except:
		#exit=1 #If that's not working, your screwed. Just give up now.
		pass
	dump,contours,hierarchy=cv2.findContours(ret,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) #Get contours in image in a list.
	contours.sort(key=cv2.contourArea,reverse=True) #Sort them by area. Trust me. Saves time because there are a ton of contours with 0 area.
	contour=0 #Iterator
	squares=[] #List of squares to add to.
	while(contour<len(contours) and cv2.contourArea(contours[contour])>1000): #Loop until area is too small or all are done
		newsquare=gridSquare(contours[contour])
		#print cv2.contourArea(contours[contour])
		epsilon = 0.01*cv2.arcLength(newsquare.contour,True) #Set up for simplifying contours
		newsquare.corners=cv2.approxPolyDP(newsquare.contour,epsilon,True) #Actually simplifying
		if(len(newsquare.corners)==4): #If the simplified version has 4 sides
			squares.append(newsquare) #And mark it as a square
		contour+=1 #Iterate
	return squares


class gridSquare:
	camvec=[] #Vector pointing to camera, in camera coords
	side1=[] #Unit vector from center to side1 of square, in camera coords
	side2=[] #Unit vector from center to side1 of square, in camera coords
	normal=[] #Normal vector pointing out of the square	

	score=0 #How good is this square. See compare square normals for more
	corners=[] #Image coordinates of square corners
	contour=None #Unsimplified image coordinates of square corners
	location=[] #Square location in camera coordinates
	def getPosStats(self):
		tempcorners=self.corners.reshape(4,2,1).astype(float) #The points need to be floats, and in a specific shape
		inliers,rvec,tvec=cv2.solvePnP(objectpoints,tempcorners,CameraMatrix,distortionCoefficients) #Where the magic happens. Turns gets vector from camera to center of square
		inliers,rvec2,tvec2=cv2.solvePnP(secondObjectCorners,tempcorners,CameraMatrix,distortionCoefficients)
		inliers,rvec3,tvec3=cv2.solvePnP(thirdObjectCorners,tempcorners,CameraMatrix,distortionCoefficients)
		#print rvec
		#print rvec2
		#print rvec3

		#print(distance(vecsub(tvec2,tvec)),distance(vecsub(tvec3,tvec)))
		line1=scalarmult(vecsub(tvec2,tvec),1/distance(vecsub(tvec2,tvec)))
		line2=scalarmult(vecsub(tvec3,tvec),1/distance(vecsub(tvec3,tvec)))
		self.camvec=[float(tvec[0]),float(tvec[1]),float(tvec[2])]
		self.side1=[float(line1[0]),float(line1[1]),float(line1[2])]
		self.side2=[float(line2[0]),float(line2[1]),float(line2[2])]
		self.normal=cross(self.side1,self.side2)
		tempx=proj(self.side1,self.camvec)
		tempy=proj(self.side2,self.camvec)
		tempz=proj(self.normal,self.camvec)
		self.location=[sign(tempx,self.side1)*distance(tempx),sign(tempy,self.side2)*distance(tempy),sign(tempz,self.normal)*distance(tempz)]
		#print ("CONTOUR")
		#print (self.contour)
		#print ("CORNERS")
		#print (self.corners)
		#self.location[0]=sign(temp,self.side1)*distance(temp)

#		self.location[1]=sign(temp,self.side2)*distance(temp)
#		self.location[2]=sign(temp,self.normal)*distance(temp)
		#print self.location
		#print ""
	def compareSquareNormals(self,square):
		tempcross=cross(self.normal,square.normal)
		edge=0
		for point in square.corners:
			if(point[0][0]<1 or point[0][0]>len(img[0])-2 or point[0][1]<1 or point[0][1]>len(img)-2):
				edge=1
		if(not edge):
			#score+=abs(dot(cross1,cross2))
			self.score+=1-abs(distance(tempcross)/(distance(square.normal)*distance(self.normal)))
	def __init__(self,contour):
		self.contour=contour
		
squarelength=28.5 #Needs to be a float, in cm of real length of the squares
objectpoints=np.array([[[-squarelength/2,-squarelength/2,0]],[[-squarelength/2,squarelength/2,0]],[[squarelength/2,squarelength/2,0]],[[squarelength/2,-squarelength/2,0]]],np.float32) #3d grid square coordinates
secondObjectCorners=np.array([[[-squarelength/2,0,0]],[[-squarelength/2,squarelength,0]],[[squarelength/2,squarelength,0]],[[squarelength/2,0,0]]],np.float32)
thirdObjectCorners=np.array([[[0,-squarelength/2,0]],[[0,squarelength/2,0]],[[squarelength,squarelength/2,0]],[[squarelength,-squarelength/2,0]]],np.float32)

objectpoints=objectpoints.reshape(4,3,1) #Needs to be this shape
secondObjectCorners=secondObjectCorners.reshape(4,3,1)
thirdObjectCorners=thirdObjectCorners.reshape(4,3,1)
CameraMatrix=np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) #Values found in CalibrationValues.txt
distortionCoefficients=np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Values found in Calibration Values.txt

distortionCoefficients=distortionCoefficients.reshape(5,1) #Needs to be this shape

heights=[[0,0],[0,0],[0,0]]
font = cv2.FONT_HERSHEY_SIMPLEX #Used for drawing text.
camera=0 #Will be used to test camera loading
if(len(sys.argv)<2): #If no arguments passed
	camera=cv2.VideoCapture(1) #Load the webcam
	filenames=[] #Don't give any filenames
else:
	filenames=glob.glob(sys.argv[1]) #Get the filenames from the command
	print(filenames) #Print them, 'cause why not?
exit=0 #Don't stop running yet
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
	heights[2]=heights[1]
	heights[1]=heights[0]
	heights[0]=[0,0]
	if(len(filenames)>0): #If we're running purely on files
		exit=1 #Make it quit when we're done with files
		filename=filenames.pop(0) #And get the first file in the list
		try: 
			img=cv2.imread(filename) #Read the image
		except:
			continue #Unless you can't. Then skip it.
	elif(camera): #If using webcam
		ret, img = camera.read() #Read from webcam
	else: #If things are weird, just quit
		break
	if(img==None): #Do make sure that there's an image
		break
	outimg=np.copy(img) #Copy the image. Not really needed, but can be nice long term
	#squares=computeFrameSquares(img)
	
	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	try:
		cv2.imshow('Threshold',ret) #Display the thresholded image
	except:
		#exit=1 #If that's not working, your screwed. Just give up now.
		pass
	dump,contours,hierarchy=cv2.findContours(ret,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) #Get contours in image in a list.
	contours.sort(key=cv2.contourArea,reverse=True) #Sort them by area. Trust me. Saves time because there are a ton of contours with 0 area.
	contour=0 #Iterator
	squares=[] #List of squares to add to.
	while(contour<len(contours) and cv2.contourArea(contours[contour])>1000): #Loop until area is too small or all are done
		newsquare=gridSquare(contours[contour])
		#print cv2.contourArea(contours[contour])
		epsilon = 0.01*cv2.arcLength(newsquare.contour,True) #Set up for simplifying contours
		newsquare.corners=cv2.approxPolyDP(newsquare.contour,epsilon,True) #Actually simplifying
		cv2.polylines(img,[newsquare.contour],True,(0,255,0)) #Draw it
		if(len(newsquare.corners)==4): #If the simplified version has 4 sides
			squares.append(newsquare)
			 #And mark it as a square
		elif(len(newsquare.corners)>=4):
			#one=(vecsub2(newsquare.corners[0],newsquare.corners[1]))
			#two=(vecsub2(newsquare.corners[2],newsquare.corners[3]))
			#angle=dot2(one, two)/(distance2(one)*distance2(two))
			#print("angle:")
			#print(angle)
			print("corner")
			print(newsquare.corners[0][0])
			print(newsquare.corners[1][0])
			sides=[]
			i=0
			while i<len(newsquare.corners):
				j=i+1
				while j<len(newsquare.corners):
					sides.append(vecsub2(newsquare.corners[i][0],newsquare.corners[j][0]))
					j=j+1
				i=i+1
			print("side")
			print(sides[0])
			ppairs=[]
			i=0
			while i<len(sides):
				j=i+1
				while j<len(sides):
					dotP =abs(dot2(sides[i],sides[j]))
					if(dotP >=1):
						pair=[sides[i],sides[j]]
						ppairs.append(pair)
						z=2
						#print(pair)
					j=j+1
				i=i+1
			i=0
			print("ppair")
			print(ppairs[0])
			
			#while i<len(ppairs):
				#print("pair")
				#print(ppairs[i])
				#i=i+1
			while i<len(ppairs):
				j=i+1 
				while j<len(ppairs):
					if((ppairs[i][0]in(ppairs[j])) and (ppairs[i][1]in(ppairs[j]))):
						z=0
						print("A good pair")
						newsquare.corners=ppairs[i]
						squares.append(newsquare)
						#print(ppairs[j])
					j=j+1 
				i=i+1



			#	one=(vecsub2(newsquare.corners[i],newsquare.corners[i+1]))
			#	
			#	j=0
			#	while j<len(newsquare.corners):
			#		two=(vecsub2(newsquare.corners[j],newsquare.corners[j+1]))
			#		angle=dot2(one, two)/(distance2(one)*distance2(two))
			#		if( angle >=0 & angle <= 5):
			#			cv2.polylines(img[newsquare.corners[i],newsquare.corners[i+2],newsquare.corners[j],newsquare.corners[j+1]],True,(255,255,255))
			#		j=j+1
			#	i=i+1
			#cv2.polylines(img,[newsquare.corners],True,(255,255,255))
		else:
			tempcorners = newsquare.corners		
			tempvecs = []			
			for indx in range(len(tempcorners)): #create a list of vectors
				newvec = [tempcorners[indx][0][0] - tempcorners[indx - 1][0][0], tempcorners[indx][0][1] - tempcorners[indx - 1][0][1]]
				tempvecs.append(newvec)
			maxcross = 0			
			for indx in range(len(tempvecs)):
				tempcross = cross2D(tempvecs[indx],tempvecs[indx-1])
				maxcross = max(maxcross, tempcross)
			area = cv2.contourArea(cv2.convexHull(newsquare.contour))			
			#print(maxcross,area)
			ratio = round(float(area)/maxcross,1)
			#print(area,ratio)
			newsquare.corners=cv2.approxPolyDP(newsquare.contour,epsilon/10,True) #Actually simplifying
			if 4.0 >= ratio > 1.3:
				cv2.polylines(img,[newsquare.corners],True,(0,0,255)) #Draw it
				#print newsquare.corners
				indx1=0
				while(indx1<len(newsquare.corners)):
					
					indx2=0
					a=[newsquare.corners[indx1][0][0],newsquare.corners[indx1][0][1],0]
					a1=[newsquare.corners[indx1-1][0][0],newsquare.corners[indx1-1][0][1],0]
					b=[]
					sort=[]
					while(indx2<len(newsquare.corners) and indx2!=indx1):
						b=[newsquare.corners[indx2][0][0],newsquare.corners[indx2][0][1],0]
						sort.append([math.asin(1-pow(dot(vecsub(b,a),vecsub(a1,a))/(distance(vecsub(b,a))*distance(vecsub(a1,a))),2)),indx2])
						indx2+=1
					sort.sort()
					#print sort
					i=-1
					count=0
					while(i>-len(sort)):
						#sort[i].append(sort[i][0]-sort[i-1][0])
						if(abs(sort[i][0])<0.01 and abs(sort[i][1]-indx1)>1):
							#print(sort[i],sort[i-1]) KELSEY COMMENTED
							
							b=[newsquare.corners[sort[i][1]][0][0],newsquare.corners[sort[i][1]][0][1],0]
							c=[newsquare.corners[sort[i-1][1]][0][0],newsquare.corners[sort[i-1][1]][0][1],0]
							#cv2.line(img,tuple(b[:2]),(int(a[0]),int(a[1])),(255,255,255)) #white
							#cv2.line(img,tuple(c[:2]),(int(a[0]),int(a[1])),(255,255,255)) #white 
							i=-len(sort)
						i-=1
					indx1+=1
			elif 2.9 >= ratio > 1.3:
				#print newsquare.corners
				pass
			elif 1.3 >= ratio > 0.6:
				contour+=1
				continue
				newsquare.corners=cv2.convexHull(newsquare.contour)
				newsquare.corners=cv2.approxPolyDP(newsquare.corners,epsilon,True) #Actually simplifying
				if(len(newsquare.corners)==4):
					#Case 1
					squares.append(newsquare)
				elif(len(newsquare.corners)==5):
					#Case 2
					cv2.polylines(img,[newsquare.corners],True,(255,0,0))
					temprect = cv2.minAreaRect(newsquare.corners)
					tempbox = cv2.boxPoints(temprect) #Perhaps this would work with a newer version of OpenCv
					tempbox = np.int0(tempbox)
					cv2.drawContours(img,[tempbox],0,(0,255,255),2)
					#print(box, "This is box")
					#print(newsquare.corners)
			else:
				pass
		contour+=1 #Iterate

	#print(contour,len(squares)) #Print the # of squares found
	#print(len(img),len(img[0]))
	for square in squares:
		square.getPosStats()
	index1=0 #Iterator1
	#print("")

	while(index1<len(squares)): #Loop through squares
		index2=0 #Iterator2 starts where 1 hasn't reached
		score=0
		while(index2<len(squares)): #And loops through squares
			squares[index1].compareSquareNormals(squares[index2])
			index2+=1 #Iterate
		index1+=1 #Iterate
	squares.sort(key=attrgetter('score'),reverse=True)
	if(len(squares)>0):
		averageheight=0
		scorethreshold=.95*squares[0].score
		tvecindex=0
		for square in [square for square in squares if square.score > scorethreshold]:

			#print(square.location)
			height=abs(square.location[2])
			#height=abs(dot(square.camvec,square.normal)/distance(square.normal))
			averageheight+=height
			x=0
			y=0
			for point in square.corners:
				x+=point[0][0]
				y+=point[0][1]
			x=int(x/4)
			y=int(y/4)
			cv2.putText(img,str(int(height))+" "+str(int(square.score*100)),(x,y), font, 1,(255,255,255),1,cv2.LINE_AA)
	
			cv2.polylines(img,[square.corners],True,(255,0,0)) #Draw both squares
			tvecindex+=1
		#print(len([square for square in squares if square.score > scorethreshold]))

		if(tvecindex!=0):
			averageheight=averageheight/tvecindex
			heights[0]=[averageheight,scorethreshold/.95]
			#cv2.putText(img,str(int(averageheight)),(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
		else:
			pass
			#cv2.putText(img,"N/A",(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
	else:
		cv2.putText(img,"N/A",(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
	print("") #Divider line
	weights=[.5,.3,.2]
	totalscore=weights[0]*heights[0][1]+weights[1]*heights[1][1]+weights[2]*heights[2][1]
	if(totalscore!=0):
		heights[0]=[(weights[0]*heights[0][1]*heights[0][0]+weights[1]*heights[1][1]*heights[1][0]+weights[2]*heights[2][1]*heights[2][0])/totalscore,totalscore]
		#cv2.putText(img,str(int(heights[0][0])),(60,60), font, 1,(255,255,255),1,cv2.LINE_AA)
	try:
		cv2.imshow("hi",img) #This is mainly to let my borked python3 install, which can't display images, work.
		if(camera): #If we're doing video
			if cv2.waitKey(1) & 0xFF == ord('q'): #Let the program run while waiting for q to be pressed
				break #Exit
		else: #If it's just files,
			cv2.waitKey(0) #Wait for a key to continue on
			cv2.destroyAllWindows() #And remove the old window
	except:
		pass
#cv2.destroyAllWindows() #And don't leave silly windows behind.
