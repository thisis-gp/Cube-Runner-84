import pygame
import random
import sys
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 400
GROUND_HEIGHT = HEIGHT - 50
PLAYER_SIZE = 35  # Slightly larger player
GRAVITY = 0.8     # Reduced gravity for higher jumps
JUMP_FORCE = 18   # Increased jump force
INITIAL_GAME_SPEED = 5  # Initial game speed
MAX_GAME_SPEED = 12     # Maximum game speed

# Neon color themes
NEON_COLORS = [
    (255, 0, 128),    # Neon Pink
    (0, 255, 255),    # Neon Cyan
    (255, 0, 255),    # Neon Purple
    (0, 255, 128),    # Neon Green
    (255, 255, 0),    # Neon Yellow
    (0, 128, 255),    # Neon Blue
    (255, 128, 0)     # Neon Orange
]

BG_COLOR = (20, 20, 30)  # Darker background to make neon colors pop
PLAYER_COLOR = (0, 255, 255)  # Neon Cyan
OBSTACLE_COLORS = [(255, 0, 128), (0, 255, 128), (255, 255, 0)]  # Neon colors
GROUND_COLOR = (40, 40, 60)
TEXT_COLOR = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Geometry Dash")
clock = pygame.time.Clock()

class BackgroundEffect:
    def __init__(self, game_speed):
        self.lines = []
        self.shapes = []
        self.bg_color = BG_COLOR
        self.target_bg_color = BG_COLOR
        self.last_color_change = pygame.time.get_ticks()
        self.color_change_interval = 10000  # 10 seconds
        self.color_transition_speed = 0.05
        self.game_speed = game_speed
        
        # Initialize background lines
        for _ in range(15):
            self.lines.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, GROUND_HEIGHT - 20),
                'length': random.randint(50, 150),
                'speed': random.uniform(1, 3),
                'color': random.choice(NEON_COLORS),
                'thickness': random.randint(1, 3)
            })
        
        # Initialize background shapes
        for _ in range(10):
            shape_type = random.choice(['circle', 'rect', 'triangle'])
            self.shapes.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, GROUND_HEIGHT - 50),
                'size': random.randint(10, 40),
                'speed': random.uniform(1, 2.5),
                'color': random.choice(NEON_COLORS),
                'alpha': random.randint(30, 100),
                'type': shape_type
            })
    
    def update(self, game_speed):
        self.game_speed = game_speed
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to change background color
        if current_time - self.last_color_change > self.color_change_interval:
            self.target_bg_color = (
                random.randint(10, 30),
                random.randint(10, 30),
                random.randint(20, 40)
            )
            self.last_color_change = current_time
        
        # Gradually transition to target background color
        self.bg_color = (
            int(self.bg_color[0] + (self.target_bg_color[0] - self.bg_color[0]) * self.color_transition_speed),
            int(self.bg_color[1] + (self.target_bg_color[1] - self.bg_color[1]) * self.color_transition_speed),
            int(self.bg_color[2] + (self.target_bg_color[2] - self.bg_color[2]) * self.color_transition_speed)
        )
        
        # Update lines
        for line in self.lines:
            line['x'] -= line['speed'] * (self.game_speed / 3)
            if line['x'] + line['length'] < 0:
                line['x'] = WIDTH
                line['y'] = random.randint(0, GROUND_HEIGHT - 20)
                line['length'] = random.randint(50, 150)
                line['color'] = random.choice(NEON_COLORS)
        
        # Update shapes
        for shape in self.shapes:
            shape['x'] -= shape['speed'] * (self.game_speed / 3)
            if shape['x'] + shape['size'] < 0:
                shape['x'] = WIDTH
                shape['y'] = random.randint(0, GROUND_HEIGHT - 50)
                shape['size'] = random.randint(10, 40)
                shape['color'] = random.choice(NEON_COLORS)
                shape['alpha'] = random.randint(30, 100)
    
    def draw(self):
        # Fill background with current color
        screen.fill(self.bg_color)
        
        # Draw grid lines (faint)
        grid_color = (self.bg_color[0] + 20, self.bg_color[1] + 20, self.bg_color[2] + 20)
        grid_spacing = 40
        for x in range(0, WIDTH, grid_spacing):
            pygame.draw.line(screen, grid_color, (x, 0), (x, GROUND_HEIGHT), 1)
        for y in range(0, GROUND_HEIGHT, grid_spacing):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)
        
        # Draw shapes (behind lines)
        for shape in self.shapes:
            shape_surface = pygame.Surface((shape['size'], shape['size']), pygame.SRCALPHA)
            
            if shape['type'] == 'circle':
                pygame.draw.circle(
                    shape_surface, 
                    (*shape['color'], shape['alpha']), 
                    (shape['size']//2, shape['size']//2), 
                    shape['size']//2
                )
            elif shape['type'] == 'rect':
                pygame.draw.rect(
                    shape_surface, 
                    (*shape['color'], shape['alpha']), 
                    (0, 0, shape['size'], shape['size'])
                )
            else:  # triangle
                points = [
                    (shape['size']//2, 0),
                    (0, shape['size']),
                    (shape['size'], shape['size'])
                ]
                pygame.draw.polygon(
                    shape_surface, 
                    (*shape['color'], shape['alpha']), 
                    points
                )
            
            screen.blit(shape_surface, (shape['x'], shape['y']))
        
        # Draw lines
        for line in self.lines:
            pygame.draw.line(
                screen, 
                line['color'], 
                (line['x'], line['y']), 
                (line['x'] + line['length'], line['y']), 
                line['thickness']
            )

class Player:
    def __init__(self):
        self.size = PLAYER_SIZE
        self.x = 100
        self.y = GROUND_HEIGHT - self.size
        self.vel_y = 0
        self.jumping = False
        self.rotation = 0
        self.trail = []
        self.trail_max = 10
        self.color = PLAYER_COLOR
        self.pulse_effect = 0
    
    def jump(self):
        if not self.jumping:
            self.vel_y = -JUMP_FORCE
            self.jumping = True
    
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Check ground collision
        if self.y > GROUND_HEIGHT - self.size:
            self.y = GROUND_HEIGHT - self.size
            self.vel_y = 0
            self.jumping = False
        
        # Update rotation based on movement
        if self.jumping:
            self.rotation += 5
        else:
            self.rotation = 0
        
        # Update trail
        if len(self.trail) >= self.trail_max:
            self.trail.pop(0)
        self.trail.append((self.x + self.size//2, self.y + self.size//2))
        
        # Update pulse effect
        self.pulse_effect = (self.pulse_effect + 0.1) % (2 * math.pi)
    
    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / self.trail_max))
            size = int(self.size * (i / self.trail_max) * 0.8)
            trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(trail_surface, (*self.color, alpha), (0, 0, size, size))
            trail_rect = trail_surface.get_rect(center=pos)
            screen.blit(trail_surface, trail_rect)
        
        # Create a surface for the square
        square_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Add glow effect
        glow_size = int(self.size + 4 + 2 * math.sin(self.pulse_effect))
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color, 100), (0, 0, glow_size, glow_size))
        glow_rect = glow_surface.get_rect(center=(self.size//2, self.size//2))
        square_surface.blit(glow_surface, glow_rect)
        
        # Draw the main square
        pygame.draw.rect(square_surface, self.color, (0, 0, self.size, self.size))
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(square_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
        
        # Draw the rotated square
        screen.blit(rotated_surface, rotated_rect)

class Obstacle:
    def __init__(self, x, shape_type, game_speed):
        self.x = x
        self.shape_type = shape_type  # "rect" or "triangle"
        self.color = random.choice(OBSTACLE_COLORS)
        self.pulse_effect = random.random() * 2 * math.pi
        self.game_speed = game_speed
        
        if shape_type == "rect":
            self.width = random.randint(20, 40)
            self.height = random.randint(20, 60)
            self.y = GROUND_HEIGHT - self.height
        else:  # triangle
            self.size = random.randint(20, 40)
            self.y = GROUND_HEIGHT - self.size
    
    def update(self, game_speed):
        self.game_speed = game_speed
        self.x -= self.game_speed
        self.pulse_effect = (self.pulse_effect + 0.05) % (2 * math.pi)
    
    def draw(self):
        # Calculate glow size based on pulse effect
        glow_size = int(3 + 2 * math.sin(self.pulse_effect))
        
        if self.shape_type == "rect":
            # Draw glow
            pygame.draw.rect(
                screen, 
                self.color, 
                (self.x - glow_size, self.y - glow_size, 
                 self.width + glow_size*2, self.height + glow_size*2),
                0
            )
            
            # Draw main shape
            pygame.draw.rect(
                screen, 
                (min(self.color[0] + 50, 255), 
                 min(self.color[1] + 50, 255), 
                 min(self.color[2] + 50, 255)), 
                (self.x, self.y, self.width, self.height)
            )
        else:  # triangle
            # Points for the triangle
            points = [
                (self.x, self.y + self.size),
                (self.x + self.size, self.y + self.size),
                (self.x + self.size // 2, self.y)
            ]
            
            # Draw glow
            glow_points = [
                (points[0][0] - glow_size, points[0][1] + glow_size),
                (points[1][0] + glow_size, points[1][1] + glow_size),
                (points[2][0], points[2][1] - glow_size)
            ]
            pygame.draw.polygon(screen, self.color, glow_points)
            
            # Draw main shape
            pygame.draw.polygon(
                screen, 
                (min(self.color[0] + 50, 255), 
                 min(self.color[1] + 50, 255), 
                 min(self.color[2] + 50, 255)), 
                points
            )
    
    def is_off_screen(self):
        return self.x < -50

def check_collision(player, obstacle):
    # Add a small forgiveness margin to make the game slightly easier
    player_rect = pygame.Rect(player.x + 2, player.y + 2, player.size - 4, player.size - 4)
    
    if obstacle.shape_type == "rect":
        obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
    else:  # For triangle, use a more forgiving hitbox
        obstacle_rect = pygame.Rect(obstacle.x + obstacle.size//4, obstacle.y + obstacle.size//4, 
                                   obstacle.size//2, obstacle.size//2)
    
    return player_rect.colliderect(obstacle_rect)

def draw_ground():
    # Draw ground with grid pattern
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_HEIGHT, WIDTH, HEIGHT - GROUND_HEIGHT))
    
    # Add grid lines to ground
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (GROUND_COLOR[0] + 20, GROUND_COLOR[1] + 20, GROUND_COLOR[2] + 20), 
                         (x, GROUND_HEIGHT), (x, HEIGHT), 1)
    
    # Add neon line at the top of the ground
    pygame.draw.line(screen, random.choice(NEON_COLORS), (0, GROUND_HEIGHT), (WIDTH, GROUND_HEIGHT), 2)

def show_game_over(score, time_survived):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Game Over text
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over", True, (255, 0, 128))  # Neon pink
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
    
    # Score text
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 0))  # Neon yellow
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    
    # Time survived text
    time_font = pygame.font.SysFont(None, 36)
    time_text = time_font.render(f"Time: {time_survived:.1f}s", True, (0, 255, 128))  # Neon green
    time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    
    # Restart text
    restart_font = pygame.font.SysFont(None, 36)
    restart_text = restart_font.render("Press R to restart", True, (0, 255, 255))  # Neon cyan
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
    
    # Add glow effect to Game Over text
    glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
    glow_surf.fill((0, 0, 0, 0))
    pygame.draw.rect(glow_surf, (255, 0, 128, 100), glow_surf.get_rect(), 0, 10)
    screen.blit(glow_surf, (text_rect.x - 10, text_rect.y - 10))
    
    # Draw all text
    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    screen.blit(time_text, time_rect)
    screen.blit(restart_text, restart_rect)

