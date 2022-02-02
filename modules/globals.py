WNAME = "pysndfx 1.0"

UI_PATH = "./ui/sound_processing.ui"

FILTER_LIST = ["Reverb", "Chorus", "PitchShifter"]

DESC = """pysndproc version 1.0
    -------------------
    Python app that offers both GUI and CLI interfaces for
    easy sound processing. Currently only *.wav files are
    supported. Currently available filters (with their valid names):
    - Reverb (reverb),
    - Chorus (chorus),
    - Pitch shifter (pitchshifter)
"""

FILTER_LABELS ={
    "Reverb": {
        1: "Room size (0.0 - 0.1)",
        2: "Damping (0.0 - 0.1)",
        3: "Wet/Dry Ratio (0.0 - 1.0)"
    },
    "Chorus": {
        1: "Rate [Hz]",
        2: "Depth (0.0 - 0.1)",
        3: "Wet Mix (0.0 - 1.0)"
    },
    "PitchShifter": {
        1: "Shift [semitones]"
    }
}

FILTER_PARAMS = {
    "reverb": {"room_size": 0.2, "damping": 0.02, "ratio": 0.2},
    "chorus": {"rate": 1.0, "depth": 0.25, "mix": 0.5},
    "pitchshifter": {"shift": 12}
}

PARAMS_HELP = """Dict containing valid parameters for selected filter.
    
    Reverb:
    -> room_size: (0.0 - 1.0) def. 0.2
    -> damping: (0.0 - 1.0) def. 0.02
    -> ratio: (0.0 - 1.0) def. 0.2
    
    Chorus:
    -> rate: (0.0 - 30.0) def 1.0
    -> depth (0.0 - 1.0) def 0.25
    -> mix (0.0 - 1.0) def 0.5
    
    Pitch shifter:
    -> shift: (-24 - 24) def 12
"""