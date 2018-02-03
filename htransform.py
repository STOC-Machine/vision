import cv2
import sys
import numpy as np
import math
import glob
#CameraMatrix=np.array([[376.60631072, 0., 334.94985263], [0., 376.37590044, 245.47987032], [0., 0., 1.]])
CameraMatrix=np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) # Logitech values found in CalibrationValues.txt
#distortionCoefficients=np.array([-3.30211385e-01, 1.58724644e-01, -1.87573090e-04, 4.55691783e-04, -4.98096761e-02])
distortionCoefficients=np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Logitech values found in Calibration Values.txt
distortionCoefficients=distortionCoefficients.reshape(5,1) #Needs to be this shape


filenames=glob.glob(sys.argv[1])
exit=0 #Don't stop running yet
def makeHoughLines(img):
  # print('asdfasdf')
  red,green,blue=cv2.split(img) #split the image into components.
  testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
  testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
  ret,out=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY)
  # print(out[0][0])
  #try:
  #print(ret)
  i=0
  j=0
  z=0
  #cv2.imshow('Threshold',out) #Display the thresholded image
  while i<len(out):
    while j<len(out[i]):
      if(out[i][j] == 0):
        out[i][j]=255
      elif(out[i][j]== 255):
        out[i][j]=0
      else:
        out[i][j]=255
      print(out[i][j])
      j=j+1
    i=i+1
  cv2.imshow('Threshold',out) #Display the thresholded image


  # cv2.waitKey(0)
  # cv2.destroyAllWindows()
  #except:
  #  pass
  lines = cv2.HoughLinesP(out, 1, np.pi/180, 875, 10, 120)
  #lines = cv2.cornerHarris(out, out, ksize, k[, dst[, borderType]])
  for line in lines:
          x1, y1, x2, y2 = line[0]
          cv2.line(out, (x1,y1), (x2,y2), 160, 2)
  cv2.imwrite('houghlines.jpg', out)
  cv2.imshow('houghlines.jpg', out)
  # print(lines)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
 
  return lines
  #try: 

  #except:
    #pass 

BestCamRotGuess=0
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
  if(len(filenames)>0): #If we're running purely on files
      exit=1 #Make it quit when we're done with files
      filename=filenames.pop(0) #And get the first file in the list
      #try: 
      img=cv2.imread(filename) #Read the image
      makeHoughLines(img)
        #print('asdfasdf')
      #except:
        #print(';lkj;lkj;lkj')
        #continue #Unless you can't. Then skip it.
  else: #If things are weird, just quit
      break
  if(img==None): #Do make sure that there's an image
    break33
  img=cv2.undistort(img,CameraMatrix,distortionCoefficients)


