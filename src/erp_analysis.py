import pickle

import autoreject
import matplotlib
import mne

matplotlib.use('qtAgg')
from src import project_config as cfg


def autoreject_analysis(epochs, subject_name):
    cfg.init_config(subject_name)
    ar = autoreject.AutoReject(n_interpolate=[1, 2, 3, 4], random_state=11,
                               n_jobs=4, verbose=True)
    ar.fit(epochs)
    epochs_ar, reject_log = ar.transform(epochs, return_log=True)

    # Save results of the autoreject
    reject_log_file = open(cfg.subject_processed_file_path /
                           f"{cfg.current_subject}_autoreject-reject_log",
                           'wb')
    pickle.dump(reject_log, reject_log_file)
    reject_log_file.close()
    epochs_ar.save(cfg.subject_processed_file_path /
                   f"{cfg.current_subject}_epochs_autoreject-epo.fif.gz")

    return epochs_ar


def create_report_for_subject(epochs):
    # Baseline Correction
    epochs.apply_baseline(baseline=(-2.4, -2.2))

    # Create report
    report = mne.Report(title='Epochs')
    report.add_epochs(epochs=epochs,
                      title=f'Epochs from subject {cfg.current_subject}')

    # Crop epochs for better viewing
    epochs.crop(tmin=-0.2, tmax=0.8)

    # Sanity check for all epochs without seperating the conditions
    evoked_all = epochs.average()
    evoked_all.plot_joint(times=[-0.2, 0, 0.2, 0.4, 0.6, 0.8])
    evoked_all.plot(gfp=True, spatial_colors=True)
    evoked_all.plot_image(show_names="all")
    topo_fig = mne.viz.plot_compare_evokeds(
        dict(all=list(epochs.iter_evoked())), axes="topo", ci=True)

    # Add to report
    report.add_evokeds(evokeds=evoked_all,
                       titles=[
                           f'Evoked from {cfg.current_subject} (Autorejected)'],
                       n_jobs=3)
    report.add_figure(topo_fig, title="topo", section="Evoked Topo Map")

    # Equalize event counts
    epochs.equalize_event_counts()

    # Topoplot for congruent Incongruent and neutral
    conditions = ['Congruent', 'Incongruent', 'Neutral']
    evokeds = dict(Congruent=list(epochs['Congruent'].iter_evoked()),
                   Incongruent=list(epochs['Incongruent'].iter_evoked()),
                   Neutral=list(epochs['Neutral'].iter_evoked()))

    cin_fig = mne.viz.plot_compare_evokeds(evokeds, axes="topo", ci=True)

    channels = ["Oz", "POz", "Pz", "Cz", "Fz", "FCz"]
    for channel in channels:
        fig = mne.viz.plot_compare_evokeds(evokeds, picks=channel, ci=True,
                                           show=False)
        report.add_figure(fig,
                          title=f"Congruent Invongruent Neutral Comparison at channel {channel}",
                          section="Congruent Invongruent Neutral Comparison")

    # Contra-ipsi ERP analysis
    query = "Congruency == '{}' and Target_location == '{}'"
    all_evokeds = {f"{c}/{t}": epochs[query.format(c, t)].average()
                   for t in epochs.metadata.Target_location.unique()
                   for c in epochs.metadata.Congruency.unique()}

    congruent_evokeds = {f"{t}": epochs[query.format('Congruent', t)].average()
                         for t in epochs.metadata.Target_location.unique()}

    neutral_evokeds = {f"{t}": epochs[query.format('Neutral', t)].average()
                       for t in epochs.metadata.Target_location.unique()}

    incongruent_evokeds = {
        f"{t}": epochs[query.format('Incongruent', t)].average()
        for t in epochs.metadata.Target_location.unique()}

    left_evokeds = {f"{c}": epochs[query.format(c, 'Left')].average()
                    for c in epochs.metadata.Congruency.unique()}

    right_evokeds = {f"{c}": epochs[query.format(c, 'Right')].average()
                     for c in epochs.metadata.Congruency.unique()}

    left_minus_right_evoked = {c: mne.combine_evoked([
        epochs[query.format(c, 'Left')].average(),
        epochs[query.format(c, 'Right')].average()], weights=[1, -1])
        for c in epochs.metadata.Congruency.unique()}

    right_minus_left_evoked = {c: mne.combine_evoked([
        epochs[query.format(c, 'Left')].average(),
        epochs[query.format(c, 'Right')].average()], weights=[-1, 1])
        for c in epochs.metadata.Congruency.unique()}

    right_channels = mne.pick_channels_regexp(epochs.info['ch_names'],
                                              '.*[02458]$')
    left_channels = mne.pick_channels_regexp(epochs.info['ch_names'],
                                             '.*[13579]$')

    # Print contra ipsi waves for given channels
    conta_ipsi_channels = ["PO7", "PO8"]
    for channel in conta_ipsi_channels:
        titles = [f'Evoked response to Incongruent trials in {channel}',
                  f'Evoked response to Congruent trials in {channel}',
                  f'Evoked response to BM on Left in {channel}',
                  f'Evoked response to BM on Right in {channel}'
                  f'Evoked response to Neutral trials in {channel}',
                  f'Evoked response to Contra-ipsi in {channel}']
        section = "Contra and Ipsi ERP"
        fig1 = mne.viz.plot_compare_evokeds(incongruent_evokeds,
                                            legend='lower right',
                                            picks=channel, title=titles[0],
                                            show=False, show_sensors=True)

        fig2 = mne.viz.plot_compare_evokeds(congruent_evokeds,
                                            legend='lower right',
                                            picks=channel, title=titles[1],
                                            show=False, show_sensors=True)
        fig3 = mne.viz.plot_compare_evokeds(left_evokeds,
                                            legend='lower right',
                                            ylim=dict(eeg=[-5, 8]),
                                            picks=channel, title=titles[2],
                                            show=False, show_sensors=True)
        fig4 = mne.viz.plot_compare_evokeds(right_evokeds,
                                            legend='lower right',
                                            ylim=dict(eeg=[-5, 8]),
                                            picks=channel, title=titles[3],
                                            show=False, show_sensors=True)
        fig5 = mne.viz.plot_compare_evokeds(neutral_evokeds,
                                            legend='lower right',
                                            ylim=dict(eeg=[-5, 8]),
                                            picks=channel, title=titles[3],
                                            show=False, show_sensors=True)
        report.add_figure(fig1, title=titles[0], section=section)
        report.add_figure(fig2, title=titles[1], section=section)
        report.add_figure(fig3, title=titles[2], section=section)
        report.add_figure(fig4, title=titles[3], section=section)
        report.add_figure(fig5, title=titles[2], section=section)

        if channel in left_channels:
            fig6 = mne.viz.plot_compare_evokeds(right_minus_left_evoked,
                                                legend='lower right',
                                                picks=channel,
                                                title=titles[4],
                                                show=False,
                                                show_sensors=True)
            report.add_figure(fig6, title=titles[3], section=section)
        elif channel in right_channels:
            fig6 = mne.viz.plot_compare_evokeds(left_minus_right_evoked,
                                                legend='lower right',
                                                ylim=dict(eeg=[-5, 8]),
                                                picks=channel, title=titles[3],
                                                show=False, show_sensors=True)
            report.add_figure(fig6, title=titles[3], section=section)

    report.save(
        cfg.subject_output_folder / f"{cfg.current_subject}_report.html",
        overwrite=True)
