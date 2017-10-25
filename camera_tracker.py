import numpy as np
import cv2
import os
import pickle

LOWER_IR = np.array([0,20,200])
UPPER_IR = np.array([180,255,255])
FILENAME = 'calMatrix.p'
BASE_DIR = os.path.dirname(os.path.realpath(__name__))

class CameraTracker:
    cx = None
    cy = None

    def __init__(self, com_object, video_input=0):
        self.cap = cv2.VideoCapture(video_input)
        self.com_object = com_object

    def get_current_coords(self):
        if self.cx is None or self.cy is None:
            return None

        return {'x':self.cx, 'y':self.cy}

    def calibrate(self):
        oldfile = None
        for file in os.listdir(BASE_DIR):
            if file == FILENAME:
                oldfile = file

        if oldfile:
            print('starting from previous calibration...')
            with open(os.path.join(BASE_DIR, oldfile), 'rb') as f:
                matrix = pickle.load(f)
                return matrix
        else:
            print('No old configuration was found. please calibrate screen')

        cal_list = []
        width = 0
        height = 0

        def mouse_click(event, x, y, flags, param):
            if (len(cal_list) > 0) and event == cv2.EVENT_RBUTTONUP:
                cal_list.pop()
            elif len(cal_list) < 4 and event == cv2.EVENT_LBUTTONUP:
                cal_list.append([x,y])

        while True:
            ret, frame = self.cap.read()
            width = frame.shape[1]
            height = frame.shape[0]

            pts = np.array(cal_list, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0))

            cv2.namedWindow('calibrate')
            cv2.setMouseCallback('calibrate', mouse_click)

            cv2.imshow('calibrate', frame)

            # to finish press 'd'
            if cv2.waitKey(2) & 0xFF == ord('d'):
                break

        if len(cal_list) == 4:
            pts_origin = np.float32(cal_list)
            pts_dest = np.float32([[0, 0], [width, 0], [width, height],[0, height]])
            matrix = cv2.getPerspectiveTransform(pts_origin, pts_dest)
            with open(os.path.join(BASE_DIR, FILENAME), 'wb') as f:
                pickle.dump(matrix, f)
        else:
            matrix = np.eye(3)

        cv2.destroyWindow('calibrate')
        return matrix

    def ir_loop(self, matrix):
        print('loop start')
        while True:
            ret, frame = self.cap.read()
            if ret:
                width = frame.shape[1]
                height = frame.shape[0]
                frame = cv2.warpPerspective(frame, matrix, (width,height))
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, LOWER_IR, UPPER_IR)
                mask2, contours, hierarchy = cv2.findContours(mask, 1,
                                                              cv2.CHAIN_APPROX_SIMPLE)
                final_cnt = None
                max_area = 0

                for i in range(len(contours)):
                    cnt = contours[i]
                    area = cv2.contourArea(cnt)
                    if area > max_area:
                        max_area = area
                        final_cnt = cnt

                M = cv2.moments(final_cnt)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    tracked_frame = cv2.circle(frame, (cx, cy), 10,
                                         (255, 255, 0))

                    cx /= float(width)
                    cy /= float(height)

                else:
                    cx = None
                    cy = None
                    tracked_frame = frame

                self.com_object.set_current_coords(cx, cy)
                cv2.imshow('mask', tracked_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        print("breaked")
        # When everything done, release the capture
        self.cap.release()