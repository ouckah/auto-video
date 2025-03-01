import pygame
import random
import cv2
import time
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
recorder = Recorder(window_name=WINDOW_NAME, fourcc="mp4v", fps=FPS, output_file="output.mov")
time.sleep(0.5)
while not recorder.setup_video_writer():
    time.sleep(0.1)

# recording setup
VIDEO_LENGTH = 3 # in seconds
MAX_FRAMES = VIDEO_LENGTH * FPS

# game loop
running = True
clock = pygame.time.Clock()
start_time = time.time()

frame_count = 0
while running:
    screen.fill((0, 0, 0))  # clear screen
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    # capture frame for recording
    recorder.capture_frame()

    frame_count += 1
    if frame_count >= MAX_FRAMES:  # stop after recording enough frames
        running = False

    clock.tick(FPS)

# cleanup
pygame.quit()
cv2.destroyAllWindows()
recorder.release()
print("🎥 Recording saved as output.mov ✅")
