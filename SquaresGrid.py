import cv2 
import numpy as np 
import math 
import GridSquares as grid 
import color_detect as cd 
#finding position on the grid
def initialize_pos(img)
#initial position must
#be on the green line 
#be the corner square, aka on the edge 
#if the conditions are met define location of the drone as (0,0)
	color_lines = color_detect(img, 83, 151)
	if(color_lines == 0):#if no lines found
		return "not at the start"
	if(color_lines>1):
	#error?
	if(color_lines == 1):
		#if(we see an edge)
			#if(we see a corner)
			#this spot is (0,0)