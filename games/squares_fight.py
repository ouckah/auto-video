import pygame
import random

class Square:
  def __init__(self, x, y, dx, dy, color, size, index, health):
    self.x = x
    self.y = y
    self.dx = dx
    self.dy = dy
    self.color = color
    self.size = size
    self.index = index
    self.health = health
  
  def move(self):
    self.x += self.dx
    self.y += self.dy

  def damage(self, amount=1):
    self.health -= amount
    if self.health <= 0:
      self.health = 0
  
  def is_dead(self):
    return self.health <= 0
  
  def grow(self, amount=5):
    self.size += amount

  def shrink(self, amount=5):
    self.size -= amount

class SquareFight:

  
  def __init__(self, screen, fps, screen_width, screen_height):

    # game specific fields
    self.NUM_SQUARES = 20
    self.SQUARE_SIZE = 50
    self.SQUARE_HEALTH = 5
    self.COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

    self.play = True

    self.screen = screen
    self.fps = fps

    self.screen_width = screen_width
    self.screen_height = screen_height

    # define the bounding box
    box_size = int(min(screen_width, screen_height) * 0.8)  # 80% of the smallest dimension
    self.box_x = (screen_width - box_size) // 2
    self.box_y = (screen_height - box_size) // 2
    self.box_size = box_size

    self.squares = []
    self.square_health = [self.SQUARE_HEALTH] * self.NUM_SQUARES


  def start(self):
    # init square properties
    for i in range(self.NUM_SQUARES):
      x = random.randint(self.box_x, self.box_x + self.box_size - self.SQUARE_SIZE)
      y = random.randint(self.box_y, self.box_y + self.box_size - self.SQUARE_SIZE)
      dx = random.choice([-3, 3])
      dy = random.choice([-3, 3])
      color = random.choice(self.COLORS)
      self.squares.append(Square(x, y, dx, dy, color, self.SQUARE_SIZE, i, self.SQUARE_HEALTH))

  
  def playing(self):
    return self.play

  
  def draw_square(self, square):
    color = square.color
    lighter_color = (min(color[0] + 100, 255), min(color[1] + 100, 255), min(color[2] + 100, 255))

    pygame.draw.rect(self.screen, color, (square.x, square.y, square.size, square.size))
    pygame.draw.rect(self.screen, lighter_color, (square.x, square.y, square.size - 10, square.size - 10))


  def draw_health_bar(self, square):
    x, y = square.x, square.y - 20

    max_health = self.SQUARE_HEALTH
    health = square.health

    pygame.draw.rect(self.screen, (0, 255, 0), (x, y, square.size, 10))
    pygame.draw.rect(self.screen, (255, 0, 0), (x, y, square.size * ((max_health - health) / max_health), 10))

  
  def draw_title(self, text):
    pass


  def detect_collisions(self):
    for i in range(len(self.squares)):
      for j in range(i + 1, len(self.squares)):
        sq1, sq2 = self.squares[i], self.squares[j]

        # check if either square is dead
        if sq1.is_dead() or sq2.is_dead():
          continue

        if (sq1.x < sq2.x + sq2.size and sq1.x + sq1.size > sq2.x and
          sq1.y < sq2.y + sq2.size and sq1.y + sq1.size > sq2.y):

          overlap_x = min(sq1.x + sq1.size - sq2.x, sq2.x + sq2.size - sq1.x)
          overlap_y = min(sq1.y + sq1.size - sq2.y, sq2.y + sq2.size - sq1.y)

          # vertical collision
          if overlap_x > overlap_y:
            sq1.dy, sq2.dy = sq2.dy, sq1.dy  # swap y velocities
            sq1.damage()
            sq1.grow()

          # horizontal collision
          else:
            sq1.dx, sq2.dx = sq2.dx, sq1.dx  # swap x velocities
            sq2.damage()
            sq2.grow()

          # if a square is dead, keep track
          if sq1.is_dead():
            self.NUM_SQUARES -= 1
          if sq2.is_dead():
            self.NUM_SQUARES -= 1


  def update(self):
    self.screen.fill((0, 0, 0))  # clear screen
        
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return  # exit the game loop
      
    # draw the bounding box (white border)
    BUFFER = 5
    pygame.draw.rect(self.screen, (255, 255, 255), (self.box_x, self.box_y, self.box_size, self.box_size), BUFFER)

    # usual game logic
    if self.play:

      # move squares
      for square in self.squares:
        square.move()

        # bounce off bounded box walls
        if square.x <= self.box_x + BUFFER or square.x + square.size >= self.box_x + self.box_size - BUFFER:
          square.dx *= -1
        if square.y <= self.box_y + BUFFER or square.y + square.size >= self.box_y + self.box_size - BUFFER:
          square.dy *= -1

      # detect collisions between squares
      self.detect_collisions()

      # draw squares
      for square in self.squares:
        if not square.is_dead():
          self.draw_square(square)
          self.draw_health_bar(square)

    else:
      for square in self.squares:
        if self.square_health[self.squares.index(square)] > 0:
          # increase the size of the square over time
          self.square_size_increase_rate = 1
          square.size += self.square_size_increase_rate
          self.draw_square(square)
          self.draw_health_bar(square)