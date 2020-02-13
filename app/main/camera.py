from threading import Thread
import cv2, time

class VideoStreamWidget(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            print('calling update')
            print('isOpened = '+str(self.capture.isOpened()))
            if self.capture.isOpened():
                print('Inside isOpened')
                (self.status, self.frame) = self.capture.read()
                print('frame = '+str(self.frame))
            time.sleep(0.01)


    def read(self):
        print('self.frame in read = '+str(self.frame))
        return self.frame

    def show_frame(self):
        # Display frames in main program
        cv2.imshow('frame', self.frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

# if __name__ == '__main__':
#     video_stream_widget = VideoStreamWidget()
#     while True:
#         try:
#             video_stream_widget.show_frame()
#         except AttributeError:
#             pass