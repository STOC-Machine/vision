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

def update_position(previous_squares, current_squares, previous_position):

	#Delete all of this. Switch to minimizing cost function, where cost function is the distance between squares

	#I first go through all vectors between squares and find the minumum from each of the previous squares
	min_distances_vectors = []

	for ps in previous_squares:
		min_dist_vec = 0
		min_cs = None

		#I am assuming square does not have the same distance from 2 previous squares
		for cs in current_squares:
			dist_vector = compare_two_squares(ps, cs)
			min_temp = min(min_dist, np.linalg.norm(dist_vector))

			if not min_temp == np.linalg.norm(min_dist_vec):
				min_dist_vec = dist_vector
				min_cs = cs

		min_distances_vectors.append(min_dist_vec)

	#If there are different numbers of squares previous_squares and current_squares, I have to get rid of all the extra
	difference = min(0, previous_squares.length - current_squares.length)

	for i in range(difference):
		max_item = None
		for dist_tuple in min_distances_vectors:
			if max_item is None or np.linalg.norm(dist_tuple[0]) > np.linalg.norm(max_item[0]):
				max_item = dist_tuple

		if max_item is not None:
			min_distances_vectors.remove(max_item)

	avg_dist_vector = []
	for dist_tuple in min_distances_vectors:
		for i in range(avg_dist_vector.length):
			avg_dist_vector[i] += dist_tuple[i]

	for i in range(avg_dist_vector.length):
		avg_dist_vector[i] /= min_distances_vectors.length

	return avg_dist_vector

# return vector distance between centers of squares
def compare_two_squares(s_1, s_2):
	return [1,1]

