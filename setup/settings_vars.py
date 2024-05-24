""" Settings variables for P.E.A.T. """

# Define dictionary items
fields = {
    # Session variables
    'subject': {'type': 'str', 'value': '999'},
    'condition': {'type': 'str', 'value': 'TEST'},
    'disp_plots': {'type': 'int', 'value': 0},

    # Stimulus option variables
    'num_stim_chans': {'type': 'int', 'value': 1},
    'test_freqs': {'type': 'str', 'value': "500, 1000, 2000, 4000"},
    'duration': {'type': 'float', 'value': 2},

    # Staircase option variables
    'starting_level': {'type': 'float', 'value': 30},
    'min_level': {'type': 'float', 'value': -50},
    'max_level': {'type': 'float', 'value': 90},
    'step_sizes': {'type': 'str', 'value': "10, 5, 2"},
    'num_reversals': {'type': 'int', 'value': 5},
    'rapid_descend': {'type': 'str', 'value': 'Yes'},
    'rapid_descend_bool': {'type': 'bool', 'value': True},
    
    # Audio device variables
    'audio_device': {'type': 'int', 'value': 999},
    'channel_routing': {'type': 'str', 'value': '1'},

    # Calibration variables
    'cal_file': {'type': 'str', 'value': 'cal_stim.wav'},
    'cal_level_dB': {'type': 'float', 'value': -30.0},
    'slm_reading': {'type': 'float', 'value': 70.0},
    'slm_offset': {'type': 'float', 'value': 100.0},

    # Presentation level variables
    'adjusted_level_dB': {'type': 'float', 'value': -25.0},
    'desired_level_dB': {'type': 'float', 'value': 75},

    # Version control variables
    'config_file_status': {'type': 'int', 'value': 0},
    'check_for_updates': {'type': 'str', 'value': 'yes'},
    'version_lib_path': {'type': 'str', 'value': 
        r'\\starfile\Public\Temp\MooreT\Personal Files\admin\versions.xlsx'},
}
