from threading import Thread
import cv2, time

class VideoStreamWidget(object):
    def __init__(self, src=0):
        """Starts the thread to update the video frames
        """
        self.capture = cv2.VideoCapture(src)
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        """Updates the video frames
        """

        while True:

            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(0.01)


    def read(self):
        """Reads the latest updated frame
        """
        return self.frame

    def show_frame(self):
        """Displays frame
        Used for debugging purposes only
        """
        cv2.imshow('frame', self.frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)