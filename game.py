import pygame
import sys
import os

from pygame.cursors import ball
from assets import Paddle, Ball
import random
import time

class Pong:

    def __init__(self, window_width=None, window_height=None, fps=60, player1="human", player2="bot"):
        
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Get screen dimensions and calculate scaling
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        
        # Reference dimensions (4K monitor baseline)
        self.reference_width = 1280
        self.reference_height = 960
        
        # If no dimensions provided, use 60% of screen width maintaining aspect ratio
        if window_width is None or window_height is None:
            self.window_width = int(screen_width * 0.6)
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

        self.top_score = 10 

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
        
        # Initialize background music
        self.setup_background_music()


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
         
        random_target = 0.02
        rqueue = 5 

        if self.bot_move_queue.__len__() > 0:
            pass
        elif random.random() <= random_target:
            next_move = random.randint(0, 2)
            
            for i in range(rqueue):
                self.bot_move_queue.append(next_move)
        else:
            if(self.ball.y > (self.player_2_paddle.y + 10)):
                self.bot_move_queue.append(2)
                self.bot_move_queue.append(2)
                self.bot_move_queue.append(2)
            elif(self.ball.y < (self.player_2_paddle.y - 10)):
                self.bot_move_queue.append(1)
                self.bot_move_queue.append(1)
                self.bot_move_queue.append(1)
            else:
                self.bot_move_queue.append(0)

        print(self.bot_move_queue)
        return self.bot_move_queue.pop(0)       


    def game_over(self):
        # Stop background music
        self.stop_background_music()
        
        # Show winner message and play again popup
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # Play again
                        self.reset_game()
                        self.setup_background_music()  # Restart music
                        return
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        # Quit game
                        pygame.quit()
                        sys.exit()
            
            # Clear screen
            self.screen.fill(self.background_color)
            
            # Render winner message
            if(self.player_1_score >= self.top_score):
                winner_surface = self.announcement_font.render('Player 1 Won!', True, self.player_1_color)
            elif(self.player_2_score >= self.top_score):
                winner_surface = self.announcement_font.render('Player 2 Won!', True, self.player_2_color)
            
            winner_rect = winner_surface.get_rect(center=(self.window_width // 2, self.window_height // 2 - int(100 * self.scale_factor)))
            self.screen.blit(winner_surface, winner_rect)
            
            # Render play again prompt
            play_again_surface = self.font.render('Play Again? (Y/N)', True, (255, 255, 255))
            play_again_rect = play_again_surface.get_rect(center=(self.window_width // 2, self.window_height // 2 + int(50 * self.scale_factor)))
            self.screen.blit(play_again_surface, play_again_rect)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)

    def reset_game(self):
        """Reset the game state for a new game"""
        self.player_1_score = 0
        self.player_2_score = 0
        
        # Reset paddle positions
        paddle_margin = int(self.window_width / 64)
        
        self.player_1_paddle.x = self.window_width - paddle_margin - self.paddle_width
        self.player_1_paddle.y = (self.window_height / 2) - (self.paddle_height / 2)
        self.player_1_paddle.rect.topleft = (int(self.player_1_paddle.x), int(self.player_1_paddle.y))
        
        self.player_2_paddle.x = paddle_margin
        self.player_2_paddle.y = (self.window_height / 2) - (self.paddle_height / 2)
        self.player_2_paddle.rect.topleft = (int(self.player_2_paddle.x), int(self.player_2_paddle.y))
        
        # Reset ball
        self.ball.spawn()
        
        # Clear bot move queue
        self.bot_move_queue = []
    
    def setup_background_music(self):
        """Setup and start background music"""
        try:
            # Try to load the arcade-beat.mp3 file
            music_path = os.path.join("music", "arcade-beat.mp3")
            
            if os.path.exists(music_path):
                # Load and play the MP3 file
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                
                print("Background music started (arcade-beat.mp3)")
                self.background_music = True
            else:
                print(f"Music file not found: {music_path}")
                self.background_music = None
                
        except Exception as e:
            print(f"Could not initialize background music: {e}")
            self.background_music = None
            
    def stop_background_music(self):
        """Stop background music"""
        if hasattr(self, 'background_music') and self.background_music:
            pygame.mixer.music.stop()


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



