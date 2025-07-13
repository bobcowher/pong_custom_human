from random import random
from re import error
import pygame
import math
import numpy as np
import random

class Paddle:

    def __init__(self, x, y, player_color, window_height, width=20, height=120, scale_factor=1.0):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Scale movement speed based on screen size
        self.speed = int(10 * scale_factor)

        self.paddle_color = player_color

        self.window_height = window_height
        self.scale_factor = scale_factor


    def draw(self, screen):
        pygame.draw.rect(screen, self.paddle_color,(self.rect.x, self.rect.y, self.width, self.height))


    def move(self, direction):

        # Direction 0 is down, 1 is up. 

        if(direction == 0):
            return
        elif(direction == 1):
            new_y = self.y - self.speed
        elif(direction == 2):
            new_y = self.y + self.speed

        if(0 <= new_y <= (self.window_height - self.height)):
            self.y = new_y

    
        self.rect.topleft = (self.x, self.y)

            
class Ball:

    def __init__(self, window_height, window_width, player_1_paddle, player_2_paddle, width=10, height=10, scale_factor=1.0):
        self.height = height
        self.width = width
        self.window_height = window_height
        self.window_width = window_width
        self.player_1_paddle = player_1_paddle
        self.player_2_paddle = player_2_paddle
        self.ball_color = (255, 255, 255)
        self.scale_factor = scale_factor

        self.spawn()


    def spawn(self):
        # Fix the swapped coordinates bug and center the ball properly
        self.x = self.window_width / 2
        self.y = self.window_height / 2
        
        # Scale ball speed based on screen size
        base_speed_x = random.randint(5, 10)
        base_speed_y = random.randint(3, 10)
        
        self.vx = int(base_speed_x * self.scale_factor)
        self.vy = int(base_speed_y * self.scale_factor)
        
        # Randomize initial direction
        if random.random() < 0.5:
            self.vx *= -1
        if random.random() < 0.5:
            self.vy *= -1
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def generate_new_rect(self):
        new_y = self.y + self.vy
        new_x = self.x + self.vx
    
        new_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        return new_x, new_y, new_rect


    def move(self):
        
        collision = False

        # First pass at new_x and new_y
        new_x, new_y, new_rect = self.generate_new_rect()

        if(not (0 <= new_y <= (self.window_height - self.height))):
            # Scale the maximum speed limit based on screen size
            max_speed = int(20 * self.scale_factor)
            self.vy = np.clip(self.vy * -1, -max_speed, max_speed)


        for paddle in [self.player_1_paddle, self.player_2_paddle]:
               if(new_rect.colliderect(paddle)):
                    # Scale the max speed limit for x direction as well
                    max_speed_x = int(25 * self.scale_factor)
                    self.vx = np.clip((self.vx * 1.1) * -1, -max_speed_x, max_speed_x) # Invert direction and speed up the ball slightly
        
        new_x, new_y, new_rect = self.generate_new_rect()

        self.x = new_x
        self.y = new_y
        self.rect = new_rect

#        self.rect.topleft = (self.x, self.y)
    

    def draw(self, screen):
        pygame.draw.rect(screen, self.ball_color,(self.rect.x, self.rect.y, self.width, self.height))








