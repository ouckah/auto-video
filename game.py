import pygame
import random
import cv2
import time
import threading
from recorder import Recorder

pygame.init()

# game variables
WINDOW_NAME = "Python"
FPS = 60
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1016
SQUARE_SIZE = 40
NUM_SQUARES = 10
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

# set up Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption(WINDOW_NAME)

# force window creation by handling a few events
for _ in range(5):  # process a few events to ensure window is initialized
    pygame.event.get()
    pygame.display.flip()

# square properties
squares = []
for _ in range(NUM_SQUARES):
    x = random.randint(0, SCREEN_WIDTH - SQUARE_SIZE)
    y = random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)
    dx = random.choice([-3, 3])
    dy = random.choice([-3, 3])
    color = random.choice(colors)
    squares.append([x, y, dx, dy, color])

# wait for window to appear
FOURCC = "mp4v"
OUTPUT_FILE = "output.mp4"
recorder = Recorder(window_name=WINDOW_NAME, fourcc=FOURCC, fps=FPS, output_file=OUTPUT_FILE)
time.sleep(0.5)
while not recorder.setup_video_writer():
    time.sleep(0.1)

def game_loop(screen, squares, fps, stop_event):
    clock = pygame.time.Clock()
    start_time = time.time()

    while True:
        screen.fill((0, 0, 0))  # clear screen
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # exit the game loop

        for square in squares:
            square[0] += square[2]  # move x
            square[1] += square[3]  # move y

            # bounce off walls
            if square[0] <= 0 or square[0] + SQUARE_SIZE >= SCREEN_WIDTH:
                square[2] *= -1
            if square[1] <= 0 or square[1] + SQUARE_SIZE >= SCREEN_HEIGHT:
                square[3] *= -1

            pygame.draw.rect(screen, square[4], (square[0], square[1], SQUARE_SIZE, SQUARE_SIZE))

        pygame.display.flip()  # update display

        if time.time() - start_time >= VIDEO_LENGTH:  # stop after VIDEO_LENGTH seconds
            stop_event.set()  # signal to stop the recording
            break

        clock.tick(fps)

# recording setup
VIDEO_LENGTH = 3 # in seconds

# flag to stop recording
stop_recording = threading.Event()

def record_video(recorder, duration, fps, stop_event):
    start_time = time.time()
    last_capture_time = start_time
    
    while True:
        if stop_event.is_set():  # check if we should stop the recording
            break

        current_time = time.time()

        # capture frame at intervals based on the target FPS
        if current_time - last_capture_time >= 1 / fps:
            recorder.capture_frame()
            last_capture_time = current_time
        
        # stop recording after the specified duration
        if current_time - start_time >= duration:
            break
        
        # sleep for a small time to prevent busy-waiting
        time.sleep(0.001)

    recorder.release()
    print(f"🎥 Recording saved as {OUTPUT_FILE} ✅")

if __name__ == "__main__":
    # record in a background thread
    recording_thread = threading.Thread(target=record_video, args=(recorder, VIDEO_LENGTH, FPS, stop_recording))
    recording_thread.start()

    # run the game loop in the main thread
    game_loop(screen, squares, FPS, stop_recording)

    # wait for recording to finish
    recording_thread.join()

# cleanup
pygame.quit()
cv2.destroyAllWindows()
