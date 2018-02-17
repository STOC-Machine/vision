import cv2
import numpy as np
import math

def color_detect(image, hsv_lower_val, hsv_upper_val):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define range of color in HSV
    lower_color = np.array([hsv_lower_val,50,50])
    upper_color = np.array([hsv_upper_val,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_color, upper_color)

    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 20, 20, 2)

    if(type(lines) is not np.ndarray or lines.all() == None):
        print('No such lines')
        return 0

    merge_lines(lines)
    
#    for line in lines:
#        x1, y1, x2, y2 = line[0]
#        cv2.line(image, (x1,y1), (x2,y2), (0, 0, 0), 2)
#    cv2.imwrite('houghlines.jpg', image)

    return lines

def merge_lines(lines):
    slopes = []
    total_slope = 0

    x_min = lines[0][0][0]
    y_min = lines[0][0][1]
    x_max = lines[0][0][2]
    y_max = lines[0][0][3]
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2-y1)/(x2-x1)
        
        slopes.append(slope)
        total_slope += slope

        x_min = min(x_min, x1, x2)
        x_max = max(x_max, x1, x2)
        y_min = min(y_min, y1, y2)
        y_max = max(y_max, y1, y2)

    slope_ave = total_slope/len(slopes)

    length = math.sqrt((x_max-x_min)**2 + (y_max-y_min)**2)

#img = cv2.imread('green_line_dag_test.png', cv2.IMREAD_COLOR)
#red = 0, green = 60, blue = 120, max = 179
#color_detect(img, 40, 80)
