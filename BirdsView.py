import cv2
import sys
import numpy as np
import glob
import GridSquares as grid

#CameraMatrix=np.array([[376.60631072, 0., 334.94985263], [0., 376.37590044, 245.47987032], [0., 0., 1.]])
CameraMatrix=np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) # Logitech values found in CalibrationValues.txt
#distortionCoefficients=np.array([-3.30211385e-01, 1.58724644e-01, -1.87573090e-04, 4.55691783e-04, -4.98096761e-02])
distortionCoefficients=np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Logitech values found in Calibration Values.txt
distortionCoefficients=distortionCoefficients.reshape(5,1) #Needs to be this shape


font = cv2.FONT_HERSHEY_SIMPLEX #Used for drawing text.
camera=0 #Will be used to test camera loading
if(len(sys.argv)<2): #If no arguments passed
	camera=cv2.VideoCapture(0) #Load the webcam
	filenames=[] #Don't give any filenames
else:
	filenames=glob.glob(sys.argv[1]) #Get the filenames from the command
	print(filenames) #Print them, 'cause why not?
exit=0 #Don't stop running yet

BestCamRotGuess=0
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
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
	if(type(img) is not np.ndarray): #Do make sure that there's an image
		break
	img=cv2.undistort(img,CameraMatrix,distortionCoefficients)
	outimg=np.copy(img) #Copy the image. Not really needed, but can be nice long term
	#print img.shape
	birdsview=np.zeros([1000,1000,3],dtype=np.uint8)
	cv2.circle(birdsview,(int(birdsview.shape[0]/2),int(birdsview.shape[1]/2)),5,(255,255,0),-1)
	squares,BestCamRotGuess=grid.getSquareStats(img,CameraMatrix,np.array([[]]),BestCamRotGuess) #It's a magic function! Yay!
	#print(contour,len(squares)) #Print the # of squares found
	#print(len(img),len(img[0]))
	gluedSquareCorners=[]
	gluedSquareCoords=[]
	squarelength=28.5
	squareGap=2
	baseobjectpoints=[[-squarelength/2,-squarelength/2,0],[-squarelength/2,squarelength/2,0],[squarelength/2,squarelength/2,0],[squarelength/2,-squarelength/2,0]]
	if(BestCamRotGuess!=0):
		tempcamline=grid.vecadd(grid.scalarmult(BestCamRotGuess,50),[birdsview.shape[0]/2,birdsview.shape[0]/2,0])
		cv2.line(birdsview,(int(tempcamline[0]),int(tempcamline[1])),(int(birdsview.shape[0]/2),int(birdsview.shape[1]/2)),(0,0,255),1,cv2.LINE_AA)
	for square in squares:
		tempvec=grid.vecsub(square.location,squares[0].location)
		INeedAnIndex=0
		while(INeedAnIndex<4):
			tempdrawvec=grid.vecadd(square.location,baseobjectpoints[INeedAnIndex])
			tempdrawvec2=grid.vecadd(square.location,baseobjectpoints[INeedAnIndex-1])
			INeedAnIndex+=1
			cv2.line(birdsview,(int(tempdrawvec[0]+birdsview.shape[0]/2),int(tempdrawvec[1]+birdsview.shape[1]/2)),(int(tempdrawvec2[0]+birdsview.shape[0]/2),int(tempdrawvec2[1]+birdsview.shape[1]/2)),(255,255,255),3,cv2.LINE_AA)
		tempvec[0]=(squarelength+squareGap)*round(tempvec[0]/(squarelength+squareGap),0)
		tempvec[1]=(squarelength+squareGap)*round(tempvec[1]/(squarelength+squareGap),0)
		tempvec[2]=0
		for i in baseobjectpoints:
			gluedSquareCoords.append([[grid.vecadd(i,tempvec)[0]],[grid.vecadd(i,tempvec)[1]],[grid.vecadd(i,tempvec)[2]]])
		for i in grid.denumpify(square.corners):
			gluedSquareCorners.append([[i[0]],[i[1]]])
		#print tempvec
		#print(square.location)
		x=0
		y=0
		for point in square.corners:
			x+=point[0][0]
			y+=point[0][1]
		x=int(x/4)
		y=int(y/4)
		cv2.putText(img,str(int(abs(square.location[2])))+" "+str(int(square.score*100)),(x,y), font, 1,(255,255,255),1,cv2.LINE_AA)

		cv2.polylines(img,[square.corners],True,(255,0,0)) #Draw both squares
		#print square.location
		#print square.side1
		cv2.drawContours(img,square.contour,True,(0,255,0))
		
		#print(len([square for square in squares if square.score > scorethreshold]))
	if(len(squares)>0):
		gluedSquareCorners=np.asarray(gluedSquareCorners).astype(float)
		gluedSquareCoords=np.asarray(gluedSquareCoords).astype(float)
		gluedSquareCorners.reshape(len(gluedSquareCorners),2,1)
		gluedSquareCoords.reshape(len(gluedSquareCoords),3,1)
		#for square2 in squares:
			#print square2.corners
		#for square2 in squares:
			#print grid.vecsub(square2.location,squares[0].location)
		#print gluedSquareCorners
		#print gluedSquareCoords
		inliers,fullrvec,fulltvec=cv2.solvePnP(gluedSquareCoords,gluedSquareCorners,CameraMatrix,distortionCoefficients,squares[0].rvec,squares[0].tvec,True) #Where the magic happens. Turns gets vector from camera to center of square
		#print fulltvec,fullrvec
		rotMatrix=cv2.Rodrigues(fullrvec)
		camerapos=np.multiply(cv2.transpose(rotMatrix[0]), -1).dot(fulltvec)
		print(camerapos)
		print(squares[0].location)
		camToGridTransform=np.concatenate((cv2.transpose(rotMatrix[0]),camerapos),axis=1)
		gridToCamTransform=np.linalg.inv(np.concatenate((camToGridTransform,np.array([[0,0,0,1]])),axis=0))
		camRot=list(camToGridTransform.dot(np.array([0,0,1,0])))
		tempcamline2=grid.vecadd(grid.scalarmult(camRot,50),[birdsview.shape[0]/2,birdsview.shape[0]/2,0])
		cv2.line(birdsview,(int(tempcamline2[0]),int(tempcamline2[1])),(int(birdsview.shape[0]/2),int(birdsview.shape[1]/2)),(255,0,255),1,cv2.LINE_AA)
	print("") #Divider line
	try:
		cv2.imshow("hi",img) #This is mainly to let my borked python3 install, which can't display images, work.
		cv2.imshow("Birds eye view",birdsview)
		if(camera): #If we're doing video
			if(len(squares)>0):
				BestCamRotGuess=squares[0].camRot
			if cv2.waitKey(1) & 0xFF == ord('q'): #Let the program run while waiting for q to be pressed
				break #Exit
		else: #If it's just files,
			BestCamRotGuess=0
			cv2.waitKey(0) #Wait for a key to continue on
			cv2.destroyAllWindows() #And remove the old window
	except:
		pass
#cv2.destroyAllWindows() #And don't leave silly windows behind.