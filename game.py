import pygame
import random
import cv2
import time
from recorder import Recorder
from util import get_window_position

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

def game_loop(screen, squares, fps):
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
            break

        clock.tick(fps)

# recording setup
VIDEO_LENGTH = 3 # in seconds
FOURCC = "mp4v"
OUTPUT_FILE = "output.mp4"
recorder = Recorder(fourcc=FOURCC, fps=FPS, output_file=OUTPUT_FILE)

if __name__ == "__main__":
    time.sleep(0.5)
    
    # get window-to-be-recorded data
    x, y, width, height = get_window_position(WINDOW_NAME)
    print(x, y, width, height)
    
    # start recording window
    recorder.start_recording(x, y, width, height)

    # run the game loop in the main thread
    game_loop(screen, squares, FPS)

    # end recording
    recorder.stop_recording()

# cleanup
pygame.quit()
cv2.destroyAllWindows()
