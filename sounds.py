import pygame

class SoundEffect:
  pygame.mixer.init()

  bling_sound = pygame.mixer.Sound("./sounds/bling.wav")
  blood_pop_sound = pygame.mixer.Sound("./sounds/blood-pop.wav")
  jump_sound = pygame.mixer.Sound("./sounds/jump.wav")
  tap_sound = pygame.mixer.Sound("./sounds/tap.wav")
