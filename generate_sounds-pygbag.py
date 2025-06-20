import numpy as np
from scipy.io import wavfile
import os

def generate_sine_wave(freq, duration, sample_rate=44100, amplitude=0.5):
    """Generate a sine wave at the specified frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave

def generate_square_wave(freq, duration, sample_rate=44100, amplitude=0.5):
    """Generate a square wave at the specified frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * np.sign(np.sin(2 * np.pi * freq * t))
    return wave

def generate_triangle_wave(freq, duration, sample_rate=44100, amplitude=0.5):
    """Generate a triangle wave at the specified frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t))
    return wave

def generate_sawtooth_wave(freq, duration, sample_rate=44100, amplitude=0.5):
    """Generate a sawtooth wave at the specified frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * 2 * (t * freq - np.floor(0.5 + t * freq))
    return wave

def generate_noise(duration, sample_rate=44100, amplitude=0.5):
    """Generate white noise"""
    return amplitude * np.random.uniform(-1, 1, int(sample_rate * duration))

def apply_envelope(wave, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sustain_level=0.8):
    """Apply an ADSR envelope to a wave"""
    sample_rate = 44100
    total_length = len(wave)
    
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_length - attack_samples - decay_samples - release_samples
    
    envelope = np.ones(total_length)
    
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    if decay_samples > 0:
        envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Sustain
    envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain_level
    
    # Release
    if release_samples > 0:
        envelope[attack_samples+decay_samples+sustain_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    return wave * envelope

def save_wave(wave, filename, sample_rate=44100):
    """Save a wave to a WAV file"""
    # Ensure the wave is in the range [-1, 1]
    wave = np.clip(wave, -1, 1)
    
    # Convert to 16-bit PCM
    wave_int = (wave * 32767).astype(np.int16)
    
    # Save the file
    wavfile.write(filename, sample_rate, wave_int)

def generate_jump_sound():
    """Generate a jump sound effect"""
    sample_rate = 44100
    duration = 0.3
    
    # Start with a higher frequency and sweep down
    freqs = np.linspace(800, 400, int(sample_rate * duration))
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.7 * np.sin(2 * np.pi * freqs * t / sample_rate)
    
    # Add a bit of square wave for that 8-bit feel
    square = 0.3 * np.sign(np.sin(2 * np.pi * freqs * 1.5 * t / sample_rate))
    
    combined = wave + square
    
    # Apply envelope
    result = apply_envelope(combined, attack=0.01, decay=0.1, release=0.2, sustain_level=0.7)
    
    save_wave(result, "sounds/jump.ogg", sample_rate)

def generate_crash_sound():
    """Generate a crash sound effect"""
    sample_rate = 44100
    duration = 0.5
    
    # Base noise
    noise = generate_noise(duration, sample_rate, 0.8)
    
    # Add some low frequency rumble
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    rumble = 0.6 * np.sin(2 * np.pi * 60 * t) * np.exp(-5 * t)
    
    combined = noise + rumble
    
    # Apply envelope
    result = apply_envelope(combined, attack=0.001, decay=0.2, release=0.3, sustain_level=0.6)
    
    save_wave(result, "sounds/crash.ogg", sample_rate)

def generate_speed_up_sound():
    """Generate a speed up notification sound"""
    sample_rate = 44100
    duration = 0.5
    
    # Create an ascending series of notes
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Three ascending notes
    note1 = 0.3 * np.sin(2 * np.pi * 400 * t) * np.exp(-10 * (t - 0.1)**2)
    note2 = 0.3 * np.sin(2 * np.pi * 600 * t) * np.exp(-10 * (t - 0.25)**2)
    note3 = 0.3 * np.sin(2 * np.pi * 800 * t) * np.exp(-10 * (t - 0.4)**2)
    
    combined = note1 + note2 + note3
    
    save_wave(combined, "sounds/speed_up.ogg", sample_rate)

def generate_simple_music_loop():
    """Generate a simple 8-bit style music loop"""
    sample_rate = 44100
    bpm = 120
    beats_per_measure = 4
    measures = 4
    
    # Calculate total duration
    beat_duration = 60 / bpm
    measure_duration = beat_duration * beats_per_measure
    total_duration = measure_duration * measures
    
    # Create base track
    result = np.zeros(int(sample_rate * total_duration))
    
    # Define a simple melody (C major scale notes)
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    # Create a simple melody pattern
    melody_pattern = [0, 2, 4, 7, 6, 4, 2, 0, 1, 3, 5, 7, 5, 3, 1, 0]
    
    # Add melody
    for i, note_idx in enumerate(melody_pattern):
        beat_position = i % 16
        t_start = beat_position * beat_duration
        t_end = t_start + beat_duration * 0.8  # Note duration is 80% of beat
        
        start_sample = int(t_start * sample_rate)
        end_sample = int(t_end * sample_rate)
        
        note = notes[note_idx]
        t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
        
        # Use square wave for melody
        wave = 0.3 * np.sign(np.sin(2 * np.pi * note * t))
        
        # Apply simple envelope
        env = np.ones_like(wave)
        attack = int(0.05 * len(wave))
        release = int(0.2 * len(wave))
        
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if release > 0:
            env[-release:] = np.linspace(1, 0, release)
            
        wave = wave * env
        
        # Add to result
        if end_sample <= len(result):
            result[start_sample:end_sample] += wave
    
    # Add bass line
    bass_notes = [65.41, 73.42, 82.41, 87.31]  # C2, D2, E2, F2
    bass_pattern = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 2, 1]
    
    for i, note_idx in enumerate(bass_pattern):
        beat_position = i % 16
        t_start = beat_position * beat_duration
        t_end = t_start + beat_duration * 0.7  # Bass note duration
        
        start_sample = int(t_start * sample_rate)
        end_sample = int(t_end * sample_rate)
        
        note = bass_notes[note_idx]
        t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
        
        # Use sawtooth wave for bass
        wave = 0.25 * generate_sawtooth_wave(note, t_end - t_start)[:len(t)]
        
        # Apply simple envelope
        env = np.ones_like(wave)
        attack = int(0.1 * len(wave))
        release = int(0.3 * len(wave))
        
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if release > 0:
            env[-release:] = np.linspace(1, 0, release)
            
        wave = wave * env
        
        # Add to result
        if end_sample <= len(result):
            result[start_sample:end_sample] += wave
    
    # Add drums
    for i in range(measures * beats_per_measure):
        # Kick drum on beats 1 and 3
        if i % 4 == 0 or i % 4 == 2:
            t_start = i * beat_duration
            t_end = t_start + 0.1  # Short kick
            
            start_sample = int(t_start * sample_rate)
            end_sample = int(t_end * sample_rate)
            
            t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
            
            # Kick is a sine wave with descending frequency
            freqs = np.linspace(150, 50, len(t))
            kick = 0.5 * np.sin(2 * np.pi * freqs * t / len(t))
            
            # Apply envelope
            env = np.exp(-20 * t)
            kick = kick * env
            
            # Add to result
            if end_sample <= len(result):
                result[start_sample:end_sample] += kick
        
        # Hi-hat on every beat
        t_start = i * beat_duration
        t_end = t_start + 0.05  # Very short hi-hat
        
        start_sample = int(t_start * sample_rate)
        end_sample = int(t_end * sample_rate)
        
        # Hi-hat is filtered noise
        hat = 0.15 * generate_noise(t_end - t_start)
        
        # Apply envelope
        env = np.exp(-50 * np.linspace(0, t_end - t_start, len(hat)))
        hat = hat * env
        
        # Add to result
        if end_sample <= len(result):
            result[start_sample:end_sample] += hat
    
    # Normalize and save
    result = result / np.max(np.abs(result)) * 0.9
    save_wave(result, "sounds/music_loop.ogg")

