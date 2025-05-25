#!/usr/bin/env python3
"""
Guitar Pro Tremolo Converter

This script removes tremolo picking effects from GP5 files and converts them
to individual notes with proper timing consideration, respecting the
tremolo speed encoded in the file (hopefully!)

Requires PyGuitarPro: pip install PyGuitarPro

Usage:
    python tremolo_converter.py input.gp5 output.gp5
"""

import sys
import guitarpro as gp
import argparse
from fractions import Fraction


def has_tremolo_picking(beat):
    """Check if a beat has tremolo picking effect."""
    if hasattr(beat.effect, 'tremoloPicking') and beat.effect.tremoloPicking:
        return True
    for note in beat.notes:
        if hasattr(note.effect, 'tremoloPicking') and note.effect.tremoloPicking:
            return True
    return False


def remove_tremolo_effect(beat):
    """Remove tremolo picking effect from a beat."""
    if hasattr(beat.effect, 'tremoloPicking'):
        beat.effect.tremoloPicking = None
    for note in beat.notes:
        if hasattr(note.effect, 'tremoloPicking'):
            note.effect.tremoloPicking = None


def duration_to_fraction(duration_value, is_dotted=False, is_double_dotted=False):
    """Convert GP duration to fraction of a whole note."""
    base_fraction = Fraction(1, duration_value)
    if is_double_dotted:
        return base_fraction * Fraction(7, 4)
    elif is_dotted:
        return base_fraction * Fraction(3, 2)
    return base_fraction


def get_beat_duration_fraction(beat):
    """Get the duration of a beat as a fraction of a whole note."""
    is_dotted = hasattr(beat.duration, 'isDotted') and beat.duration.isDotted
    is_double_dotted = hasattr(beat.duration, 'isDoubleDotted') and beat.duration.isDoubleDotted
    return duration_to_fraction(beat.duration.value, is_dotted, is_double_dotted)


def calculate_beat_positions(voice):
    """Calculate the start position of each beat in the voice as fractions."""
    positions = []
    current_pos = Fraction(0)
    for beat in voice.beats:
        positions.append(current_pos)
        current_pos += get_beat_duration_fraction(beat)
    return positions


def get_time_signature_duration(measure):
    """Get the total duration of a measure based on time signature."""
    if hasattr(measure, 'header') and hasattr(measure.header, 'timeSignature'):
        ts = measure.header.timeSignature
        try:
            numerator = int(ts.numerator)
            denominator = int(ts.denominator)
            return Fraction(numerator, denominator)
        except AttributeError:
            try:
                numerator = int(getattr(ts, 'numerator'))
                denominator = int(getattr(ts, 'denominator'))
                return Fraction(numerator, denominator)
            except:
                print("    Warning: Could not reliably read time signature numerator/denominator. Defaulting to 4/4.")
                return Fraction(1)
        except TypeError:
            print("    Warning: Time signature numerator or denominator are not valid numbers. Defaulting to 4/4.")
            return Fraction(1)
    return Fraction(1)


def create_individual_notes(original_beat, voice, tremolo_speed_object):
    """Create individual notes (handling chords) based on original duration and tremolo speed object."""
    original_duration_fraction = get_beat_duration_fraction(original_beat)
    target_duration = None

    if tremolo_speed_object:
        speed_value = tremolo_speed_object.duration.value
        if speed_value == 8:
            target_duration = 8
        elif speed_value == 16:
            target_duration = 16
        elif speed_value == 32:
            target_duration = 32
        else:
            print(f"    Warning: Unknown tremolo duration value: {speed_value}. Defaulting to 16th.")
            target_duration = 16
    else:
        print("    Warning: Tremolo speed object not found, defaulting to 16th notes.")
        target_duration = 16

    if target_duration is None:
        return []

    target_duration_fraction = duration_to_fraction(target_duration)
    new_beats = []
    num_original_notes = len(original_beat.notes)
    if num_original_notes > 0:
        notes_per_subdivision = [[] for _ in range(num_original_notes)] # Store sequences for each original note
        remaining_duration = original_duration_fraction

        while remaining_duration >= target_duration_fraction:
            for i, original_note in enumerate(original_beat.notes):
                new_beat = type(original_beat)(voice)
                new_beat.duration = type(original_beat.duration)()
                new_beat.duration.value = target_duration
                if hasattr(new_beat.duration, 'isDotted'): new_beat.duration.isDotted = False
                if hasattr(new_beat.duration, 'dotted'): new_beat.duration.dotted = False
                if hasattr(new_beat.duration, 'isDoubleDotted'): new_beat.duration.isDoubleDotted = False
                if hasattr(new_beat.duration, 'doubleDotted'): new_beat.duration.doubleDotted = False
                new_beat.effect = type(original_beat.effect)()
                new_note = type(original_note)(new_beat)
                new_note.value = original_note.value
                new_note.string = original_note.string
                new_note.type = original_note.type
                new_note.velocity = original_note.velocity
                new_note.effect = type(original_note.effect)()
                new_beat.notes.append(new_note)
                notes_per_subdivision[i].append(new_beat)
            remaining_duration -= target_duration_fraction

        # Works by interleaving these streams of notes into the voice
        # There's probably a wayyyyy simpler way to do this

        if notes_per_subdivision and notes_per_subdivision[0]: # Check if any notes were created
            num_subdivisions = len(notes_per_subdivision[0])
            for _ in range(num_subdivisions):
                new_chord_beat = type(original_beat)(voice)
                new_chord_beat.duration = type(original_beat.duration)()
                new_chord_beat.duration.value = target_duration
                if hasattr(new_chord_beat.duration, 'isDotted'): new_chord_beat.duration.isDotted = False
                if hasattr(new_chord_beat.duration, 'dotted'): new_chord_beat.duration.dotted = False
                if hasattr(new_chord_beat.duration, 'isDoubleDotted'): new_chord_beat.duration.isDoubleDotted = False
                new_chord_beat.effect = type(original_beat.effect)()
                for original_note in original_beat.notes:
                    new_note = type(original_note)(new_chord_beat)
                    new_note.value = original_note.value
                    new_note.string = original_note.string
                    new_note.type = original_note.type
                    new_note.velocity = original_note.velocity
                    new_note.effect = type(original_note.effect)()
                    new_chord_beat.notes.append(new_note)
                new_beats.append(new_chord_beat)
    else:
        # Handle the case where the original beat had no notes (maybe a rest or something weird idk)
        pass

    return new_beats


