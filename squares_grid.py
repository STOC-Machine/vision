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
	matchings, flipped = frame_matching(previous_squares, current_squares)
	matchings = remove_bad_matchings(matchings)


	if not flipped:
		vector_dist = vector_dist_between_frames(previous_squares, current_squares, matchings)
	else:
		vector_dist = vector_dist_between_frames(current_squares, previous_squares, matchings)

	return np.array(previous_position) + np.array(vector_dist)

def vector_dist_between_frames(previous_squares, current_squares, matchings):
        #in the future distinguish between no matchings and distance of 0
        if(len(matchings) == 0):
            return [0,0]

	vector_list = []
	
	for ps in previous_squares:
                if ps.name in matchings:
		        matched_square_name = matchings[ps.name][0]
                else:
                        continue

		for cs in current_squares:
			if matched_square_name == cs.name:
				vector_list.append(vec_distance(ps, cs))
        vector_sum = np.zeros((1,2))
        for vector in vector_list:
            vector_sum += vector
        return vector_sum / len(vector_list)


def remove_bad_matchings(matchings):
	for key in matchings.keys():
	    if matchings[key][1] >= 50:
		del matchings[key]

	return matchings

def frame_matching(previous_squares, current_squares):
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
	# Each name is a number value in a string
	ps_name = 0
	cs_name = 0

	matching_distances = {}
	final_matching = {}

	# This double for loop finds distance between every square in domain and every square in codomain
	for ps in domain:
		ps_matching = {}
		ps.name = str(ps_name)

		# First match is the smallest distance (optimal) without considering overlap
		# First match is a tuple that has the (name, distance)
		first_match = None

		for cs in codomain:
			if not cs.name:
				cs.name = str(cs_name)
				cs_name += 1

			# Find the distance & save it to dictionary
			dist = np.linalg.norm(vec_distance(ps, cs))
			ps_matching[cs.name] = dist

			if first_match == None or first_match[1] > dist:
				first_match = (cs.name, dist)

		matching_distances[ps.name] = ps_matching
		final_matching[ps.name] = first_match
		ps_name += 1

	# Boolean whether there are overlaps in final_matching and names of square in the domain that will be replaced
	overlaps, overlap_target = check_for_overlap(final_matching)

	while overlaps:
                for tester in final_matching:
		    overlap_target_current_match = final_matching[overlap_target][0]
		del matching_distances[overlap_target][overlap_target_current_match]

		target_distance_dictionary = matching_distances[overlap_target]

		next_best = None
		for key in target_distance_dictionary:
			if next_best == None or next_best[1] > target_distance_dictionary[key]:
				next_best = (key, target_distance_dictionary[key])

		if next_best == None:
			del final_matching[overlap_target]
		else:
			final_matching[overlap_target] = next_best

		overlaps, overlap_target = check_for_overlap(final_matching)


	return final_matching, flipped


def check_for_overlap(matching_dictionary):
	overlap_target = None

        for key_1 in matching_dictionary:
            for key_2 in matching_dictionary:
                if not key_1 == key_2 and matching_dictionary[key_1][0] == matching_dictionary[key_2][0]:
                    conflict_1 = matching_dictionary[key_1]
                    conflict_2 = matching_dictionary[key_2]


                    if conflict_1[1] > conflict_2[1]:
                        overlap_target = key_1
                    else:
                        overlap_target = key_2

                    return True, overlap_target
                        
	return False, None

# return vector distance between centers of squares
def vec_distance(square_1, square_2):
	corner_1 = get_bottom_left_corner(square_1)
	corner_2 = get_bottom_left_corner(square_2)

	return corner_2 - corner_1

def get_bottom_left_corner(square):
	lowest_corner = None

	for corner in square.corners:
		if type(lowest_corner) is not np.ndarray or corner[0][1] < lowest_corner[0][1]:
			lowest_corner = corner
		elif corner[0][1] == lowest_corner[0][1]:
			if corner[0][0] < lowest_corner[0][0]:
				lowest_corner = corner

	return lowest_corner