def generate_geometry_dash_style_music():
    """Generate a more complex music loop inspired by Geometry Dash"""
    sample_rate = 44100
    bpm = 140
    beats_per_measure = 4
    measures = 8
    
    # Calculate total duration
    beat_duration = 60 / bpm
    measure_duration = beat_duration * beats_per_measure
    total_duration = measure_duration * measures
    
    # Create base track
    result = np.zeros(int(sample_rate * total_duration))
    
    # Define a pentatonic scale for that electronic feel
    notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]  # C major pentatonic
    
    # Create an arpeggio pattern
    arpeggio_pattern = [0, 4, 7, 4, 2, 5, 7, 5] * 4
    
    # Add arpeggios
    for i, note_idx in enumerate(arpeggio_pattern):
        beat_position = i / 2  # 16th notes
        t_start = beat_position * beat_duration
        t_end = t_start + beat_duration * 0.2  # Short staccato notes
        
        start_sample = int(t_start * sample_rate)
        end_sample = int(t_end * sample_rate)
        
        note = notes[note_idx]
        t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
        
        # Use square wave with a bit of triangle for that synth sound
        square = 0.2 * np.sign(np.sin(2 * np.pi * note * t))
        # Make sure triangle wave has the same length as t
        triangle = 0.1 * generate_triangle_wave(note, t_end - t_start, sample_rate)[:len(square)]
        wave = square + triangle
        
        # Apply envelope
        env = np.exp(-10 * np.linspace(0, 1, len(wave)))
        wave = wave * env
        
        # Add to result
        if end_sample <= len(result):
            result[start_sample:end_sample] += wave
    
    # Add a pulsing bass line
    bass_notes = [65.41, 73.42, 82.41, 87.31]  # C2, D2, E2, F2
    bass_pattern = [0, 0, 1, 1, 2, 2, 3, 3] * 4
    
    for i, note_idx in enumerate(bass_pattern):
        beat_position = i
        t_start = beat_position * beat_duration
        t_end = t_start + beat_duration * 0.8
        
        start_sample = int(t_start * sample_rate)
        end_sample = int(t_end * sample_rate)
        
        note = bass_notes[note_idx]
        t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
        
        # Use a mix of sawtooth and square for a rich bass
        saw = 0.25 * generate_sawtooth_wave(note, t_end - t_start)[:len(t)]
        square = 0.15 * np.sign(np.sin(2 * np.pi * note * t))
        wave = saw + square
        
        # Add a slight wobble effect
        wobble = 1 + 0.2 * np.sin(2 * np.pi * 8 * t)
        wave = wave * wobble
        
        # Apply envelope
        env = np.ones_like(wave)
        attack = int(0.1 * len(wave))
        release = int(0.3 * len(wave))
        
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if release > 0:
            env[-release:] = np.linspace(1, 0, release)
            
        wave = wave * env
        
        # Add to result
        if end_sample <= len(result):
            result[start_sample:end_sample] += wave
    
    # Add electronic drums
    for i in range(measures * beats_per_measure):
        # Kick drum on beats 1 and 3
        if i % 2 == 0:
            t_start = i * beat_duration
            t_end = t_start + 0.15
            
            start_sample = int(t_start * sample_rate)
            end_sample = int(t_end * sample_rate)
            
            t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
            
            # Electronic kick with pitch envelope
            freqs = np.linspace(180, 40, len(t))
            kick = 0.6 * np.sin(2 * np.pi * freqs * t / len(t))
            
            # Add some distortion
            kick = np.tanh(kick * 2) * 0.5
            
            # Apply envelope
            env = np.exp(-15 * t)
            kick = kick * env
            
            # Add to result
            if end_sample <= len(result):
                result[start_sample:end_sample] += kick
        
        # Snare on beats 2 and 4
        if i % 4 == 1 or i % 4 == 3:
            t_start = i * beat_duration
            t_end = t_start + 0.2
            
            start_sample = int(t_start * sample_rate)
            end_sample = int(t_end * sample_rate)
            
            # Snare is noise + a tone
            noise_part = 0.3 * generate_noise(t_end - t_start)
            tone_part = 0.2 * np.sin(2 * np.pi * 180 * np.linspace(0, t_end - t_start, len(noise_part)))
            snare = noise_part + tone_part
            
            # Apply envelope
            env = np.exp(-20 * np.linspace(0, t_end - t_start, len(snare)))
            snare = snare * env
            
            # Add to result
            if end_sample <= len(result):
                result[start_sample:end_sample] += snare
        
        # Hi-hat pattern
        if i % 1 == 0:  # On every beat
            t_start = i * beat_duration
            t_end = t_start + 0.05
            
            start_sample = int(t_start * sample_rate)
            end_sample = int(t_end * sample_rate)
            
            # Hi-hat is filtered noise
            hat = 0.15 * generate_noise(t_end - t_start)
            
            # Apply envelope
            env = np.exp(-60 * np.linspace(0, t_end - t_start, len(hat)))
            hat = hat * env
            
            # Add to result
            if end_sample <= len(result):
                result[start_sample:end_sample] += hat
    
    # Add some risers and effects for that EDM feel
    for i in range(measures):
        if i % 4 == 3:  # Every 4th measure
            t_start = i * measure_duration
            t_end = (i + 1) * measure_duration
            
            start_sample = int(t_start * sample_rate)
            end_sample = int(t_end * sample_rate)
            
            t = np.linspace(0, t_end - t_start, end_sample - start_sample, False)
            
            # Rising frequency sweep
            freqs = np.linspace(500, 5000, len(t))
            sweep = 0.1 * np.sin(2 * np.pi * freqs * t / sample_rate)
            
            # Apply rising envelope
            env = np.linspace(0, 1, len(sweep)) ** 2
            sweep = sweep * env
            
            # Add to result
            if end_sample <= len(result):
                result[start_sample:end_sample] += sweep
    
    # Normalize and save
    result = result / np.max(np.abs(result)) * 0.9
    save_wave(result, "sounds/geometry_dash_music.ogg")

if __name__ == "__main__":
    # Create sounds directory if it doesn't exist
    os.makedirs("sounds", exist_ok=True)
    
    print("Generating jump sound...")
    generate_jump_sound()
    
    print("Generating crash sound...")
    generate_crash_sound()
    
    print("Generating speed up sound...")
    generate_speed_up_sound()
    
    print("Generating music loop...")
    generate_geometry_dash_style_music()
    
    print("All sounds generated successfully!")
