class Note:
    """Represents a musical note."""
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, name_or_number, octave=0):
        if isinstance(name_or_number, (int, str)):
            # Convert string numbers to integers
            if isinstance(name_or_number, str) and name_or_number.isdigit():
                name_or_number = int(name_or_number)
            
            if isinstance(name_or_number, int):
                # If given a number (0-11)
                self.number = int(name_or_number) % 12
                self.octave = octave
                self.name = self.NOTES[self.number]
            else:
                # If given a note name
                if name_or_number not in self.NOTES:
                    raise ValueError(f"Invalid note name: {name_or_number}. Must be one of {self.NOTES}")
                self.name = name_or_number
                self.number = self.NOTES.index(self.name)
                self.octave = octave
        else:
            raise ValueError("Input must be a note name (str) or a number (0-11)")

    def get_midi_number(self):
        """Get the MIDI note number including octave information."""
        return self.number + (self.octave * 12)

    def __repr__(self):
        return f"{self.name}{self.octave}"

    def __eq__(self, other):
        if not isinstance(other, Note):
            return False
        return (self.name == other.name and 
                self.number == other.number and 
                self.octave == other.octave)


class Harmonizer:
    """Harmonizes a sequence of notes into chords."""
    def __init__(self, notes):
        if not notes:
            raise ValueError("Notes list cannot be empty")
        self.notes = [Note(note) for note in notes]
        self.voicer = Voicer()

    def harmonize(self, chord_size=3):
        """Harmonize with multiple voicing options per chord."""
        if chord_size < 2:
            raise ValueError("Chord size must be at least 2")
        if chord_size > len(self.notes):
            raise ValueError(f"Chord size ({chord_size}) cannot be larger than number of notes ({len(self.notes)})")
            
        chord_sets = []
        for root in self.notes:
            # Get basic chord
            basic_chord = self._build_chord(root, chord_size)
            
            # Generate all voicing variations
            voicings = self._generate_voicings(basic_chord)
            chord_sets.append(voicings)
            
        return chord_sets
    
    def _build_chord(self, root, size):
        """Build a basic chord of given size (all notes in same octave)."""
        if not self.notes or size < 1:
            return []
            
        chord = []
        try:
            index = self.notes.index(root)
            while len(chord) < size:
                chord.append(self.notes[index % len(self.notes)])
                index += 2  # Skip one note
        except ValueError as e:
            raise ValueError(f"Root note {root} not found in notes list") from e
        except Exception as e:
            raise ValueError(f"Error building chord: {str(e)}") from e
            
        return chord
    
    def _generate_voicings(self, chord_notes):
        """Generate different voicings for a chord."""
        voicings = []
        
        # Basic voicings
        close = Voicer.close_position(chord_notes)
        voicings.append(("Close Position", close))
        
        drop2 = Voicer.drop_2(chord_notes)
        voicings.append(("Drop 2", drop2))
        
        drop_top = Voicer.drop_top(chord_notes)
        voicings.append(("Drop Top", drop_top))
        
        raise_bottom = Voicer.raise_bottom(chord_notes)
        voicings.append(("Raise Bottom", raise_bottom))
        
        minimal = Voicer.minimal_intervals(chord_notes)
        voicings.append(("Minimal Intervals", minimal))
        
        spread = Voicer.spread(chord_notes)
        voicings.append(("Spread", spread))
        
        return voicings