def show_score_and_speed(score, time_score, game_speed):
    # Score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score + time_score}", True, (0, 255, 255))  # Neon cyan
    screen.blit(score_text, (10, 10))
    
    # Time score
    time_font = pygame.font.SysFont(None, 24)
    time_text = time_font.render(f"Time: {time_score}", True, (255, 255, 0))  # Neon yellow
    screen.blit(time_text, (10, 50))
    
    # Speed
    speed_font = pygame.font.SysFont(None, 24)
    speed_text = speed_font.render(f"Speed: {game_speed:.1f}x", True, (0, 255, 128))  # Neon green
    screen.blit(speed_text, (10, 80))

def show_speed_up_notification():
    font = pygame.font.SysFont(None, 36)
    text = font.render("Speed Up!", True, (255, 0, 128))  # Neon pink
    text_rect = text.get_rect(center=(WIDTH//2, 50))
    
    # Add glow effect
    glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
    glow_surf.fill((0, 0, 0, 0))
    pygame.draw.rect(glow_surf, (255, 0, 128, 80), glow_surf.get_rect(), 0, 10)
    screen.blit(glow_surf, (text_rect.x - 10, text_rect.y - 10))
    
    screen.blit(text, text_rect)

def main():
    # Game variables
    game_speed = INITIAL_GAME_SPEED
    player = Player()
    obstacles = []
    background = BackgroundEffect(game_speed)
    last_obstacle_time = 0
    game_over = False
    obstacle_score = 0
    time_score = 0
    min_obstacle_distance = 300  # Minimum distance between obstacles
    
    # Time tracking
    start_time = pygame.time.get_ticks()
    current_game_time = 0
    last_speed_increase = 0
    speed_increase_interval = 15000  # 15 seconds
    show_speed_notification = False
    speed_notification_time = 0
    
    # For beat-based color changes
    beat_interval = 500  # milliseconds (120 BPM)
    last_beat_time = pygame.time.get_ticks()
    beat_count = 0
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.jump()
                if event.key == pygame.K_r and game_over:
                    # Restart the game
                    return main()
        
        # Update game time if not game over
        if not game_over:
            current_game_time = (current_time - start_time) / 1000  # Convert to seconds
            time_score = int(current_game_time * 2)  # 2 points per second
            
            # Check if it's time to increase speed
            if current_game_time - last_speed_increase >= speed_increase_interval / 1000:
                if game_speed < MAX_GAME_SPEED:
                    game_speed += 0.5
                    last_speed_increase = current_game_time
                    show_speed_notification = True
                    speed_notification_time = current_time
        
        # Update background
        background.update(game_speed)
        
        # Beat-based color changes
        if current_time - last_beat_time > beat_interval:
            last_beat_time = current_time
            beat_count += 1
            
            # Every 4 beats (one bar), change player color
            if beat_count % 4 == 0:
                player.color = random.choice(NEON_COLORS)
        
        # Draw background
        background.draw()
        
        if not game_over:
            # Update player
            player.update()
            
            # Generate obstacles
            can_spawn = len(obstacles) == 0 or (obstacles[-1].x < WIDTH - min_obstacle_distance)
            if can_spawn and current_time - last_obstacle_time > random.randint(1500, 2500):
                shape_type = "rect" if random.random() < 0.7 else "triangle"
                obstacles.append(Obstacle(WIDTH, shape_type, game_speed))
                last_obstacle_time = current_time
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update(game_speed)
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                    obstacle_score += 1
            
            # Check collisions
            for obstacle in obstacles:
                if check_collision(player, obstacle):
                    game_over = True
        
        # Draw everything
        draw_ground()
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw()
        
        # Draw player
        player.draw()
        
        # Show score and speed
        show_score_and_speed(obstacle_score, time_score, game_speed / INITIAL_GAME_SPEED)
        
        # Show speed up notification if needed
        if show_speed_notification and current_time - speed_notification_time < 2000:
            show_speed_up_notification()
        else:
            show_speed_notification = False
        
        if game_over:
            show_game_over(obstacle_score + time_score, current_game_time)
        
        # Update the display
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
