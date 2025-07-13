import pygame
import sys

from pygame.cursors import ball
from assets import Paddle, Ball
import random
import time

class Pong:

    def __init__(self, window_width=None, window_height=None, fps=60, player1="human", player2="bot"):
        
        pygame.init()
        
        # Get screen dimensions and calculate scaling
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        
        # Reference dimensions (4K monitor baseline)
        self.reference_width = 1280
        self.reference_height = 960
        
        # If no dimensions provided, use 80% of screen width maintaining aspect ratio
        if window_width is None or window_height is None:
            self.window_width = int(screen_width * 0.8)
            self.window_height = int(self.window_width * (self.reference_height / self.reference_width))
        else:
            self.window_width = window_width
            self.window_height = window_height
        
        # Calculate scaling factor based on window width
        self.scale_factor = self.window_width / self.reference_width
        
        pygame.display.set_caption("Pong")

        self.off_screen_surface = pygame.Surface((self.window_width, self.window_height))
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.fps = fps

        self.background_color = (0, 0, 0)

        # Scale all dimensions based on screen size
        self.paddle_height = int(120 * self.scale_factor)
        self.paddle_width = int(20 * self.scale_factor)
       
        self.player_1_color = (50, 205, 50)
        self.player_2_color = (138, 43, 226)
        
        # Scale fonts
        self.font = pygame.font.SysFont(None, int(70 * self.scale_factor))
        self.announcement_font = pygame.font.SysFont(None, int(150 * self.scale_factor))

        self.player1 = player1
        self.player2 = player2

        self.player_1_score = 0
        self.player_2_score = 0

        self.top_score = 20

        # Scale paddle positions
        paddle_margin = int(self.window_width / 64)
        
        self.player_1_paddle = Paddle(x=self.window_width - paddle_margin - self.paddle_width,
                                      y=(self.window_height / 2) - (self.paddle_height / 2),
                                      player_color=self.player_1_color,
                                      height=self.paddle_height,
                                      width=self.paddle_width,
                                      window_height=self.window_height,
                                      scale_factor=self.scale_factor);
        
        self.player_2_paddle = Paddle(x=paddle_margin,
                                      y=(self.window_height / 2) - (self.paddle_height / 2),
                                      player_color=self.player_2_color,
                                      height=self.paddle_height,
                                      width=self.paddle_width,
                                      window_height=self.window_height,
                                      scale_factor=self.scale_factor);

        # Scale ball size
        ball_size = int(20 * self.scale_factor)
        
        self.ball = Ball(window_height=self.window_height,
                         window_width=self.window_width,
                         height=ball_size,
                         width=ball_size,
                         player_1_paddle=self.player_1_paddle,
                         player_2_paddle=self.player_2_paddle,
                         scale_factor=self.scale_factor)

        self.bot_move_queue = []


    def game_loop(self):
        while(True):

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            keys = pygame.key.get_pressed()

            if self.player1 == "human": 
                if keys[pygame.K_k]:
                    self.player_1_paddle.move(1)
                elif keys[pygame.K_j]:
                    self.player_1_paddle.move(2)
            if self.player2 == "human":
                if keys[pygame.K_w]:
                    self.player_2_paddle.move(1)
                elif keys[pygame.K_s]:
                    self.player_2_paddle.move(2)

            if self.player1 == "bot":
                move = self.get_bot_move()
                self.player_1_paddle.move(move)
            if self.player2 == "bot":
                move = self.get_bot_move()
                self.player_2_paddle.move(move)

            self.step()


    def get_bot_move(self):
         
        random_target = 0.05
        rqueue = 5

        if self.bot_move_queue.__len__() > 0:
            pass 
        elif random.random() <= random_target:
            next_move = random.randint(0, 2)
            
            for i in range(rqueue):
                self.bot_move_queue.append(next_move)
        else:
            if(self.ball.vy > 0):
                self.bot_move_queue.append(2)
            else:
                self.bot_move_queue.append(1)

        return self.bot_move_queue.pop(0)       


    def game_over(self):
        # Render the "You Died" message
        if(self.player_1_score >= self.top_score):
            game_over_surface = self.announcement_font.render('Player 1 Won', True, self.player_1_color)
        elif(self.player_2_score >= self.top_score):
            game_over_surface = self.announcement_font.render('Player 2 Won', True, self.player_2_color)
        
        game_over_rect = game_over_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))

        # Blit the message to the screen
        self.screen.blit(game_over_surface, game_over_rect)

        # Update the display to show the message
        pygame.display.flip()

        self.done = True

        time.sleep(10)

        pygame.quit()
        sys.exit()


    def fill_background(self):
        self.screen.fill(self.background_color)

        # Scale UI element spacing
        margin = int(20 * self.scale_factor)
        ui_y = int(10 * self.scale_factor)
        
        player_1_score_surface = self.font.render(f'Score: {self.player_1_score}', True, self.player_1_color)
        self.screen.blit(player_1_score_surface, ((self.window_width / 2) + margin, ui_y))
        
        player_2_score_surface = self.font.render(f'Score: {self.player_2_score}', True, self.player_2_color)
        self.screen.blit(player_2_score_surface, ((self.window_width / 2) - player_2_score_surface.get_width() - margin, ui_y))


    def step(self):
        # Render directly to the main screen (no need for off-screen surface scaling)
        self.screen.fill(self.background_color)
        
        # Draw score
        self.fill_background()
        
        # Draw game elements
        self.player_1_paddle.draw(screen=self.screen)
        self.player_2_paddle.draw(screen=self.screen)
        self.ball.move()
        self.ball.draw(screen=self.screen)
        
        self.clock.tick(self.fps)
        pygame.display.flip()

        if(self.ball.x < 0):
            self.player_1_score += 1
            self.ball.spawn()
        elif(self.ball.x > self.window_width):
            self.player_2_score += 1
            self.ball.spawn()


        if(self.player_1_score >= self.top_score or
           self.player_2_score >= self.top_score):
            self.game_over()