class Voicer:
    """Provides different voicing options for chords."""
    
    @staticmethod
    def close_position(chord_notes):
        """Basic close position voicing (notes as close as possible)."""
        if not chord_notes:
            return []
            
        root = chord_notes[0]
        voiced_notes = [Note(root.name, 0)]  # Root in base octave
        
        current_note = voiced_notes[0]
        for note in chord_notes[1:]:
            new_octave = current_note.octave
            if note.number < current_note.number:
                new_octave += 1
            
            new_note = Note(note.name, new_octave)
            current_note = new_note
            voiced_notes.append(new_note)
        
        return voiced_notes
    
    @staticmethod
    def drop_2(chord_notes):
        """Drop 2 voicing - second note from top dropped by an octave."""
        if len(chord_notes) < 3:
            return Voicer.close_position(chord_notes)
            
        # First get close position
        close_voiced = Voicer.close_position(chord_notes)
        
        # Drop the second to last note down an octave
        result = close_voiced.copy()
        drop_idx = len(result) - 2
        result[drop_idx] = Note(result[drop_idx].name, result[drop_idx].octave - 1)
        
        return result
    
    @staticmethod
    def spread(chord_notes):
        """Spread voicing - each note separated by roughly an octave."""
        if not chord_notes:
            return []
            
        root = chord_notes[0]
        voiced_notes = [Note(root.name, 0)]  # Root in base octave
        
        for i, note in enumerate(chord_notes[1:], 1):
            new_note = Note(note.name, i)  # Each subsequent note up an octave
            voiced_notes.append(new_note)
        
        return voiced_notes
    
    @staticmethod
    def drop_top(chord_notes):
        """Drop the highest note by an octave."""
        if len(chord_notes) < 2:
            return Voicer.close_position(chord_notes)
            
        close_voiced = Voicer.close_position(chord_notes)
        result = close_voiced.copy()
        # Drop the last note down an octave
        result[-1] = Note(result[-1].name, result[-1].octave - 1)
        return result
    
    @staticmethod
    def raise_bottom(chord_notes):
        """Raise the lowest note by an octave."""
        if len(chord_notes) < 2:
            return Voicer.close_position(chord_notes)
            
        close_voiced = Voicer.close_position(chord_notes)
        result = close_voiced.copy()
        # Raise the first note up an octave
        result[0] = Note(result[0].name, result[0].octave + 1)
        return result
    
    @staticmethod
    def minimal_intervals(chord_notes):
        """Find voicing with minimal total intervals between adjacent notes."""
        if len(chord_notes) < 2:
            return Voicer.close_position(chord_notes)
            
        def calculate_total_intervals(voicing):
            total = 0
            for i in range(len(voicing) - 1):
                interval = abs(voicing[i+1].get_midi_number() - voicing[i].get_midi_number())
                total += interval
            return total
        
        # Try different octave combinations
        best_voicing = None
        min_total = float('inf')
        
        # Start with close position
        base_voicing = Voicer.close_position(chord_notes)
        
        # Try moving each note up or down an octave
        for i in range(len(base_voicing)):
            test_voicing = base_voicing.copy()
            # Try moving note up an octave
            test_voicing[i] = Note(test_voicing[i].name, test_voicing[i].octave + 1)
            total = calculate_total_intervals(test_voicing)
            if total < min_total:
                min_total = total
                best_voicing = test_voicing.copy()
                
            # Try moving note down an octave
            test_voicing[i] = Note(test_voicing[i].name, test_voicing[i].octave - 1)
            total = calculate_total_intervals(test_voicing)
            if total < min_total:
                min_total = total
                best_voicing = test_voicing.copy()
        
        return best_voicing if best_voicing else base_voicing
    
    @staticmethod
    def shift_octave(chord_notes, offset):
        """Shift all notes up or down by a given number of octaves."""
        return [Note(note.name, note.octave + offset) for note in chord_notes]

    @staticmethod
    def get_available_voicings():
        """Returns list of available voicing options."""
        return ['close', 'drop2', 'spread', 'drop_top', 'raise_bottom', 'minimal_intervals', 'shift_octave']


# Example usage
if __name__ == "__main__":
    # Input can be note names or numbers
    input_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    harmonizer = Harmonizer(input_notes)

    # Generate 3-note chords
    three_note_chords = harmonizer.harmonize(chord_size=3)
    print("3-note chords:")
    for chord in three_note_chords:
        print(chord)

    # Generate 4-note chords
    four_note_chords = harmonizer.harmonize(chord_size=4)
    print("\n4-note chords:")
    for chord in four_note_chords:
        print(chord)
