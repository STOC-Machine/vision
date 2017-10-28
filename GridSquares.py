import numpy as np
import cv2
import sys
import glob
from operator import attrgetter
import math

def dot(a,b):#a.b
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def vecsub(a,b):#a-b
	return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]
def vecadd(a,b): #a+b
	return [a[0]+b[0],a[1]+b[1],a[2]+b[2]]
def distance(a): #magnitude a
	return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
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
def denumpify(a): #This is terrible long term. But it works for now!
	return [[a[0][0][0],a[0][0][1]],[a[1][0][0],a[1][0][1]],[a[2][0][0],a[2][0][1]],[a[3][0][0],a[3][0][1]]]

def computeFrameSquares(img):
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
	camRot=None #Rotation Vector of Camera
	normal=[] #Normal vector pointing out of the square	
	rvec=None
	camerapos=None
	score=0 #How good is this square. See compare square normals for more
	corners=[] #Image coordinates of square corners
	contour=None #Unsimplified image coordinates of square corners
	location=[] #Square location in camera coordinates
	def getPosStats(self,CameraMatrix,distortionCoefficients,objectpoints):
		camvalues=[]
		#print self.corners
		tempcorners=self.corners.reshape(4,2,1).astype(float) #The points need to be floats, and in a specific shape
		#print tempcorners,objectpoints
		#print objectpoints.shape,tempcorners.shape
		inliers,self.rvec,tvec=cv2.solvePnP(objectpoints,tempcorners,CameraMatrix,distortionCoefficients) #Where the magic happens. Turns gets vector from camera to center of square
		rotMatrix=cv2.Rodrigues(self.rvec)
		camerapos=np.multiply(cv2.transpose(rotMatrix[0]), -1).dot(tvec)
		camToGridTransform=np.concatenate((cv2.transpose(rotMatrix[0]),camerapos),axis=1)
		gridToCamTransform=np.linalg.inv(np.concatenate((camToGridTransform,np.array([[0,0,0,1]])),axis=0))
		self.camRot=list(camToGridTransform.dot(np.array([0,0,1,0])))
		self.normal=gridToCamTransform.dot(np.array([0,0,1,0]))
		#print self.normal
		self.camerapos=camerapos
		self.location=[camerapos[0][0],camerapos[1][0],camerapos[2][0]]

	def alignSquares(self,guess,CameraMatrix,distortionCoefficients,objectpoints):
		alignmentvals=[0,0,0,0]
		alignmentvals[0]=dot(self.camRot,guess)
		for rot in range(1,4):
			tempcorners=np.roll(self.corners,rot,axis=0)
			tempcorners=tempcorners.reshape(4,2,1).astype(float)
			inliers,self.rvec,tvec=cv2.solvePnP(objectpoints,tempcorners,CameraMatrix,distortionCoefficients) #Where the magic happens. Turns gets vector from camera to center of square
			rotMatrix=cv2.Rodrigues(self.rvec)
			camerapos=np.multiply(cv2.transpose(rotMatrix[0]), -1).dot(tvec)
			camToGridTransform=np.concatenate((cv2.transpose(rotMatrix[0]),camerapos),axis=1)
			gridToCamTransform=np.linalg.inv(np.concatenate((camToGridTransform,np.array([[0,0,0,1]])),axis=0))
			alignmentvals[rot]=dot(list(camToGridTransform.dot(np.array([0,0,1,0]))),guess)
		#print alignmentvals,alignmentvals.index(max(alignmentvals))
		#print self.corners
		#print self.location
		self.corners=np.roll(self.corners,alignmentvals.index(max(alignmentvals)),axis=0)
		#print self.corners
		self.getPosStats(CameraMatrix,distortionCoefficients,objectpoints)

	def compareSquareNormals(self,square,dim):
		tempcross=cross(self.normal,square.normal)
		edge=0
		print dim
		for point in square.corners:
			if(point[0][0]<1 or point[0][0]>dim[1]-2 or point[0][1]<1 or point[0][1]>dim[0]-2):
				edge=1
		if(not edge):
			#score+=abs(dot(cross1,cross2))
			self.score+=1-abs(distance(tempcross)/(distance(square.normal)*distance(self.normal)))
	def __init__(self,contour):
		self.contour=contour

def getSquareStats(img,CameraMatrix,distortionCoefficients,BestCamRotGuess):
	squarelength=28.5 #Needs to be a float, in cm of real length of the squares
	squareGap=2.5
	objectpoints=np.array([[[-squarelength/2,-squarelength/2,0]],[[-squarelength/2,squarelength/2,0]],[[squarelength/2,squarelength/2,0]],[[squarelength/2,-squarelength/2,0]]],np.float32) #3d grid square coordinates
	objectpoints=objectpoints.reshape(4,3,1) #Needs to be this shape
	squares=computeFrameSquares(img)
	for square in squares:
		square.getPosStats(CameraMatrix,distortionCoefficients,objectpoints)
	index1=0
	while(index1<len(squares)):
		index2=0
		while(index2<len(squares)):
			squares[index1].compareSquareNormals(squares[index2],img.shape)
			index2+=1
		index1+=1
	squares.sort(key=attrgetter('score'),reverse=True)
	if(len(squares)>0):
		scorethreshold=max(.95*squares[0].score,1.0)
		squares=list(filter(lambda x:x.score>scorethreshold,squares))
	for square in squares:
		if(BestCamRotGuess==0):
			BestCamRotGuess=squares[0].camRot
		square.alignSquares(BestCamRotGuess,CameraMatrix,distortionCoefficients,objectpoints)
	return squares,BestCamRotGuess

