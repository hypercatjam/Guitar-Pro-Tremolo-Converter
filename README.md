This Python script helps you clean up Guitar Pro 5 (`.gp5`) files by converting tremolo picking effects into individual notes, respecting the tremolo speed encoded in the file (hopefully). This can be particularly useful for those who prefer to see explicitly written notes rather than tremolo notations, or most notably for better note detection and readability in Rocksmith CDLC (Black Metal charters rejoice). More testing required. 

## Features

* **Tremolo Conversion:** Converts tremolo-picked notes into a sequence of individual notes based on the detected tremolo speed (e.g., 8th, 16th, 32nd notes).
* **Intelligent Speed Detection:** Attempts to read the tremolo picking speed from the GP5 file.
* **Chord Support:** Handles tremolo picking on chords by duplicating all notes in the chord for each subdivision.

## Limitations

* **GP5 Only:** Only works with GP5 files. You must export any newer GP files to GP5 or older via File>Export>GP5 in Guitar Pro 8.
* **Time Signatures:** I've only tested on 4/4 and 3/4. More testing required for odd time signatures.

## Requirements

* Python 3.x
* PyGuitarPro library (`pip install PyGuitarPro`)

# Installation Directions

This script requires **Python 3** and the **PyGuitarPro** library.

## General Pre-requisites

Before installing, make sure you have **Python 3** installed on your system. You can download it from the official Python website: [python.org](https://www.python.org/).

To check if you have Python 3 and pip (Python's package installer), open a terminal or command prompt and run:

```bash
python3 --version
pip3 --version
```

If these commands return version numbers (e.g., `Python 3.x.x` and `pip x.x.x`), you're ready to proceed.

---

## Installation Instructions

### Windows

1. **Download the Script**  
   Download the `tremolo_converter.py` script to a folder on your computer (e.g., `C:\ChartingTools`).
2. **Open Command Prompt**  
   Open the Command Prompt by searching for **cmd** in the Start Menu.
3. **Navigate to the Script Directory**  
   Use the `cd` command to navigate to the directory where you saved the script. For example:
   ```dos
   cd C:\GuitarProTools
   ```
4. **Install PyGuitarPro**  
   Install the necessary Python library:
   ```dos
   pip install PyGuitarPro
   ```
5. **Run the Script**  
   You can now run the script. Replace `input.gp5` with the path to your Guitar Pro 5 file and `output.gp5` with the desired output file name.
   ```dos
   python tremolo_converter.py input.gp5 output.gp5
   ```

---

### Linux

1. **Download the Script**  
   Download the `tremolo_converter.py` script to a directory (e.g., `~/GuitarProTools`).
2. **Open Terminal**  
   Open your preferred terminal application.
3. **Navigate to the Script Directory**  
   Use the `cd` command to navigate to the directory where you saved the script. For example:
   ```bash
   cd ~/GuitarProTools
   ```
4. **Install PyGuitarPro**  
   Install the necessary Python library. Depending on your distribution, you might use `pip` or `pip3`. It's generally recommended to use `pip3` for Python 3.
   ```bash
   pip3 install PyGuitarPro
   ```
5. **Run the Script**  
   You can now run the script:
   ```bash
   python3 tremolo_converter.py input.gp5 output.gp5
   ```

---

### macOS

1. **Download the Script**  
   Download the `tremolo_converter.py` script to a folder (e.g., `~/Documents/GuitarProTools`).
2. **Open Terminal**  
   Open the Terminal application (found in **Applications/Utilities**).
3. **Navigate to the Script Directory**  
   Use the `cd` command to navigate to the directory where you saved the script. For example:
   ```bash
   cd ~/Documents/GuitarProTools
   ```
4. **Install PyGuitarPro**  
   Install the necessary Python library:
   ```bash
   pip3 install PyGuitarPro
   ```
5. **Run the Script**  
   You can now run the script:
   ```bash
   python3 tremolo_converter.py input.gp5 output.gp5
   ```
## Usage

Open your terminal or command prompt, navigate to the script's directory, and run the script as follows:

```bash
python tremolo_converter.py <input_file.gp5> <output_file.gp5>
```
Make sure you replace `<input_file.gp5>` with the path to your Guitar Pro 5 file!

Replace `<output_file.gp5>` with the desired name for the new Guitar Pro 5 file. 

Example:
```bash
python tremolo_converter.py my_song_with_tremolo.gp5 my_song_converted.gp5
```
That's it! With that, it will export a new .GP5 with the conversions.


---


How it Works:

The script iterates through each track, measure, and beat in the Guitar Pro file. When it finds a beat with a tremolo picking effect, it calculates the original duration of that beat and the intended duration of each individual note based on the tremolo speed (e.g., if a quarter note has 16th note tremolo, it will be expanded into four 16th notes). It then replaces the original tremolo-picked beat with a sequence of new beats, each containing the original notes of the chord (if any) but with the shorter, expanded duration.
Important Note on Timing: The script attempts to maintain correct timing within measures. If converting tremolo causes a measure to exceed its time signature duration, the script will try to trim excess beats to prevent timing issues in the exported file. However, complex or highly dense tremolo patterns might still result in minor timing discrepancies in the output file, which might require manual adjustment in Guitar Pro.
Troubleshooting
ModuleNotFoundError: No module named 'guitarpro': This means PyGuitarPro is not installed. Make sure you ran pip install PyGuitarPro (or pip3 install PyGuitarPro) successfully. 
FileNotFoundError: Double-check that the input file path you provided is correct and the file exists. 
Errors related to gp5 file parsing: While PyGuitarPro is generally robust, highly corrupted or unusual .gp5 files might cause parsing issues. 
Unexpected timing/measure issues: For very complex tremolo patterns, manual review and minor adjustments in Guitar Pro might be necessary after conversion. 


