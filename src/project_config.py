import sys
from pathlib import Path

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]
this.raw_data_path = Path(
    '/Users/huseyinelmas/CCNLAB/BP_EEG_Analysis/data')
this.output_path = Path(
    '/Users/huseyinelmas/CCNLAB/BP_EEG_Analysis/results')
this.exec_log_path = Path(
    '/Users/huseyinelmas/CCNLAB/BP_EEG_Analysis/logs')

# Constants
this.event_code_to_stimulus_id = {
    "Stimulus/Congruent/Left/Walk": 11, "Stimulus/Congruent/Left/Kick": 12,
    "Stimulus/Congruent/Right/Walk": 13, "Stimulus/Congruent/Right/Kick": 14,
    "Stimulus/Incongruent/Left/Walk": 21, "Stimulus/Incongruent/Left/Kick": 22,
    "Stimulus/Incongruent/Right/Walk": 23,
    "Stimulus/Incongruent/Right/Kick": 24,
    "Stimulus/Neutral/Left/Walk": 31, "Stimulus/Neutral/Left/Kick": 32,
    "Stimulus/Neutral/Right/Walk": 33, "Stimulus/Neutral/Right/Kick": 34}

this.event_code_to_all_events_ids = this.event_code_to_stimulus_id.copy()
this.event_code_to_all_events_ids.update({
    'Cue/Kick': 10,
    'Cue/Walk': 20,
    'Cue/Neutral': 30,

    'Response/Congruent/Left/Walk/Correct': 51,
    'Response/Congruent/Left/Walk/Incorrect': 52,
    'Response/Congruent/Left/Kick/Correct': 53,
    'Response/Congruent/Left/Kick/Incorrect': 54,

    'Response/Congruent/Right/Walk/Correct': 55,
    'Response/Congruent/Right/Walk/Incorrect': 56,
    'Response/Congruent/Right/Kick/Correct': 57,
    'Response/Congruent/Right/Kick/Incorrect': 58,

    'Response/Incongruent/Left/Walk/Correct': 61,
    'Response/Incongruent/Left/Walk/Incorrect': 62,
    'Response/Incongruent/Left/Kick/Correct': 63,
    'Response/Incongruent/Left/Kick/Incorrect': 64,

    'Response/Incongruent/Right/Walk/Correct': 65,
    'Response/Incongruent/Right/Walk/Incorrect': 66,
    'Response/Incongruent/Right/Kick/Correct': 67,
    'Response/Incongruent/Right/Kick/Incorrect': 68,

    'Response/Neutral/Left/Walk/Correct': 71,
    'Response/Neutral/Left/Walk/Incorrect': 72,
    'Response/Neutral/Left/Kick/Correct': 73,
    'Response/Neutral/Left/Kick/Incorrect': 74,

    'Response/Neutral/Right/Walk/Correct': 75,
    'Response/Neutral/Right/Walk/Incorrect': 76,
    'Response/Neutral/Right/Kick/Correct': 77,
    'Response/Neutral/Right/Kick/Incorrect': 78
})

this.id_to_event_code = {v: k for k, v in
                         this.event_code_to_all_events_ids.items()}
this.condition_color_dict = \
    {1: 'red',
     2: 'lightcoral',
     3: 'rosybrown',
     4: 'blue',
     5: 'lightblue',
     6: 'lightsteelblue',
     7: 'springgreen',
     8: 'palegreen',
     9: 'darkseagreen',
     -1: 'black'
     }

this.current_subject = None


def init_config(name):
    if this.current_subject is None:
        this.current_subject = name

        this.subject_path = this.raw_data_path / this.current_subject
        this.subject_eeg_folder = this.raw_data_path / this.current_subject \
                                  / 'eeg'
        this.subject_behavior_folder = this.raw_data_path / \
                                       this.current_subject / 'behavior'
        this.subject_output_folder = this.output_path / this.current_subject
        this.subject_processed_file_path = this.subject_eeg_folder / 'processed'
        this.subject_preprocessed_file_path = \
            this.subject_eeg_folder / 'processed' / \
            f"{this.current_subject}_preprocessed.set"
