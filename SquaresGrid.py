import numpy as np

import color_detect as cd
import GridSquares as gs


def find_color_line(img):
	"""
	:param img:
	"""

	red_values = (0, 20)
	green_values = (40, 80)

	red_lines = cd.color_detect(img, red_values[0], red_values[1])
	green_lines = cd.color_detect(img, green_values[0], red_values[1])

	if type(red_lines) is np.ndarray and red_lines.all() is not None:
		return red_lines, "r"
	elif type(red_lines) is np.ndarray and red_lines.all() is not None:
		return green_lines, "g"
	return None


def find_edge(img):
	return None


def initialize(img):
	"""
	:param img:
	"""

	color_lines, color = find_color_line(img)
	edges = find_edge(img)

	if edges.length == 2:
		corner_initialize(img)
	elif color is not None:
		color_edge_initialize(img)
	elif edges is not None:
		non_color_edge_initialize(img)


def corner_initialize(img):
	return None


def color_edge_initialize(img):
	return None


def non_color_edge_initialize(img):
	return None
>>>>>>> 56173e1fcad6e00d22e217c81e186b6874aa22c7
