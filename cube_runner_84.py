import pygame
import random
import sys
import math
import os
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 400
GROUND_HEIGHT = HEIGHT - 50
PLAYER_SIZE = 35  # Slightly larger player
GRAVITY = 0.8     # Reduced gravity for higher jumps
JUMP_FORCE = 18   # Increased jump force
INITIAL_GAME_SPEED = 5  # Initial game speed
MAX_GAME_SPEED = 12     # Maximum game speed

# Sound settings
MUSIC_BPM = 120  # Beats per minute
BEAT_INTERVAL = 60000 / MUSIC_BPM  # Milliseconds per beat

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
pygame.display.set_caption("Cube Runner '84")
clock = pygame.time.Clock()

# Create sounds directory if it doesn't exist
os.makedirs("sounds", exist_ok=True)

# Sound class to handle sound effects and music
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.last_beat_time = 0
        self.beat_count = 0
        
        # Create simple sounds using Pygame
        self._create_sounds()
        
    def _create_sounds(self):
        # Create jump sound (simple beep with descending pitch)
        jump_sound = self._create_beep(800, 400, 300)
        jump_sound.set_volume(0.4)
        self.sounds['jump'] = jump_sound
        
        # Create crash sound (noise)
        crash_sound = self._create_noise(500)
        crash_sound.set_volume(0.5)
        self.sounds['crash'] = crash_sound
        
        # Create speed up sound (ascending beeps)
        speed_sound = self._create_speed_up_sound()
        speed_sound.set_volume(0.4)
        self.sounds['speed_up'] = speed_sound
        
        # Create simple music loop
        self._create_music_loop()
    
    def _create_beep(self, start_freq, end_freq, duration_ms):
        """Create a simple beep sound with frequency sweep"""
        sample_rate = 44100
        duration = duration_ms / 1000.0
        samples = int(duration * sample_rate)
        
        # Create buffer
        buf = bytearray(samples * 2)  # 16-bit samples
        
        # Generate a frequency sweep
        for i in range(samples):
            t = i / sample_rate
            freq = start_freq + (end_freq - start_freq) * (i / samples)
            amplitude = 32767 * 0.5 * (1 - (i / samples))  # Fade out
            value = int(amplitude * math.sin(2 * math.pi * freq * t))
            
            # Set the sample in the buffer (little endian)
            buf[i*2] = value & 0xFF
            buf[i*2 + 1] = (value >> 8) & 0xFF
        
        return pygame.mixer.Sound(buffer=buf)
    
    def _create_noise(self, duration_ms):
        """Create a noise sound for crash effect"""
        sample_rate = 44100
        duration = duration_ms / 1000.0
        samples = int(duration * sample_rate)
        
        # Create buffer
        buf = bytearray(samples * 2)  # 16-bit samples
        
        # Generate noise
        for i in range(samples):
            amplitude = 32767 * 0.5 * (1 - (i / samples))  # Fade out
            value = int(amplitude * (random.random() * 2 - 1))
            
            # Set the sample in the buffer (little endian)
            buf[i*2] = value & 0xFF
            buf[i*2 + 1] = (value >> 8) & 0xFF
        
        return pygame.mixer.Sound(buffer=buf)
    
    def _create_speed_up_sound(self):
        """Create a speed up notification sound"""
        sample_rate = 44100
        duration = 500 / 1000.0  # 500ms
        samples = int(duration * sample_rate)
        
        # Create buffer
        buf = bytearray(samples * 2)  # 16-bit samples
        
        # Generate three ascending beeps
        freqs = [400, 600, 800]
        for j, freq in enumerate(freqs):
            start = int(j * samples / 3)
            end = int((j + 1) * samples / 3)
            
            for i in range(start, end):
                t = (i - start) / sample_rate
                amplitude = 32767 * 0.4 * math.sin(math.pi * (i - start) / (end - start))
                value = int(amplitude * math.sin(2 * math.pi * freq * t))
                
                # Set the sample in the buffer (little endian)
                buf[i*2] = value & 0xFF
                buf[i*2 + 1] = (value >> 8) & 0xFF
        
        return pygame.mixer.Sound(buffer=buf)
    
    def _create_music_loop(self):
        """Create a simple 8-bit style music loop"""
        # Create a simple music pattern
        sample_rate = 44100
        bpm = MUSIC_BPM
        beats = 16
        
        duration = beats * 60 / bpm
        samples = int(duration * sample_rate)
        
        # Create buffer
        buf = bytearray(samples * 2)  # 16-bit samples
        
        # Define a simple melody (C major scale notes)
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        
        # Create a simple melody pattern
        pattern = [0, 2, 4, 7, 6, 4, 2, 0, 1, 3, 5, 7, 5, 3, 1, 0]
        
        # Generate the melody
        for beat in range(beats):
            start_sample = int(beat * samples / beats)
            end_sample = int((beat + 0.8) * samples / beats)  # Note duration is 80% of beat
            
            note = notes[pattern[beat]]
            
            for i in range(start_sample, end_sample):
                t = (i - start_sample) / sample_rate
                
                # Create a simple square wave
                value = 32767 * 0.2 * (1 if math.sin(2 * math.pi * note * t) > 0 else -1)
                
                # Apply simple envelope
                env = 1.0
                if i - start_sample < (end_sample - start_sample) * 0.1:
                    env = (i - start_sample) / ((end_sample - start_sample) * 0.1)
                elif i - start_sample > (end_sample - start_sample) * 0.7:
                    env = 1.0 - (i - start_sample - (end_sample - start_sample) * 0.7) / ((end_sample - start_sample) * 0.3)
                
                value = int(value * env)
                
                # Add to buffer
                existing_value = (buf[i*2 + 1] << 8) | buf[i*2]
                if existing_value > 32767:
                    existing_value -= 65536
                
                new_value = max(min(existing_value + value, 32767), -32768)
                
                buf[i*2] = new_value & 0xFF
                buf[i*2 + 1] = (new_value >> 8) & 0xFF
        
        # Create a Sound object directly from the buffer
        try:
            pygame.mixer.music.load(self._save_wav_to_file(buf, sample_rate))
        except:
            print("Could not create music loop")
    
    def _save_wav_to_file(self, buf, sample_rate):
        """Save buffer as a WAV file and return the filename"""
        filename = "sounds/music_loop.wav"
        
        # Save the music file
        with open(filename, "wb") as f:
            # Write a minimal WAV header
            f.write(b'RIFF')
            f.write((36 + len(buf)).to_bytes(4, 'little'))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write((16).to_bytes(4, 'little'))
            f.write((1).to_bytes(2, 'little'))  # PCM format
            f.write((1).to_bytes(2, 'little'))  # Mono
            f.write((sample_rate).to_bytes(4, 'little'))
            f.write((sample_rate * 2).to_bytes(4, 'little'))
            f.write((2).to_bytes(2, 'little'))
            f.write((16).to_bytes(2, 'little'))
            f.write(b'data')
            f.write((len(buf)).to_bytes(4, 'little'))
            f.write(buf)
        
        return filename
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def start_music(self):
        """Start playing the music loop"""
        try:
            pygame.mixer.music.load("sounds/music_loop.wav")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_playing = True
            self.last_beat_time = pygame.time.get_ticks()
            self.beat_count = 0
        except:
            print("Could not load music file")
            self.music_playing = False
    
    def stop_music(self):
        """Stop the music"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def update(self):
        """Update beat tracking"""
        if not self.music_playing:
            return False, self.beat_count
        
        current_time = pygame.time.get_ticks()
        beat_occurred = False
        
        # Check if a beat has occurred
        if current_time - self.last_beat_time > BEAT_INTERVAL:
            self.last_beat_time = current_time - ((current_time - self.last_beat_time) % BEAT_INTERVAL)
            self.beat_count += 1
            beat_occurred = True
        
        return beat_occurred, self.beat_count

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
    
    def update(self, game_speed, beat_occurred=False):
        self.game_speed = game_speed
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to change background color or if a beat occurred
        if current_time - self.last_color_change > self.color_change_interval or beat_occurred:
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
    
    def jump(self, sound_manager):
        if not self.jumping:
            self.vel_y = -JUMP_FORCE
            self.jumping = True
            sound_manager.play_sound('jump')
    
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
    sound_manager = SoundManager()
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
    
    # Start the music
    sound_manager.start_music()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.jump(sound_manager)
                if event.key == pygame.K_r and game_over:
                    # Stop music before restarting
                    sound_manager.stop_music()
                    # Restart the game
                    return main()
        
        # Update music and get beat information
        beat_occurred, beat_count = sound_manager.update()
        
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
                    sound_manager.play_sound('speed_up')
        
        # Update background with beat information
        background.update(game_speed, beat_occurred)
        
        # Change player color on every 4th beat
        if beat_occurred and beat_count % 4 == 0 and not game_over:
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
                    sound_manager.play_sound('crash')
        
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
