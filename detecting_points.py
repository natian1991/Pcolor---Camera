import imutils
from imutils import contours
from skimage import measure
import numpy as np
import cv2
from matplotlib import pyplot as plt

# TODO add edge cases to the one spot
# TODO check the 4 points

def detect_one_point(input_video):
    """
    detect the brightest spot in input_video if there's a bright one
    :param input_video: camera port or a video file path
    :return:
    """
    cap = cv2.VideoCapture(input_video)
    ret, frame = cap.read()

    while ret:
        # Capture frame-by-frame
        if frame.size == 0:
            print "no frame"
            break

        # Our operations on the frame come here
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)

        # find the contours in the thresh
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        if len(cnts) > 0:
            c = cnts[0]
            # getting the center of the dot
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            # draw the bright spot on the image
            # cv2.circle(gray, (int(cX), int(cY)), int(radius), (0, 0, 255), 3)
            print (cX, cY)  # should be changed to write to some socket


        # Display the resulting frame
        # cv2.imshow('frame', gray)
        # cv2.waitKey(10)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        ret, frame = cap.read()


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()



def detect4points(input_video):
    """
    detect the 4 brightest spots in input_video if there's a bright one
    :param input_video: camera port or a video file path
    :return:
    """
    cap = cv2.VideoCapture(input_video)
    ret, frame = cap.read()
    num_of_points = 0

    while ret:
        # Capture frame-by-frame
        if frame.size == 0:
            print "no frame"
            break

        # Our operations on the frame come here
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)

        labels = measure.label(thresh, neighbors=8, background=0)
        mask = np.zeros(thresh.shape, dtype="uint8")

        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            # if all 4 points were found
            if num_of_points >= 4:
                break

            # otherwise, construct the label mask
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            mask = cv2.add(mask, labelMask)
            num_of_points += 1

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        cnts = cnts[0]

        # loop over the contours
        for (i, c) in enumerate(cnts):
            # getting the center of the dot
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            # draw the bright spot on the image
            # cv2.circle(gray, (int(cX), int(cY)), int(radius),(0, 0, 255), 3)
            print (cX, cY)  # should be changed to write to some socket


        # Display the resulting frame
        # cv2.imshow('frame', gray)
        # cv2.waitKey(10)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        if num_of_points >= 4:
            break
        ret, frame = cap.read()

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