def convert_tremolo_in_measure(measure, track_name=""):
    """Convert tremolo-picked notes in a single measure."""
    converted_count = 0
    for voice_idx, voice in enumerate(measure.voices):
        tremolo_beats = []
        beat_positions = calculate_beat_positions(voice)
        for beat_idx, beat in enumerate(voice.beats):
            beat_position = beat_positions[beat_idx]  # Assign beat_position here
            if has_tremolo_picking(beat):
                tremolo_speed_value = None
                if hasattr(beat.effect, 'tremoloPicking') and beat.effect.tremoloPicking:
                    tremolo_speed_value = beat.effect.tremoloPicking
                for note in beat.notes:
                    if hasattr(note.effect, 'tremoloPicking') and note.effect.tremoloPicking:
                        tremolo_speed_value = note.effect.tremoloPicking
                        break
                original_duration = beat.duration.value
                original_fraction = get_beat_duration_fraction(beat)
                print(f"    Found tremolo at position {float(beat_position):.3f}, original duration: {original_duration}, fraction: {float(original_fraction):.3f}, detected speed object: {tremolo_speed_value}")
                tremolo_beats.append((beat_idx, beat, beat_positions[beat_idx], original_duration, tremolo_speed_value))

        if not tremolo_beats:
            continue

        for beat_idx, beat, beat_position, original_duration, tremolo_speed_value in reversed(tremolo_beats):
            print(f"    Converting tremolo at position {float(beat_position):.3f}...")
            new_beats = create_individual_notes(beat, voice, tremolo_speed_value)

            if len(new_beats) <= 1:
                remove_tremolo_effect(beat)
                print(f"      Removed tremolo (single note)")
            else:
                voice.beats.pop(beat_idx)
                for i, new_beat in enumerate(new_beats):
                    voice.beats.insert(beat_idx + i, new_beat)
                if new_beats:
                    first_new_beat_duration = new_beats[0].duration.value
                    note_type = {8: "eighth", 16: "sixteenth", 32: "thirty-second"}.get(first_new_beat_duration, f"1/{first_new_beat_duration}")
                    print(f"      Created {len(new_beats)} {note_type} notes from duration {original_duration}")
            converted_count += 1
    return converted_count


def validate_measure_timing(measure):
    """Validate that the measure timing is correct and fix if possible."""
    time_sig_duration = get_time_signature_duration(measure)
    for voice_idx, voice in enumerate(measure.voices):
        total_duration = Fraction(0)
        for beat in voice.beats:
            total_duration += get_beat_duration_fraction(beat)
        if total_duration > time_sig_duration:
            print(f"    Warning: Voice {voice_idx + 1} duration exceeds measure capacity.")
            current_duration = Fraction(0)
            beats_to_keep = []
            for beat in voice.beats:
                beat_duration = get_beat_duration_fraction(beat)
                if current_duration + beat_duration <= time_sig_duration:
                    beats_to_keep.append(beat)
                    current_duration += beat_duration
                else:
                    break
            if len(beats_to_keep) < len(voice.beats):
                print(f"      Trimmed {len(voice.beats) - len(beats_to_keep)} excess beats.")
                voice.beats = beats_to_keep


def convert_tremolo_in_song(song):
    """Convert all tremolo-picked notes in the song."""
    converted_count = 0
    for track_idx, track in enumerate(song.tracks):
        print(f"Processing track {track_idx + 1}: {track.name}")
        for measure_idx, measure in enumerate(track.measures):
            print(f"  Measure {measure_idx + 1}")
            measure_conversions = convert_tremolo_in_measure(measure, track.name)
            if measure_conversions > 0:
                validate_measure_timing(measure)
                converted_count += measure_conversions
    return converted_count


def main():
    parser = argparse.ArgumentParser(description='Remove tremolo picking effects from GP5 files and convert to individual notes respecting tremolo speed.')
    parser.add_argument('input_file', help='Input GP5 file path')
    parser.add_argument('output_file', help='Output GP5 file path')
    parser.add_argument('--simple-mode', action='store_true', help='Just remove tremolo effects without creating individual notes')

    args = parser.parse_args()

    try:
        print(f"Loading {args.input_file}...")
        song = gp.parse(args.input_file)

        if args.simple_mode:
            print("Removing tremolo effects (simple mode)...")
            converted_count = 0
            for track in song.tracks:
                for measure in track.measures:
                    for voice in measure.voices:
                        for beat in voice.beats:
                            if has_tremolo_picking(beat):
                                remove_tremolo_effect(beat)
                                converted_count += 1
            print(f"Removed tremolo from {converted_count} beats.")
        else:
            print("Converting tremolo-picked notes...")
            converted_count = convert_tremolo_in_song(song)

        print(f"Saving to {args.output_file}...")
        gp.write(song, args.output_file)

        print(f"Conversion complete! Processed {converted_count} tremolo sections.")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()