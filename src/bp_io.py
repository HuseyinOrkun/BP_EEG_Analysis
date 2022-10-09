import glob

import mne
import numpy as np
import pandas as pd

from src import project_config as cfg


def read_eeglab_preprocessed_file(subject_name, file_name):
    from_raw_events_path = cfg.subject_eeg_folder / "raw_events.txt"
    eeglab_preprocessed_set_file = file_name

    # Read events from event txt file (eeglab output)
    all_events = pd.read_csv(from_raw_events_path, header=0, sep='\t',
                             dtype={'latency': int, 'channel': int,
                                    'urevent': int},
                             skiprows=[1],
                             usecols=['latency', 'channel', 'type', 'urevent'],
                             converters={'type': lambda x: int(x[-2:])})

    from_raw_events_stimulus_rows = all_events.loc[
        all_events['type'].isin(list(cfg.event_code_to_stimulus_id.values()))]

    from_rejected_epochs_events_path = cfg.subject_eeg_folder / "events_processed.txt"

    # Read events from event txt file (eeglab output)
    post_rejection_events = pd.read_csv(from_rejected_epochs_events_path,
                                        header=0, sep='\t',
                                        dtype={'urevent': int}, skiprows=[1],
                                        usecols=['urevent', 'type'],
                                        converters={
                                            'type': lambda x: int(x[-2:])})
    post_rejection_events = post_rejection_events.loc[
        post_rejection_events['type'].isin(
            list(cfg.event_code_to_stimulus_id.values()))]

    dropped_trials = np.setdiff1d(from_raw_events_stimulus_rows['urevent'],
                                  post_rejection_events['urevent'])

    all_events.drop(all_events[all_events.urevent.isin(dropped_trials)].index,
                    inplace=True)
    all_events.drop('urevent', axis='columns', inplace=True)
    all_events.reset_index(drop=True)
    all_events = all_events.to_numpy(dtype=int)

    ########################################################################################################################
    # Metadata
    ########################################################################################################################
    # %%

    metadata_tmin, metadata_tmax = -2.2, 2.7

    # auto-create metadata
    # this also returns a new events array and an event_id dictionary. we'll see
    # later why this is important
    metadata, events, event_id = mne.epochs.make_metadata(
        events=all_events, event_id=cfg.event_code_to_all_events_ids,
        row_events=list(cfg.event_code_to_stimulus_id.keys()),
        keep_first=['Stimulus', 'Response', 'Cue'],
        tmin=metadata_tmin, tmax=metadata_tmax,
        sfreq=1000.)  # Later raw.info['sfreq']
    metadata.reset_index(drop=True, inplace=True)

    metadata = metadata[
        ['first_Stimulus', 'first_Cue', 'first_Response', 'Cue', 'Response']]
    metadata.columns = ['Condition', 'Cue', 'Response', 'Cue_latency',
                        'Response_latency']

    metadata = pd.concat([
        metadata,
        metadata['Condition'].copy().str.split('/', expand=True).rename(
            columns={0: 'Congruency', 1: 'Target_location', 2: 'Action'})
    ], axis='columns')

    metadata['Response_correct'] = (
            metadata['Response'].str.split('/').str.get(-1) == 'Correct')
    metadata = metadata.reindex(
        columns=['Condition', 'Cue', 'Action', 'Congruency', 'Target_location',
                 'Response',
                 'Response_correct', 'Cue_latency', 'Response_latency'])

    epochs = mne.io.read_epochs_eeglab(eeglab_preprocessed_set_file,
                                       events=events,
                                       event_id=cfg.event_code_to_stimulus_id)

    epochs.metadata = metadata
    return epochs


def read_all_subject_files(kind="evoked"):
    all_subject_epochs = []
    for file_path in glob.glob(str(cfg.raw_data_path) + "/*/*/*/*epo.fif.gz"):
        if kind == "evoked":
            epochs = mne.read_epochs(file_path)
            all_subject_epochs.append(epochs)
    return all_subject_epochs
