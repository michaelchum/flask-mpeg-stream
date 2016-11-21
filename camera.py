import cv2

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

        # self.video = cv2.VideoCapture(0)

        # Create shared memory object
        self.memory = sysv_ipc.SharedMemory(123456)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):

        # Read value from shared memory
        memory_value = self.memory.read()

        # Find the 'end' of the string and strip
        i = memory_value.find('\0')
        if i != -1:
            memory_value = memory_value[:i]

        print memory_value
        image = cv2.imread(memory_value)
        # cv2.imshow("WORKING", image)
 
        # success, image = self.video.read()
        # # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # # so we must encode it into JPEG in order to correctly display the
        # # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()