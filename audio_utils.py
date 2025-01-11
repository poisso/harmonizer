import numpy as np
import io
import base64
import struct
from scipy import signal
from scipy.io import wavfile

def generate_wav_file(samples, sample_rate=44100):
    """
    Generate a WAV file from audio samples.
    
    Args:
        samples: numpy array of audio samples (-1 to 1)
        sample_rate: sampling rate in Hz
    
    Returns:
        base64 encoded WAV file data
    """
    # Convert to 16-bit PCM
    scaled = np.int16(samples * 32767)
    
    # Create WAV file manually
    buffer = io.BytesIO()
    
    # Write WAV header
    buffer.write(b'RIFF')
    buffer.write(struct.pack('<I', 0))  # Placeholder for file size
    buffer.write(b'WAVE')
    
    # Write format chunk
    buffer.write(b'fmt ')
    buffer.write(struct.pack('<I', 16))  # Chunk size
    buffer.write(struct.pack('<H', 1))   # Audio format (PCM)
    buffer.write(struct.pack('<H', 1))   # Number of channels
    buffer.write(struct.pack('<I', sample_rate))  # Sample rate
    buffer.write(struct.pack('<I', sample_rate * 2))  # Byte rate
    buffer.write(struct.pack('<H', 2))   # Block align
    buffer.write(struct.pack('<H', 16))  # Bits per sample
    
    # Write data chunk
    buffer.write(b'data')
    data_size = len(scaled.tobytes())
    buffer.write(struct.pack('<I', data_size))
    buffer.write(scaled.tobytes())
    
    # Go back and write file size
    file_size = buffer.tell() - 8
    buffer.seek(4)
    buffer.write(struct.pack('<I', file_size))
    
    # Get the WAV data
    buffer.seek(0)
    wav_data = buffer.read()
    buffer.close()
    
    return base64.b64encode(wav_data).decode('utf-8')

def generate_pwm_wave(frequency, duration, sample_rate=44100, duty_cycle=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate slightly detuned frequencies for stereo effect
    freq_l = frequency * 0.99  # Left channel slightly lower
    freq_r = frequency * 1.01  # Right channel slightly higher
    
    # Generate PWM waves for both channels
    left = np.where((np.sin(2 * np.pi * freq_l * t) + (1 - 2 * duty_cycle)) > 0, 1, -1)
    right = np.where((np.sin(2 * np.pi * freq_r * t) + (1 - 2 * duty_cycle)) > 0, 1, -1)
    
    # Combine into stereo array
    stereo = np.vstack((left, right)).T
    return stereo

def generate_chord_audio(chord, sample_rate=44100, waveform='sine'):
    duration = 1.0  # seconds
    if waveform == 'pwm':
        # Generate stereo PWM for each note and mix
        waves = [generate_pwm_wave(note.frequency, duration, sample_rate) for note in chord]
        mixed = np.sum(waves, axis=0) / len(waves)
    else:
        # Generate mono waves for other waveforms
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        waves = []
        for note in chord:
            if waveform == 'sine':
                wave = np.sin(2 * np.pi * note.frequency * t)
            elif waveform == 'sawtooth':
                wave = signal.sawtooth(2 * np.pi * note.frequency * t)
            elif waveform == 'square':
                wave = signal.square(2 * np.pi * note.frequency * t)
            waves.append(wave)
        mixed = np.sum(waves, axis=0) / len(waves)
        # Convert to mono format
        mixed = np.column_stack((mixed, mixed))
    
    # Normalize
    mixed = mixed / np.max(np.abs(mixed))
    
    # Convert to WAV file
    with io.BytesIO() as wav_file:
        wavfile.write(wav_file, sample_rate, mixed.astype(np.float32))
        wav_file.seek(0)
        return base64.b64encode(wav_file.read()).decode('utf-8')

def concatenate_chord_audio(chord_sequence, tempo=120, waveform='sine'):
    if not any(chord_sequence):
        return None
    
    sample_rate = 44100
    beat_duration = 60.0 / tempo  # Duration of one beat in seconds
    bar_duration = 4 * beat_duration  # 4 beats per bar
    
    # Calculate total number of samples needed
    total_samples = int(bar_duration * sample_rate * len(chord_sequence))
    
    # Create empty stereo array
    mixed = np.zeros((total_samples, 2))
    
    for i, chord in enumerate(chord_sequence):
        if chord is None:
            continue
            
        start_sample = int(i * bar_duration * sample_rate)
        end_sample = int((i + 1) * bar_duration * sample_rate)
        
        if waveform == 'pwm':
            # Generate stereo PWM for each note
            waves = [generate_pwm_wave(note.frequency, bar_duration, sample_rate) for note in chord]
            chord_audio = np.sum(waves, axis=0) / len(waves)
        else:
            # Generate mono audio and convert to stereo
            t = np.linspace(0, bar_duration, int(sample_rate * bar_duration), False)
            waves = []
            for note in chord:
                if waveform == 'sine':
                    wave = np.sin(2 * np.pi * note.frequency * t)
                elif waveform == 'sawtooth':
                    wave = signal.sawtooth(2 * np.pi * note.frequency * t)
                elif waveform == 'square':
                    wave = signal.square(2 * np.pi * note.frequency * t)
                waves.append(wave)
            chord_audio = np.sum(waves, axis=0) / len(waves)
            chord_audio = np.column_stack((chord_audio, chord_audio))
        
        mixed[start_sample:end_sample] = chord_audio
    
    # Normalize
    mixed = mixed / np.max(np.abs(mixed))
    
    # Convert to WAV file
    with io.BytesIO() as wav_file:
        wavfile.write(wav_file, sample_rate, mixed.astype(np.float32))
        wav_file.seek(0)
        return base64.b64encode(wav_file.read()).decode('utf-8') 