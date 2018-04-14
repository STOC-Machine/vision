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
  #red,green,blue=cv2.split(img) #split the image into components.
  #testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
  #testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
  print(img.dtype)
  print(img.shape)
  cv2.imshow("before", img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  #3ret,img=cv2.threshold(img,120,255,cv2.THRESH_BINARY_INV)
  print(img.dtype)
  print(img.shape)

  # print(out[0][0])
  #try:
  #print(ret)
  i=0
  j=0
  z=0

  #cv2.imshow('Threshold',out) #Display the thresholded image


  # cv2.waitKey(0)
  # cv2.destroyAllWindows()
  #except:
  #  pass
  lines = cv2.HoughLinesP(img, 1, np.pi/180, 25, 75, 10)
  #lines = cv2.HoughLinesP(img, 1, np.pi/180, 200, 200, 100)

  #lines = cv2.cornerHarris(out, out, ksize, k[, dst[, borderType]])
  if lines == None:
    return []
  for line in lines:
          x1, y1, x2, y2 = line[0]
          cv2.line(img, (x1,y1), (x2,y2), 160, 10)
  cv2.imwrite('houghlines.jpg', img)
  cv2.imshow('houghlines.jpg', img)
  # print(lines)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
 
  return lines
  #try: 

  #except:
    #pass 
#following the sodoku website 
#http://aishack.in/tutorials/sudoku-grabber-opencv-detection/
def grid_detect(img):
  red,green,blue=cv2.split(img) #split the image into components.
  testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
  testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
  ret,out=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY_INV)
  sudoku = out
  outerBox = np.zeros((256, 256, 1), dtype = "uint8")
  kernel = np.zeros((3,3,1), dtype = "uint8")
  #kernel(0,0) = 0; 
  sudoku = cv2.GaussianBlur(sudoku,(11,11),0)
  kernel = np.ones((5,5),np.uint8)
  dilation = cv2.dilate(sudoku,kernel,iterations = 1)
  dilation = cv2.Canny(dilation,100,200)
  cv2.imshow("dilation.jpg", dilation)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  return dilation
  

  '''blob detection attempt '''

  # # Set up the detector with default parameters.
  # detector = cv2.SimpleBlobDetector_create()
   
  # # Detect blobs.
  # keypoints = detector.detect(dilation)
   
  # # Draw detected blobs as red circles.
  # # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
  # im_with_keypoints = cv2.drawKeypoints(dilation, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
   
  # # Show keypoints
  # cv2.imshow("Keypoints", im_with_keypoints)
  # cv2.waitKey(0)


'''blob detection attempt '''


  # # Setup SimpleBlobDetector parameters.
  # params = cv2.SimpleBlobDetector_Params()
  # # Change thresholds
  # params.minThreshold = 10
  # params.maxThreshold = 200
  # # Filter by Area.
  # params.filterByArea = True
  # params.minArea = 1500
  # # Filter by Circularity
  # params.filterByCircularity = True
  # params.minCircularity = 0.1
  # # Filter by Convexity
  # params.filterByConvexity = True
  # params.minConvexity = 0.87
  # # Filter by Inertia
  # params.filterByInertia = True
  # params.minInertiaRatio = 0.01
  # # Create a detector with the parameters
  # detector = cv2.SimpleBlobDetector(params)
  # # Detect blobs.
  # keypoints = detector.detect(im)
  # # Draw detected blobs as red circles.
  # # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
  # # the size of the circle corresponds to the size of blob
  # im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  # # Show blobs
  # cv2.imshow("Keypoints", im_with_keypoints)
  # cv2.waitKey(0)


  # cv2.imshow("dilation.jpg", dilation)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()
  # return dilation




BestCamRotGuess=0
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
  if(len(filenames)>0): #If we're running purely on files
      exit=1 #Make it quit when we're done with files
      filename=filenames.pop(0) #And get the first file in the list
      #try: 
      img=cv2.imread(filename, cv2.IMREAD_COLOR) #Read the image
      print(img)
      makeHoughLines(grid_detect(img))
      #grid_detect(img)
        #print('asdfasdf')
      #except:
        #print(';lkj;lkj;lkj')
        #continue #Unless you can't. Then skip it.
  else: #If things are weird, just quit
    break
  if(img==None): #Do make sure that there's an image
    break 
  img = cv2.undistort(img,CameraMatrix,distortionCoefficients)

