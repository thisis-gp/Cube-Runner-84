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
        jump_sound = pygame.mixer.Sound(self._create_beep(800, 400, 300))
        jump_sound.set_volume(0.4)
        self.sounds['jump'] = jump_sound
        
        # Create crash sound (noise)
        crash_sound = pygame.mixer.Sound(self._create_noise(500))
        crash_sound.set_volume(0.5)
        self.sounds['crash'] = crash_sound
        
        # Create speed up sound (ascending beeps)
        speed_sound = pygame.mixer.Sound(self._create_speed_up_sound())
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
        
        return buf
    
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
        
        return buf
    
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
        
        return buf
    
    def _create_music_loop(self):
        """Create a simple 8-bit style music loop file"""
        # This is a placeholder - in a real game, you'd use an actual music file
        # For now, we'll create a very simple pattern
        
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
        
        # Save the music file
        with open("sounds/music_loop.ogg", "wb") as f:
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
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def start_music(self):
        """Start playing the music loop"""
        try:
            pygame.mixer.music.load("sounds/music_loop.ogg")
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
