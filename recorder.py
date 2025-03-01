import cv2
from mss import mss
import numpy as np
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly

class Recorder:
  def __init__(self, window_name, fourcc, fps, output_file):
        self.window_name = window_name
        self.fps = fps
        self.output_file = output_file
        
        # initialize the fourcc encoding for VideoWriter
        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)

        self.x, self.y, self.width, self.height = 0, 0, 0, 0
        self.out = None

  def get_window_position(self):
    """
    Retrieves the screen position and size of the window with the given name.
    Returns None if the window is not found.
    """
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, 0)
    for window in window_list:
      owner_name = window.get("kCGWindowOwnerName", "")
      if self.window_name in owner_name:
        bounds = window.get("kCGWindowBounds", {})
        self.x = int(bounds.get("X", 0))
        self.y = int(bounds.get("Y", 0))
        self.width = int(bounds.get("Width", 800))
        self.height = int(bounds.get("Height", 600))
        return True
    return False
  
  def setup_video_writer(self):
    """
    Initializes the VideoWriter object and checks if the window dimensions are valid.
    Returns True if everything is set up successfully, otherwise False.
    """
    if not self.get_window_position():
      print(f"Error: Window '{self.window_name}' not found.")
      return False
    
    if self.width <= 0 or self.height <= 0:
      print("Error: Invalid window dimensions.")
      return False
    
    # HOTFIX: width and height must be * 2, unsure why, might be bug with cv2.VideoWriter
    # @see https://stackoverflow.com/questions/74107626/python-opencv2-record-screen
    DOUBLED_SCREEN_SIZE = (self.width * 2, self.height * 2)
    self.out = cv2.VideoWriter(self.output_file, self.fourcc, self.fps, DOUBLED_SCREEN_SIZE) 
    
    if not self.out.isOpened():
      print("Error: Failed to open video writer.")
      return False
    
    return True

  def capture_frame(self):
    """
    Captures a screenshot of the specified window area and writes it to the video.
    """
    with mss() as sct:
      monitor = {"top": self.y, "left": self.x, "width": self.width, "height": self.height}
      img = sct.grab(monitor)
      frame = np.array(img)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
      self.out.write(frame)

  def release(self):
    """
    Releases the VideoWriter when done.
    """
    if self.out:
      self.out.release()
