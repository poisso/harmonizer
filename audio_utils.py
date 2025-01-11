import numpy as np
import io
import base64
import struct

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

def generate_chord_audio(chord, sample_rate=44100, waveform='sine'):
    """
    Generate audio data for a chord with smooth transitions.
    
    Args:
        chord: list of Note objects
        sample_rate: sampling rate in Hz
        waveform: 'sine' or 'sawtooth'
    
    Returns:
        base64 encoded WAV file data
    """
    tempo = 120  # Default tempo
    beats_per_bar = 4
    duration = (60 / tempo) * beats_per_bar  # Duration in seconds for one bar
    
    # Add a small overlap for smooth transitions
    overlap = 0.05  # 50ms overlap
    total_duration = duration + (2 * overlap)
    
    # Generate the waveform
    t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
    waves = []
    
    for note in chord:
        # Calculate frequency with octave adjustment
        A4 = 440  # Hz
        A4_note_number = 69
        midi_note = note.number + (note.octave * 12) + 60
        freq = A4 * 2**((midi_note - A4_note_number) / 12)
        
        # Generate wave
        if waveform == 'sine':
            wave = np.sin(2 * np.pi * freq * t)
        else:  # sawtooth
            wave = 2 * (t * freq - np.floor(0.5 + t * freq))
        waves.append(wave)
    
    # Mix waves and normalize
    if waves:
        mixed = sum(waves) / len(waves)
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed / max_val
    else:
        mixed = np.zeros_like(t)
    
    # Apply smoother envelope
    envelope = np.ones_like(mixed)
    attack = int(overlap * sample_rate)
    release = int(overlap * sample_rate)
    envelope[:attack] = np.power(np.linspace(0, 1, attack), 2)
    envelope[-release:] = np.power(np.linspace(1, 0, release), 2)
    mixed *= envelope
    
    return generate_wav_file(mixed, sample_rate) 

def concatenate_chord_audio(chords, tempo=120, sample_rate=44100, waveform='sine'):
    """
    Generate a single audio file from a sequence of chords.
    Empty slots at the end are ignored.
    
    Args:
        chords: list of chords (None for empty slots)
        tempo: tempo in BPM
        sample_rate: sampling rate in Hz
        waveform: 'sine' or 'sawtooth'
    """
    # Remove trailing empty slots
    while chords and chords[-1] is None:
        chords.pop()
    
    if not chords:
        return None
    
    # Calculate duration for one bar
    beats_per_bar = 4
    bar_duration = (60 / tempo) * beats_per_bar
    samples_per_bar = int(sample_rate * bar_duration)
    
    # Generate audio for each chord
    all_samples = []
    
    for chord in chords:
        if chord is None:
            # Empty bar
            bar_samples = np.zeros(samples_per_bar)
        else:
            # Generate chord samples
            t = np.linspace(0, bar_duration, samples_per_bar, False)
            waves = []
            
            for note in chord:
                A4 = 440
                A4_note_number = 69
                midi_note = note.number + (note.octave * 12) + 60
                freq = A4 * 2**((midi_note - A4_note_number) / 12)
                
                if waveform == 'sine':
                    wave = np.sin(2 * np.pi * freq * t)
                else:
                    wave = 2 * (t * freq - np.floor(0.5 + t * freq))
                waves.append(wave)
            
            # Mix waves
            bar_samples = sum(waves) / len(waves) if waves else np.zeros_like(t)
            
            # Normalize
            max_val = np.max(np.abs(bar_samples))
            if max_val > 0:
                bar_samples = bar_samples / max_val
            
            # Apply envelope to avoid clicks
            envelope = np.ones_like(bar_samples)
            attack = int(0.01 * sample_rate)  # 10ms
            release = int(0.01 * sample_rate)  # 10ms
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-release:] = np.linspace(1, 0, release)
            bar_samples *= envelope
        
        all_samples.append(bar_samples)
    
    # Concatenate all samples
    final_audio = np.concatenate(all_samples)
    
    return generate_wav_file(final_audio, sample_rate) 