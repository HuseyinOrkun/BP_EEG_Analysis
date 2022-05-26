clear;
close all;
addpath '/Users/huseyinelmas/eeglab2021.1'
[ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
EEG.etc.eeglabvers = '2021.1';

% Parameters
% EEG data path
input_path='/Users/huseyinelmas/CCNLAB/BioPrediction/EEG_data';

% Channel Location Path
chanloc_file = '/Users/huseyinelmas/CCNLAB/BioPrediction/EEG_Analysis/CACS-64_REF.bvef';

% Participants name 
participant_name='sezan3_17_05';

% EEG data file name
eeg_fname='bp-eeg-pilot-00016sezan1705.vhdr';
dset_path = fullfile(input_path,participant_name,'eeg');


baseline_interval = [-2600 -2200];

% Load dataset
EEG = pop_loadbv(dset_path, eeg_fname);
dset_name=participant_name;
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 0,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );


% Read Channel locations
chanlocs = loadbvef(chanloc_file);
EEG.chanlocs = chanlocs(3:66); % Does not read reference and ground electrode

% Filter 1 and 50Hz
EEG = pop_eegfiltnew(EEG, 'locutoff',1,'plotfreqz',1);
EEG = eeg_checkset( EEG );
EEG = pop_eegfiltnew(EEG, 'hicutoff',50,'plotfreqz',1);
dset_name=[dset_name '_ft'];
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );

% Make FCz reference
dset_name=[dset_name '_refFCz'];
EEG=pop_chanedit(EEG, 'append',64,'changefield',{65,'labels','FCz'},'changefield',{65,'sph_radius','1'},'changefield',{65,'sph_theta','0'},'changefield',{65,'sph_phi','0'},'changefield',{65,'theta','0'},'changefield',{65,'sph_phi','67'},'convert',{'sph2all'},'changefield',{65,'radius','0.1278'},'changefield',{65,'X','0.3907'},'setref',{'1:64','FCz'});
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );

% Remove bad channels
% Remove TP9 TP10
dset_name=[dset_name '_removeBads'];
EEG = pop_select( EEG, 'nochannel',{'TP9','TP10','FC3','FC4','FC2','F7','FC1','F8'});
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 3,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );

% Reref to avg keep FCz
% TODO: Interpolate if removed channels
dset_name=[dset_name '_avgReref'];
EEG = pop_reref( EEG, [],'interpchan',[]);
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 4,'setname',dset_name,'gui','off');
EEG = eeg_checkset( EEG );

% Reref again to Mastoids, keep mastoids 
% EEG = pop_reref( EEG, [10 21] ,'keepref','on');
% [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'setname','ft_rf','gui','off');
% EEG = eeg_checkset( EEG );

% Extract Epochs stimulus onset

step_file_path = fullfile(input_path,participant_name,'processed',[dset_name '_ep.set']);
EEG = eeg_checkset( EEG );
stimulus_event_codes = { 'S 11', 'S 12', 'S 13', 'S 14', 'S 21', 'S 22', 'S 23', 'S 24', 'S 31','S 32', 'S 33', 'S 34' };
EEG = pop_epoch( EEG,stimulus_event_codes , [-2.6 1.7], 'newname', 'ft_rf_ep', 'epochinfo', 'yes');
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 5,'savenew',step_file_path,'gui','off'); 


%%
% Artifact Rejection ICA and Artifact Rejection
%% run ICA
icachans = 1:size(EEG.data,1);
EEG = eeg_checkset( EEG );
EEG = pop_runica(EEG, 'icatype', 'runica', 'extended',1,'interrupt','on');
[ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
step_file_path = fullfile(input_path,participant_name,'processed');
EEG = pop_saveset( EEG, 'filename',[dset_name '_ica'] ,'filepath',step_file_path);
% 
% % Remove baseline
% step_file_path = fullfile(input_path,participant_name,'processed','ft_rf_ep_rm.set');
% EEG = eeg_checkset( EEG );
% EEG = pop_rmbase( EEG,  baseline_interval,[]);
% [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 6,'setname','ft_rf_ep_rm','savenew',step_file_path,'gui','off'); 
% eeglab redraw
