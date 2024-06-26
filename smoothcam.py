import cv2
import threading
import queue

# Replace these with your IP camera's credentials and IP address
username = 'admin'
password = 'Scrc@1234'
cameraip = '192.168.1.121'  # Replace with your camera's IP address
port = '554'  # Common ports are 554 for RTSP or 80 for HTTP

# Construct the URL for the camera stream
url = f'rtsp://{username}:{password}@{cameraip}:{port}/cam/realmonitor?channel=1&subtype=0'

class VideoStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            raise Exception("Error: Could not open video stream")
        self.frame_queue = queue.Queue(maxsize=10)
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                else:
                    print("Failed to grab frame")
            else:
                self.stopped = True

    def read(self):
        return self.frame_queue.get() if not self.frame_queue.empty() else None

    def stop(self):
        self.stopped = True

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

def main():
    try:
        video_stream = VideoStream(url).start()

        # Create a named window
        window_name = 'IP Camera Stream'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Set the window size to 750x750
        cv2.resizeWindow(window_name, 1080, 1080)

        while True:
            frame = video_stream.read()
            if frame is None:
                print("No frame available")
                continue

            cv2.imshow(window_name, frame)

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(e)
    finally:
        video_stream.stop()
        video_stream.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
