import cv2
import sys
import numpy as np
import glob

FONT = cv2.FONT_HERSHEY_SIMPLEX  # Used for drawing text.

#camera_matrix=np.array([[376.60631072, 0., 334.94985263], [0., 376.37590044, 245.47987032], [0., 0., 1.]])
camera_matrix = np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) # Logitech values found in CalibrationValues.txt
#distortion_coefficients=np.array([-3.30211385e-01, 1.58724644e-01, -1.87573090e-04, 4.55691783e-04, -4.98096761e-02])
distortion_coefficients = np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Logitech values found in Calibration Values.txt
distortion_coefficients = distortion_coefficients.reshape(5, 1) #Needs to be this shape


def find_grid(img, cam_rot_guess):
    """
    Takes a distorted image and a camera rotation guess and finds the position
    of the camera relative to the grid, as well as identifying all visible
    squares in the grid.
    :param img: The image to process
    :param cam_rot_guess:
    :return:
    """

    img = cv2.undistort(img, camera_matrix, distortion_coefficients)

    birds_view = np.zeros([1000, 1000, 3], dtype=np.uint8)
    cv2.circle(birds_view,
               (int(birds_view.shape[0] / 2), int(birds_view.shape[1] / 2)), 5,
               (255, 255, 0), -1)
    squares, cam_rot_guess = grid.get_square_stats(img, camera_matrix,
                                                   np.array([[]]),
                                                   cam_rot_guess)

    # print(contour,len(squares)) #Print the # of squares found
    # print(len(img),len(img[0]))

    glued_square_corners = []
    glued_square_coords = []
    square_length = 28.5
    square_gap = 2
    base_object_points = [[-square_length / 2, -square_length / 2, 0],
                          [-square_length / 2, square_length / 2, 0],
                          [square_length / 2, square_length / 2, 0],
                          [square_length / 2, -square_length / 2, 0]]
    if cam_rot_guess != 0:
        temp_cam_line = grid.vec_add(grid.scalar_mult(cam_rot_guess, 50),
                                     [birds_view.shape[0] / 2,
                                     birds_view.shape[0] / 2, 0])
        cv2.line(birds_view, (int(temp_cam_line[0]), int(temp_cam_line[1])),
                 (int(birds_view.shape[0] / 2), int(birds_view.shape[1] / 2)),
                 (0, 0, 255), 1, cv2.LINE_AA)
    for square in squares:
        temp_vec = grid.vec_sub(square.location, squares[0].location)

        for edge_index in range(4):
            temp_draw_vec = grid.vec_add(square.location,
                                         base_object_points[edge_index])
            temp_draw_vec2 = grid.vec_add(square.location,
                                          base_object_points[edge_index - 1])
            cv2.line(birds_view, (
            int(temp_draw_vec[0] + birds_view.shape[0] / 2),
            int(temp_draw_vec[1] + birds_view.shape[1] / 2)),
                     (int(temp_draw_vec2[0] + birds_view.shape[0] / 2),
                      int(temp_draw_vec2[1] + birds_view.shape[1] / 2)),
                     (255, 255, 255), 3, cv2.LINE_AA)

        temp_vec[0] = (square_length + square_gap) * round(
            temp_vec[0] / (square_length + square_gap), 0)
        temp_vec[1] = (square_length + square_gap) * round(
            temp_vec[1] / (square_length + square_gap), 0)
        temp_vec[2] = 0

        for i in base_object_points:
            glued_square_coords.append(
                [[grid.vec_add(i, temp_vec)[0]], [grid.vec_add(i, temp_vec)[1]],
                 [grid.vec_add(i, temp_vec)[2]]])

        for i in grid.denumpify(square.corners):
            glued_square_corners.append([[i[0]], [i[1]]])

        # print temp_vec
        # print(square.location)

        x = 0
        y = 0
        for point in square.corners:
            x += point[0][0]
            y += point[0][1]
        x = int(x / 4)
        y = int(y / 4)
        cv2.putText(img, str(int(abs(square.location[2]))) + ' ' + str(
            int(square.score * 100)), (x, y), FONT, 1, (255, 255, 255), 1,
                    cv2.LINE_AA)

        cv2.polylines(img, [square.corners], True,
                      (255, 0, 0))  # Draw both squares
        # print square.location
        # print square.side1
        cv2.drawContours(img, square.contour, True, (0, 255, 0))

        # print(len([square for square in squares if square.score > scorethreshold]))
    if len(squares) > 0:
        glued_square_corners = np.asarray(glued_square_corners).astype(float)
        glued_square_coords = np.asarray(glued_square_coords).astype(float)
        glued_square_corners.reshape(len(glued_square_corners), 2, 1)
        glued_square_coords.reshape(len(glued_square_coords), 3, 1)

        # for square2 in squares:
        # print square2.corners
        # for square2 in squares:
        # print grid.vecsub(square2.location,squares[0].location)
        # print glued_square_corners
        # print glued_square_coords

        # Where the magic happens. Turns gets vector from camera to center of square
        inliers, full_r_vec, full_t_vec = cv2.solvePnP(glued_square_coords,
                                                       glued_square_corners,
                                                       camera_matrix,
                                                       distortion_coefficients,
                                                       squares[0].rvec,
                                                       squares[0].tvec, True)
        # print full_t_vec,full_r_vec
        rot_matrix = cv2.Rodrigues(full_r_vec)
        camera_pos = np.multiply(cv2.transpose(rot_matrix[0]), -1).dot(
            full_t_vec)
        print(camera_pos)
        print(squares[0].location)

        cam_to_grid_transform = np.concatenate(
            (cv2.transpose(rot_matrix[0]), camera_pos), axis=1)
        grid_to_cam_transform = np.linalg.inv(
            np.concatenate((cam_to_grid_transform, np.array([[0, 0, 0, 1]])),
                           axis=0))
        cam_rot = list(cam_to_grid_transform.dot(np.array([0, 0, 1, 0])))
        temp_cam_line2 = grid.vec_add(grid.scalar_mult(cam_rot, 50),
                                      [birds_view.shape[0] / 2,
                                      birds_view.shape[0] / 2, 0])
        cv2.line(birds_view, (int(temp_cam_line2[0]), int(temp_cam_line2[1])),
                 (int(birds_view.shape[0] / 2), int(birds_view.shape[1] / 2)),
                 (255, 0, 255), 1, cv2.LINE_AA)

    return squares, img, birds_view


