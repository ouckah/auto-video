import time
import threading
import cv2
from mss import mss
import numpy as np

class Recorder:


  def __init__(self, fourcc, fps, output_file):
    self.fps = fps
    self.output_file = output_file
    
    # initialize the fourcc encoding for VideoWriter
    self.fourcc = cv2.VideoWriter_fourcc(*fourcc)

    self.video_writer = None

    self.thread = None
    self.stop_event = threading.Event()


  def setup_video_writer(self, width, height):
    """
    Initializes the VideoWriter object and checks if the window dimensions are valid.
    Returns True if everything is set up successfully, otherwise False.
    """
    
    if width <= 0 or height <= 0:
      print("Error: Invalid window dimensions.")
      return False
    
    # HOTFIX: width and height must be * 2, unsure why, might be bug with cv2.VideoWriter
    # @see https://stackoverflow.com/questions/74107626/python-opencv2-record-screen
    DOUBLED_SCREEN_SIZE = (width * 2, height * 2)
    self.video_writer = cv2.VideoWriter(self.output_file, self.fourcc, self.fps, DOUBLED_SCREEN_SIZE) 
    
    if not self.video_writer.isOpened():
      print("Error: Failed to open video writer.")
      return False
    
    return True


  def capture_frame(self, x, y, width, height):
    """
    Captures a screenshot of the specified window area and writes it to the video.
    """
    with mss() as sct:
      monitor = {"top": y, "left": x, "width": width, "height": height}
      img = sct.grab(monitor)
      frame = np.array(img)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
      self.video_writer.write(frame)

  
  def record_video(self, x, y, width, height):
    start_time = time.time()
    last_capture_time = start_time
    
    while True:
      if self.stop_event.is_set():  # check if we should stop the recording
        break

      current_time = time.time()

      # capture frame at intervals based on the target FPS
      if current_time - last_capture_time >= 1 / self.fps:
        self.capture_frame(x, y, width, height)
        last_capture_time = current_time
      
      # sleep for a small time to prevent busy-waiting
      time.sleep(0.001)


  def start_recording(self, x, y, width, height):
    # setup the out receiving the image data 
    self.setup_video_writer(width, height)

    # start thread that will be reading / recording
    self.thread = threading.Thread(target=self.record_video, args=(x, y, width, height))
    self.thread.start()


  def stop_recording(self):
    # send out stop event and join thread
    self.stop_event.set()
    self.thread.join()

    # release out
    self.video_writer.release()
    print(f"🎥 Recording saved as {self.output_file} ✅")
