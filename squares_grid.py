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
	return None

def frame_difference(previous_squares, current_squares):
	# Matching always has to go from less squares to more
	if len(previous_squares) <= len(current_squares):
		domain = previous_squares
		codomain = current_squares
		flipped = False
	else:
		domain = current_squares
		codomain = previous_squares
		flipped = True

	# Used to name each square to keep track of which is which
	ps_name = 0
	cs_name = 0

	matching_distances = {}
	final_matching = {}

	# This double for loop finds distance between every square in domain and every square in codomain
	for ps in domain:
		ps_matching = [:]
		ps.name = str(ps_name)

		first_match = None

		for cs in codomain:
			if not cs.name:
				cs.name = str(cs_name)
				cs_name += 1

			dist = np.linalg.norm(vec_distance(ps, cs))
			ps_matching[cs.name] = dist

			if first_match == None or first_match[1] > dist:
				first_match = (cs.name, dist)

		matching_distances[ps.name] = ps_matching
		final_matching[ps.name] = first_match
		ps_name += 1

	overlaps = None
	overlap = None

	for i in Range(len(final_matching)):
		for j in Range(i+1, len(final_matching)):
			if final_matching[i][0] == final_matching[j][0]:
				overlap = True
				overlaps = (final_matching[i], final_matching[j])

	if overlaps == None:
		overlaps = False

	while overlaps:
		overlapping_match = final_matching[overlap[0]]

		dist_list_1 = matching_distances[overlap[0]]
		dist_list_2 = matching_distances[overlap[1]]

		next_best_1 = None
		next_best_2 = None

		for cs in codomain:


			 



	for ps in matching_distances:
		ps_list = matching_distances[ps]
		match = None
		for cs in ps_list:
			if match = None or ps_list[cs] < match[1]:
				match = (cs, ps_list[cs])





# return vector distance between centers of squares
def vec_distance(square_1, square_2):
	corner_1 = get_bottom_left_corner(square_1)
	corner_2 = get_bottom_left_corner(square_2)

	return corner_2[0] - corner_1[0], corner_2[1] - corner_1[1]

def get_bottom_left_corner(square):
	lowest_corner = None

	for corner in square.corners:
		if lowest_corner == None or corner[1] < lowest_corner[1]:
			lowest_corner = corner
		elif corner[1] == lowest_corner[1]:
			if corner[0] < lowest_corner[0]:
				lowest_corner = corner

	return lowest_corner
