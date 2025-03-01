from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly

def get_window_position(window_name):
  """
  Retrieves the screen position and size of the window with the given name.
  Returns None if the window is not found.
  """
  window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, 0)
  for window in window_list:
    owner_name = window.get("kCGWindowOwnerName", "")
    if window_name in owner_name:
      bounds = window.get("kCGWindowBounds", {})
      x = int(bounds.get("X", 0))
      y = int(bounds.get("Y", 0))
      width = int(bounds.get("Width", 800))
      height = int(bounds.get("Height", 600))
      return x, y, width, height
  return None