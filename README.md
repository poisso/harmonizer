# Chord Sequence Builder

A web application for creating and experimenting with musical chord progressions. This tool allows you to generate chord harmonizations, arrange them in a sequence, and export the result as audio.

## Features

### Chord Generation
- Input notes by name (C, D, E...) or number (0-11)
- Generate harmonized chords with multiple voicings
- Choose chord size (3, 4, or 5 notes)
- Two waveform types: sine and sawtooth
- Real-time audio preview
- Randomize voicings

### Interactive Grid
- 8-bar sequence grid
- Drag and drop interface for chord arrangement
- Real-time voicing changes
- Octave controls for each chord
- Visual feedback during playback
- Move and rearrange chords within the grid

### Audio Features
- Real-time audio playback
- Adjustable tempo (BPM)
- Export sequences to WAV files
- Smooth transitions between chords
- Stop/Play controls
- Download complete sequences

## Installation

1. Create a virtual environment:
python
python -m venv venv
source venv/bin/activate # On Unix
or
venv\Scripts\activate # On Windows


2. Install dependencies:
python
pip install -r requirements.txt


3. Run the application:
python
python app.py


4. Open your browser and go to `http://localhost:5000`

## Usage

### Generating Chords
1. Enter notes in the input field (e.g., "C E G" or "0 4 7")
2. Select desired chord size (3, 4, or 5 notes)
3. Choose waveform type (sine or sawtooth)
4. Click "Generate"

### Building Sequences
1. Drag generated chords to the grid slots
2. Use the dropdown in each slot to change voicings
3. Adjust octaves using up/down arrows
4. Rearrange chords by dragging between slots
5. Clear unwanted chords using the remove button

### Playback Controls
- Set tempo using the BPM control (40-200 BPM)
- Play/Stop: Control sequence playback
- Clear: Remove all chords from the grid
- Download: Export sequence as WAV file

## Project Structure
├── app.py # Main Flask application
├── audio_utils.py # Audio generation and processing
├── harmonizer.py # Chord harmonization logic
├── templates/
│ └── index.html # Web interface
└── requirements.txt # Python dependencies


## Requirements
- Python 3.7+
- Flask
- NumPy
- Web browser with HTML5 audio support

## Technical Details

### Audio Generation
- Real-time audio synthesis using NumPy
- WAV file generation for download
- Smooth transitions between chords
- Adjustable sample rate and bit depth

### Chord Harmonization
- Support for various chord sizes
- Multiple voicing options per chord
- Octave shifting
- Note name and number input support

## License

MIT License

## Author

[Andrew McDonald]