def run_from_camera(camera):
    """
    Run bird's view from camera input.
    :param camera: the cv2 camera file handle
    :return: nothing
    """

    cam_rot_guess = 0

    # Run until q is pressed
    while cv2.waitKey(1) & 0xFF != ord('q'):
        ret, img = camera.read()

        if type(img) is not np.ndarray:
            print('Error: image did not read properly, skipping')
            continue

        squares, img, birds_view = find_grid(img, cam_rot_guess)
        cv2.imshow("Squares", img)
        cv2.imshow("Birds eye view", birds_view)

        if len(squares) > 0:
            cam_rot_guess = squares[0].cam_rot


def run_from_files(files):
    """
    Run bird's view from file input.
    :param files: a directory/filename with wildcards
    :return: nothing
    """
    files = glob.glob(files)

    while len(files) > 0:
        file = files.pop(0)
        img = cv2.imread()

        if img is None:
            print('Error: could not read image file {}, skipping.'.format(file))
            continue

        squares, img, birds_view = find_grid(img, 0)
        cv2.imshow("Squares", img)
        cv2.imshow("Birds eye view", birds_view)

        # Wait for keypress to continue, close old windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Use /dev/video0 by default. Change from 0 if using different /video
        run_from_camera(cv2.VideoCapture(0))
    else:
        run_from_files(sys.argv[1])
