import mne
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


# Define paths
subjects_path = Path('/auto/data2/oelmas/bioprediction/EEG_data')
subject_name = 'sezan3_17_05'
subject_eeg_folder = subjects_path / subject_name / 'eeg'
eeglab_preprocessed_set_file = subject_eeg_folder / 'sezan3_17_05_ft_refFCz_removeBads_avgReref_ica_finrej.set'

stimulus_id = {
    "Stimulus/Congruent/Left/Walk":11,"Stimulus/Congruent/Left/Kick":12,
    "Stimulus/Congruent/Right/Walk":13, "Stimulus/Congruent/Right/Kick":14,
    "Stimulus/Incongruent/Left/Walk":21, "Stimulus/Incongruent/Left/Kick":22,
    "Stimulus/Incongruent/Right/Walk":23, "Stimulus/Incongruent/Right/Kick": 24,
    "Stimulus/Neutral/Left/Walk":31, "Stimulus/Neutral/Left/Kick":32,
    "Stimulus/Neutral/Right/Walk":33, "Stimulus/Neutral/Right/Kick":34 }

all_events_id = stimulus_id.copy()
all_events_id.update({
    'Cue/Walk':10,
    'Cue/Kick':20,
    'Cue/Neutral':30,

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


########################################################################################################################
# %%
########################################################################################################################
from_raw_events_path = subject_eeg_folder / 'sezan_raw_events.txt'

# Read events from event txt file (eeglab output)
all_events = pd.read_csv(from_raw_events_path, header=0,  sep='\t',
                              dtype={'latency':int, 'channel':int, 'urevent':int},
                              skiprows=[1], usecols=['latency', 'channel', 'type', 'urevent'],
                              converters={'type': lambda x : int(x[-2:])})
from_raw_events_stimulus_rows = all_events.loc[all_events['type'].isin(list(stimulus_id.values()))]

from_rejected_epochs_events_path = subject_eeg_folder / 'eeglab_events.txt'

# Read events from event txt file (eeglab output)
post_rejection_events = pd.read_csv(from_rejected_epochs_events_path, header=0,  sep='\t',
                                    dtype={'urevent': int},skiprows=[1], usecols=['urevent', 'type'],
                                    converters={'type': lambda x : int(x[-2:])})
post_rejection_events = post_rejection_events.loc[post_rejection_events['type'].isin(list(stimulus_id.values()))]
dropped_trials = np.setdiff1d(from_raw_events_stimulus_rows['urevent'], post_rejection_events['urevent'])

all_events.drop(all_events[all_events.urevent.isin(dropped_trials)].index, inplace=True)
all_events.drop('urevent', axis='columns', inplace=True)
all_events.reset_index(drop=True)
all_events = all_events.to_numpy(dtype=int)

########################################################################################################################
# %% Metadata
########################################################################################################################

metadata_tmin, metadata_tmax = -2.3,  2.8

# auto-create metadata
# this also returns a new events array and an event_id dictionary. we'll see
# later why this is important
metadata, events, event_id = mne.epochs.make_metadata(
    events=all_events, event_id=all_events_id, row_events=list(stimulus_id.keys()),
    keep_first=['Stimulus', 'Response', 'Cue'],
    tmin=metadata_tmin, tmax=metadata_tmax, sfreq=1000.) # Later raw.info['sfreq']
metadata.reset_index(drop=True, inplace=True)

metadata = metadata[['first_Stimulus', 'first_Cue', 'first_Response', 'Cue', 'Response']]
metadata.columns = ['Condition', 'Cue', 'Response', 'Cue_latency', 'Response_latency']

metadata = pd.concat([
    metadata,
    metadata['Condition'].copy().str.split('/', expand=True).rename(
        columns={0: 'Congruency', 1:'Target_location', 2:'Action'})
], axis='columns')

metadata['Response_correct'] = (metadata['Response'].str.split('/').str.get(-1) == 'Correct')
metadata = metadata.reindex(columns=['Condition', 'Cue', 'Action', 'Congruency', 'Target_location', 'Response',
                                     'Response_correct', 'Cue_latency', 'Response_latency'])

# %%

baseline_period = (-2.4, -2.2)
epochs = mne.io.read_epochs_eeglab(eeglab_preprocessed_set_file, events=events, event_id=stimulus_id)
epochs.apply_baseline(baseline=baseline_period)
epochs.metadata = metadata



# right_channels = mne.pick_channels_regexp(epochs.info['ch_names'], '.*[02458]$')
# left_channels = mne.pick_channels_regexp(epochs.info['ch_names'], '.*[13579]$')
# Create ROIs by checking channel labels
selections = mne.channels.make_1020_channel_selections(epochs.info, midline="12z")

# %%
epochs.metadata = metadata
orig_epochs = epochs.copy()

# %%
epochs.crop(tmin=0, tmax=1.5)
query = "Congruency == '{}' and Target_location == '{}'"


# %%
epochs.crop(tmin=0, tmax=0.5)
all_evokeds = {f"{c}/{t}": epochs[query.format(c, t)].average()
               for t in epochs.metadata.Target_location.unique()
               for c in epochs.metadata.Congruency.unique()}
congruent_evokeds = {f"{t}": epochs[query.format('Congruent', t)].average()
                           for t in epochs.metadata.Target_location.unique()}
left_evokeds = {f"{c}": epochs[query.format(c, 'Left')].average()
                for c in epochs.metadata.Congruency.unique()}
right_evokeds = {f"{c}": epochs[query.format(c, 'Right')].average()
                 for c in epochs.metadata.Congruency.unique()}
for channel in ["PO7", "PO8"]:
    mne.viz.plot_compare_evokeds(all_evokeds,
                                 colors={'Congruent':0, 'Incongruent':1, 'Neutral':2},
                                 linestyles={'Left':'solid', 'Right':'dashed'},
                                 legend='lower right',
                                 picks=channel, title=f'Evoked response in {channel}')

    mne.viz.plot_compare_evokeds(congruent_evokeds,
                                 legend='lower right',
                                 picks=channel, title=f'Evoked response to Congruent trials in {channel}')

    mne.viz.plot_compare_evokeds(left_evokeds,
                                 legend='lower right',
                                 ylim=dict(eeg=[-5, 8]),
                                 picks=channel, title=f'Evoked response to BM on Left in {channel}')

    mne.viz.plot_compare_evokeds(right_evokeds,
                                 legend='lower right',
                                 ylim=dict(eeg=[-5, 8]),
                                 picks=channel, title=f'Evoked response to BM on Right in {channel}')

# %%
left_minus_right_evoked = { c : mne.combine_evoked([
                                    epochs[query.format(c, 'Left')].average(),
                                    epochs[query.format(c, 'Right')].average()], weights=[1, -1])
                  for c in epochs.metadata.Congruency.unique() }

right_minus_left_evoked = { c : mne.combine_evoked([
                                    epochs[query.format(c, 'Left')].average(),
                                    epochs[query.format(c, 'Right')].average()], weights=[-1, 1])
                  for c in epochs.metadata.Congruency.unique() }
# %%
mne.viz.plot_compare_evokeds(left_minus_right_evoked, legend='lower right',
                             picks='PO8', title=f'Contra-ipsi evoked response in PO8')

mne.viz.plot_compare_evokeds(right_minus_left_evoked, legend='lower right',
                             picks='PO7', title='Contra-ipsi evoked response in PO7')



