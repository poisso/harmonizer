from flask import Flask, render_template, jsonify, request
from harmonizer import Harmonizer, Note, Voicer
import audio_utils  # Change this line to import the whole module

app = Flask(__name__)

def generate_audio_data(chord, sample_rate=44100, waveform='sine'):
    """Generate audio data for a chord."""
    return audio_utils.generate_chord_audio(chord, sample_rate, waveform)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/harmonize', methods=['POST'])
def harmonize():
    data = request.get_json()
    notes_input = data.get('notes', '').split()  # Expect space-separated notes
    chord_size = int(data.get('chord_size', 3))
    waveform = data.get('waveform', 'sine')
    voicing_type = data.get('voicing', 'close')  # Default to close position
    
    try:
        # Validate input
        notes = []
        for note in notes_input:
            # Check if it's a number
            if note.isdigit():
                num = int(note)
                if num < 0 or num > 11:
                    raise ValueError(f"Note number {num} must be between 0 and 11")
                notes.append(str(num))
            # Check if it's a valid note name
            elif note.upper() in [n.upper() for n in Note.NOTES]:
                notes.append(note.upper())
            else:
                raise ValueError(f"Invalid note: {note}. Must be a number (0-11) or note name (C-B)")
        
        harmonizer = Harmonizer(notes)
        chord_sets = harmonizer.harmonize(chord_size)
        
        # Generate audio data for each chord voicing
        chord_data = []
        for chord_set in chord_sets:
            voicings_data = []
            for voicing_name, voicing in chord_set:
                audio_b64 = generate_audio_data(voicing, waveform=waveform)
                voicings_data.append({
                    'name': voicing_name,
                    'notes': [str(note) for note in voicing],
                    'audio': audio_b64
                })
            chord_data.append(voicings_data)
        
        return jsonify({
            'success': True,
            'chords': chord_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/shift_octave', methods=['POST'])
def shift_octave():
    data = request.get_json()
    voicing = [Note(note['name'], note['octave']) for note in data['notes']]
    shift = data['shift']
    waveform = data.get('waveform', 'sine')
    
    # Apply the octave shift
    shifted_voicing = Voicer.shift_octave(voicing, shift)
    
    # Generate new audio
    audio_b64 = generate_audio_data(shifted_voicing, waveform=waveform)
    
    return jsonify({
        'success': True,
        'notes': [{'name': note.name, 'octave': note.octave} for note in shifted_voicing],
        'audio': audio_b64
    })

@app.route('/play_sequence', methods=['POST'])
def play_sequence():
    data = request.get_json()
    sequence = data['sequence']
    tempo = float(data['tempo'])
    waveform = data.get('waveform', 'sine')
    
    try:
        # Convert sequence data to Note objects
        note_sequence = []
        for chord_data in sequence:
            if chord_data is None:
                note_sequence.append(None)
            else:
                chord_notes = [
                    Note(note['name'], note['octave']) 
                    for note in chord_data['notes']
                ]
                note_sequence.append(chord_notes)
        
        audio_b64 = audio_utils.concatenate_chord_audio(
            note_sequence, 
            tempo=tempo, 
            waveform=waveform
        )
        
        if audio_b64 is None:
            return jsonify({
                'success': False,
                'error': 'No chords to play'
            })
            
        return jsonify({
            'success': True,
            'audio': audio_b64
        })
    except Exception as e:
        print(f"Error in play_sequence: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download_sequence', methods=['POST'])
def download_sequence():
    data = request.get_json()
    sequence = data['sequence']
    tempo = float(data['tempo'])
    waveform = data.get('waveform', 'sine')
    
    try:
        # Convert sequence data to Note objects
        note_sequence = []
        for chord_data in sequence:
            if chord_data is None:
                note_sequence.append(None)
            else:
                chord_notes = [
                    Note(note['name'], note['octave']) 
                    for note in chord_data['notes']
                ]
                note_sequence.append(chord_notes)
        
        audio_b64 = audio_utils.concatenate_chord_audio(
            note_sequence, 
            tempo=tempo, 
            waveform=waveform
        )
        
        if audio_b64 is None:
            return jsonify({
                'success': False,
                'error': 'No chords to download'
            })
            
        return jsonify({
            'success': True,
            'audio': audio_b64
        })
    except Exception as e:
        print(f"Error in download_sequence: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 