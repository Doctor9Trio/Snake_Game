import pygame
import sys
import random
from pygame.math import Vector2

# Initialize pygame
pygame.init()

# FONT #
title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None, 40)
end_font = pygame.font.Font(None, 30)

# COLORS #
blue = (179, 217, 255)
darkblue = (26, 117, 255)
midblue = (126, 161, 255)
red = (204, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
dull_gray = (120, 120, 120)  # Dull color for outside playable area

# CREATING GRID #
OFFSET = 50
cell_size = 30
number_of_cells = 20
screen_width = 2 * OFFSET + cell_size * number_of_cells
screen_height = 2 * OFFSET + cell_size * number_of_cells
screen = pygame.display.set_mode((screen_width, screen_height))  # length and width of game screen
pygame.display.set_caption('Snake Game')  # Title of our game
clock = pygame.time.Clock()  # determine the framerate or the speed of our game

# Load images
try:
    icon = pygame.image.load('icon.png')  # game icon
    pygame.display.set_icon(icon)
    bg_surface = pygame.image.load('background.jpg')  # Replace with your background image
    food_surface = pygame.image.load('candy.png')
    snake_head_img = pygame.image.load('snake_head.png')  # Replace with your snake head image
    snake_body_img = pygame.image.load('snake_body.png')  # Replace with your snake body image
    snake_tail_img = pygame.image.load('snake_tail.png')  # Replace with your snake tail image
except FileNotFoundError as e:
    print(f"Error: {e}")
    pygame.quit()
    sys.exit()

# Load sounds
try:
    eat_sound = pygame.mixer.Sound('point.wav')
    dead_sound = pygame.mixer.Sound('gameover.mp3')
    pygame.mixer.music.load('background_music.mp3')  # Load background music for the start menu
except FileNotFoundError as e:
    print(f"Error: {e}")
    pygame.quit()
    sys.exit()

# CREATING BACKGROUND #
class Back:
    def __init__(self):
        self.position = Vector2(4, 5)

    def draw(self):
        screen.blit(bg_surface, (0, 0))

# CREATING FOOD #
class Food:
    def __init__(self, snake_body):
        self.position = self.generate_random_pos(snake_body)

    def draw(self):
        food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size, cell_size, cell_size)
        screen.blit(food_surface, food_rect)

    def generate_random_cell(self):
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)

    def generate_random_pos(self, snake_body):
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position

