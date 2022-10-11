import glob
import os
import pickle

import autoreject
import matplotlib
import mne

from src import erp_analysis

matplotlib.use('qtAgg')
from matplotlib import pyplot as plt
from src import bp_io
from src import project_config as cfg

use_autoreject = False
preprocessed_filepath_list = glob.glob(
    str(cfg.raw_data_path) + '/*/*/processed/*preprocessed.set')
preprocessed_filepath_list = preprocessed_filepath_list[0:1]

# %%
for preprocessed_filepath in preprocessed_filepath_list:

    # Get subject name, init config
    subject_name = preprocessed_filepath.split("/")[-1].split("_")[0]
    cfg.init_config(subject_name)
    autorejected_epochs_file = cfg.subject_processed_file_path / \
                               f"{subject_name}_epochs_autoreject-epo.fif.gz"
    if os.path.exists(autorejected_epochs_file) and autoreject:

        # Read autorejected results
        epochs = mne.read_epochs(autorejected_epochs_file)
        reject_log_file = open(cfg.subject_processed_file_path /
                               f"{subject_name}_autoreject-reject_log", 'rb')
        reject_log = pickle.load(reject_log_file)
        reject_log_file.close()

        # Plot results of the autoreject
        reject_log.plot('horizontal')
        evoked_bad = epochs[reject_log.bad_epochs].average()
        plt.figure()
        plt.plot(evoked_bad.times, evoked_bad.data.T * 1e6, 'r', zorder=-1)
        epochs.average().plot(axes=plt.gca())
        plt.savefig(
            cfg.subject_output_folder / f"{cfg.current_subject}_autoreject-plot.png")

    elif not os.path.exists(autorejected_epochs_file) and autoreject:
        epochs = bp_io.read_eeglab_preprocessed_file(subject_name,
                                                     preprocessed_filepath)
        original_epochs = epochs.copy()
        epochs = erp_analysis.autoreject_analysis(epochs, subject_name)
    else:
        epochs = bp_io.read_eeglab_preprocessed_file(subject_name,
                                                     preprocessed_filepath)
        original_epochs = epochs.copy()
    erp_analysis.create_report_for_subject(epochs)
