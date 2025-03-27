import sys
import queue
import time
import threading
import cv2
import numpy as np
import wave
import sounddevice as sd
import soundfile as sf
from mss import mss
import subprocess

class Recorder:

  def __init__(self, fourcc, fps, output_video="output.mp4", output_audio="output.wav"):
    self.fps = fps
    self.output_video = output_video
    self.output_audio = output_audio
    
    # Video setup
    self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
    self.video_writer = None
    self.video_thread = None
    self.audio_thread = None
    self.stop_event = threading.Event()
    
    # Audio setup
    self.input_device = "BlackHole 2ch"
    self.samplerate = 44100
    self.channels = 2 
    self.subtype = "PCM_16"

  def setup_video_writer(self, width, height):
    """
    Initializes the VideoWriter object and checks if the window dimensions are valid.
    Returns True if everything is set up successfully, otherwise False.
    """
    if width <= 0 or height <= 0:
      print("Error: Invalid window dimensions.")
      return False

    DOUBLED_SCREEN_SIZE = (width * 2, height * 2)
    self.video_writer = cv2.VideoWriter(self.output_video, self.fourcc, self.fps, DOUBLED_SCREEN_SIZE) 
    
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

    while not self.stop_event.is_set():
      current_time = time.time()
      elapsed_time = current_time - start_time  # Track elapsed time

      if elapsed_time >= 1 / self.fps:
        self.capture_frame(x, y, width, height)
        last_capture_time = current_time

      time.sleep(0.001)

  def record_audio(self):
    """Captures system audio using BlackHole and ensures synchronization."""
    q = queue.Queue()

    def callback(indata, frames, time, status):
      """This is called (from a separate thread) for each audio block."""
      if status:
          print(status, file=sys.stderr)
      q.put(indata.copy())

    # @see https://python-sounddevice.readthedocs.io/en/0.5.1/examples.html
    try:
      with sf.SoundFile(self.output_audio, mode='w', samplerate=self.samplerate,
                      channels=self.channels, subtype=self.subtype) as file:
        with sd.InputStream(samplerate=self.samplerate, device=self.input_device,
                            channels=self.channels, callback=callback):
          while not self.stop_event.is_set():
            file.write(q.get())
    except Exception as e:
        print(f"⚠️ Error recording audio: {e}")

    print(f"🎙️ Audio saved as {self.output_audio} ✅")

  def start_recording(self, x, y, width, height):
    """Starts recording both video and audio in separate threads."""
    self.setup_video_writer(width, height)

    self.stop_event.clear()

    self.video_thread = threading.Thread(target=self.record_video, args=(x, y, width, height))
    self.audio_thread = threading.Thread(target=self.record_audio)

    self.video_thread.start()
    self.audio_thread.start()

  def stop_recording(self):
    """Stops both video and audio recording and saves the files."""
    self.stop_event.set()
    self.video_thread.join()
    self.audio_thread.join()

    self.video_writer.release()

    print(f"🎥 Recording saved as {self.output_video} ✅")

  def merge_audio_video(self, final_output="final_output.mp4"):
    """Merges the recorded video and audio using FFmpeg, ensuring QuickTime compatibility."""
    cmd = [
        "ffmpeg", "-y",
        "-i", self.output_video,
        "-i", self.output_audio,
        "-filter_complex", "[1:a]asetpts=PTS-STARTPTS[aud];[0:v]setpts=PTS-STARTPTS[vid]",
        "-map", "[vid]", "-map", "[aud]",
        "-c:v", "libx264",  # Re-encode video for better compatibility
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",  # Ensure good audio quality
        "-movflags", "+faststart",  # Optimize for streaming and QuickTime playback
        final_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎬 Final video with audio saved as {final_output} ✅")