# CREATING SNAKE #
class Snake:
    def __init__(self):
        self.body = [Vector2(6, 9), Vector2(5, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.new_direction = self.direction

    def draw(self):
        for index, segment in enumerate(self.body):
            segment_rect = pygame.Rect(OFFSET + segment.x * cell_size, OFFSET + segment.y * cell_size, cell_size, cell_size)
            if index == 0:
                # Draw snake head last to ensure it's on top
                continue
            elif index == len(self.body) - 1:
                # Draw snake tail
                tail_direction = self.body[-2] - self.body[-1]
                angle = tail_direction.angle_to(Vector2(1, 0))
                rotated_tail = pygame.transform.rotate(snake_tail_img, angle)
                rotated_tail_rect = rotated_tail.get_rect(center=segment_rect.center)
                screen.blit(rotated_tail, rotated_tail_rect)
            else:
                screen.blit(snake_body_img, segment_rect)

        # Draw snake head on top
        head_rect = pygame.Rect(OFFSET + self.body[0].x * cell_size, OFFSET + self.body[0].y * cell_size, cell_size, cell_size)
        angle = self.direction.angle_to(Vector2(1, 0))  # Angle relative to (1, 0) vector (right direction)
        rotated_head = pygame.transform.rotate(snake_head_img, angle)
        rotated_rect = rotated_head.get_rect(center=head_rect.center)
        screen.blit(rotated_head, rotated_rect)

    def update(self):
        self.direction = self.new_direction
        self.body.insert(0, self.body[0] + self.direction)
        if self.add_segment:
            self.add_segment = False
        else:
            self.body = self.body[:-1]

    def reset(self):
        self.body = [Vector2(6, 9), Vector2(5, 9)]
        self.direction = Vector2(1, 0)
        self.new_direction = self.direction

# CREATING GAME #
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.bg = Back()
        self.state = 'START'
        self.score = 0
        self.high_score = 0
        self.load_high_score()  # Load high score from file

    def draw(self):
        self.bg.draw()
        self.snake.draw()
        self.food.draw()

        # Draw border around the game grid
        pygame.draw.rect(screen, black, (OFFSET, OFFSET, cell_size * number_of_cells, cell_size * number_of_cells), 2)

        # Dull color outside playable area
        screen.fill(dull_gray, (0, 0, OFFSET, screen_height))  # Left side
        screen.fill(dull_gray, (0, 0, screen_width, OFFSET))  # Top side
        screen.fill(dull_gray, (screen_width - OFFSET, 0, OFFSET, screen_height))  # Right side
        screen.fill(dull_gray, (0, screen_height - OFFSET, screen_width, OFFSET))  # Bottom side

        # Display score and high score
        score_surface = score_font.render(f'Score: {self.score}', True, black)
        high_score_surface = score_font.render(f'High Score: {self.high_score}', True, black)
        screen.blit(score_surface, (OFFSET, OFFSET - 40))
        screen.blit(high_score_surface, (screen_width - OFFSET - high_score_surface.get_width(), OFFSET - 40))

    def update(self):
        if self.state == 'GAME ON':
            self.snake.update()
            self.check_food()
            self.check_walls()
            self.check_snake()

    def check_food(self):
        if self.snake.body[0] == self.food.position:
            self.food.position = self.food.generate_random_pos(self.snake.body)
            self.snake.add_segment = True
            self.score += 1
            eat_sound.play()

    def check_walls(self):
        # Check if snake hits the boundary walls
        if not (0 <= self.snake.body[0].x < number_of_cells and 0 <= self.snake.body[0].y < number_of_cells):
            self.game_over()

    def check_snake(self):
        # Check if snake collides with itself
        if self.snake.body[0] in self.snake.body[1:]:
            self.game_over()

    def game_over(self):
        self.snake.reset()
        self.food.position = self.food.generate_random_pos(self.snake.body)
        self.high_score = max(self.high_score, self.score)  # Update high score if current score is higher
        self.save_high_score()
        self.state = 'GAME OVER'
        dead_sound.play()

    def load_high_score(self):
        try:
            with open('high_score.txt', 'r') as file:
                self.high_score = int(file.read())
        except FileNotFoundError:
            # If file doesn't exist, initialize high score to 0
            self.high_score = 0

    def save_high_score(self):
        with open('high_score.txt', 'w') as file:
            file.write(str(self.high_score))

    def reset_score(self):
        self.score = 0

class StartMenu:
    def __init__(self):
        self.title_surface = title_font.render('Snake Game', True, darkblue)
        self.start_surface = score_font.render('Press any key to start', True, midblue)
        self.show_start_text = True
        self.start_text_timer = 0
        self.music_playing = False

    def update(self):
        self.start_text_timer += 1
        if self.start_text_timer >= 20:  # Blinking effect for start text
            self.show_start_text = not self.show_start_text
            self.start_text_timer = 0

        if not self.music_playing:
            pygame.mixer.music.play(-1)  # Play background music in a loop
            self.music_playing = True

    def draw(self):
        if self.show_start_text:
            screen.blit(self.start_surface, (screen_width // 2 - self.start_surface.get_width() // 2, screen_height // 2 + 10))
        screen.blit(self.title_surface, (screen_width // 2 - self.title_surface.get_width() // 2, screen_height // 2 - 50))

class GameOverMenu:
    def __init__(self):
        self.game_over_surface = title_font.render('GAME OVER', True, red)
        self.restart_surface = score_font.render('Press any key to restart', True, midblue)
        self.score_surface = score_font.render(f'Score: ', True, black)

    def update(self, score):
        self.score_surface = score_font.render(f'Score: {score}', True, black)

    def draw(self):
        screen.blit(self.game_over_surface, (screen_width // 2 - self.game_over_surface.get_width() // 2, screen_height // 2 - 50))
        screen.blit(self.restart_surface, (screen_width // 2 - self.restart_surface.get_width() // 2, screen_height // 2 + 10))
        screen.blit(self.score_surface, (screen_width // 2 - self.score_surface.get_width() // 2, screen_height // 2 + 90))

# Initialize game objects and menus
game = Game()
start_menu = StartMenu()
game_over_menu = GameOverMenu()

# DETERMINING SPEED OF THE SNAKE #
SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)  # event to be triggered and after how many milliseconds

# GAME LOOP #
while True:
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == 'START':
                game.state = "GAME ON"
                pygame.mixer.music.stop()  # Stop background music when game starts
            elif game.state == 'GAME OVER':
                game.state = "GAME ON"
                game.reset_score()  # Reset score when restarting the game
                game_over_menu = GameOverMenu()  # Reset game over menu
            else:
                if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                    game.snake.new_direction = Vector2(0, -1)
                if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                    game.snake.new_direction = Vector2(0, 1)
                if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                    game.snake.new_direction = Vector2(1, 0)
                if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                    game.snake.new_direction = Vector2(-1, 0)

    screen.fill(white)

    if game.state == 'START':
        start_menu.update()
        start_menu.draw()
    elif game.state == 'GAME OVER':
        game_over_menu.update(game.score)
        game_over_menu.draw()
    else:
        game.draw()

    pygame.display.update()
    clock.tick(10)  # Adjust the clock tick to control overall game speed
