import GridSquares as gs
import ColorDetect as cd


class SquaresGrid:
	def update_position(self, img):
		camToGridTransform=np.concatenate((cv2.transpose(rotMatrix[0]),camerapos),axis=1)
		gridToCamTransform=np.linalg.inv(np.concatenate((camToGridTransform,np.array([[0,0,0,1]])),axis=0))
		camRot=list(camToGridTransform.dot(np.array([0,0,1,0])))
		tempcamline2=grid.vecadd(grid.scalarmult(camRot,50),[birdsview.shape[0]/2,birdsview.shape[0]/2,0])
		cv2.line(birdsview,(int(tempcamline2[0]),int(tempcamline2[1])),(int(birdsview.shape[0]/2),int(birdsview.shape[1]/2)),(255,0,255),1,cv2.LINE_AA)


