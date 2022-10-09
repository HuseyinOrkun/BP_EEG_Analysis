clear;
close all;
addpath '/Users/huseyinelmas/eeglab2022.1'
[ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
EEG.etc.eeglabvers = '2021.1';
n_channels=64;
epoch_length = [-2.4 1.5];
% Parameters

% EEG data path
input_path='/Users/huseyinelmas/CCNLAB/BP_EEG_Analysis/data';

% Channel Location Path
chanloc_file = '/Users/huseyinelmas/CCNLAB/BioPrediction/EEG_Analysis/CACS-64_REF.bvef';

% Participants name 
participant_name = 's30';
eeg_fname = 'bp-eeg-pilot-0030.vhdr';
output_path = [input_path  '/'  participant_name  '/eeg/processed'];

% EEG data file name
dset_path = fullfile(input_path, participant_name, 'eeg');

% Load dataset
current_dset=0;
EEG = pop_loadbv(dset_path, eeg_fname);
dset_name=participant_name;
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );
pop_expevents(EEG, [dset_path '/raw_events.txt'], 'samples');

% Downsample if necessary
if (EEG.srate > 500)
    current_dset = current_dset+1;
    EEG = pop_resample( EEG, 500);
    dset_name = [dset_name '_resamp'];
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off');
end
eeglab redraw


% Filter 1 and 40Hz
current_dset = current_dset+1;
EEG = pop_eegfiltnew(EEG, 'locutoff',1,'plotfreqz',1);
EEG = eeg_checkset( EEG );

EEG = pop_eegfiltnew(EEG, 'hicutoff',40,'plotfreqz',1);
dset_name=[dset_name '_ft'];
current_dset = current_dset+1;
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );
EEG = pop_saveset( EEG, 'filename',[dset_name '.set'],'filepath',output_path);
[ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
eeglab redraw

% Read Channel locations, Opt head center
chanlocs = loadbvef(chanloc_file);
EEG.chanlocs = chanlocs(3:66); % Does not read reference and ground electrode
EEG = eeg_checkset( EEG );
EEG = pop_chanedit(EEG, 'eval','chans = pop_chancenter( chans, [],[]);');
[ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
eeglab redraw
% Keep original EEG.
originalEEG = EEG;

%%%% Automatic channel rejection
dset_name=[dset_name '_chan_rej'];
current_dset = current_dset+1;
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion',5,'ChannelCriterion',0.8,'LineNoiseCriterion',4,'Highpass','off','BurstCriterion','off','WindowCriterion','off','BurstRejection','off','Distance','Euclidian');
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );
EEG = pop_saveset( EEG, 'filename',[dset_name '.set'],'filepath',output_path);
eeglab redraw

%%% Interpolate rejected channels
if isfield(EEG.chaninfo, 'removedchans')
    EEG.chaninfo.removedchans.labels
    n_interp = EEG.chaninfo.removedchans;
    EEG = pop_interp(EEG, originalEEG.chanlocs, 'spherical');
    current_dset = current_dset+1;
    dset_name=[dset_name '_interp'];
    [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off'); 
end

% Make FCz reference
current_dset = current_dset+1;
dset_name=[dset_name '_refFCz'];
EEG=pop_chanedit(EEG, 'append',64,'changefield',{65,'labels','FCz'},'changefield',{65,'sph_radius','1'},'changefield',{65,'sph_theta','0'},'changefield',{65,'sph_phi','0'},'changefield',{65,'theta','0'},'changefield',{65,'sph_phi','67'},'convert',{'sph2all'},'changefield',{65,'radius','0.1278'},'changefield',{65,'X','0.3907'},'setref',{'1:64','FCz'});
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off'); 
EEG = eeg_checkset( EEG );

% Reref to avg keep FCz
current_dset = current_dset+1;
dset_name=[dset_name '_avgReref'];
EEG = pop_reref( EEG, [],'refloc',struct('labels',{'FCz'},'sph_radius',{1},'sph_theta',{0},'sph_phi',{67},'theta',{0},'radius',{0.1278},'X',{0.3907},'Y',{0},'Z',{0.9205},'ref',{''},'type',{''},'urchan',{[]},'datachan',{0}));
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',dset_name,'gui','off');
EEG = eeg_checkset( EEG );

% Extract Epochs stimulus onset
dset_name = [dset_name '_ep'];
current_dset = current_dset + 1;
step_file_path = fullfile(input_path,participant_name,'eeg','processed',[dset_name '.set']);
EEG = eeg_checkset( EEG );
stimulus_event_codes = { 'S 11', 'S 12', 'S 13', 'S 14', 'S 21', 'S 22', 'S 23', 'S 24', 'S 31','S 32', 'S 33', 'S 34' };
EEG = pop_epoch( EEG, stimulus_event_codes, epoch_length, 'newname', dset_name, 'epochinfo', 'yes');
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'savenew',step_file_path,'gui','off'); 
eeglab redraw

%rejects = EEG.reject.rejjp | EEG.reject.rejmanual | EEG.reject.rejkurt;
%csvwrite([dset_path '/reject_before_ica.txt'],rejects)
%%% REJECT ARTIFACTS BY VISUAL INSPECTION AND SEMI AUTOMATIC METHODS
%%
% Artifact Rejection ICA and Artifact Rejection
%% run ICA
%% Get rejected info to a variable
reject_info = EEG.reject;
current_dset = current_dset+1;

current_dset = current_dset+1;
icachans = 1:size(EEG.data,1);
EEG = eeg_checkset( EEG );
EEG = pop_runica(EEG, 'icatype', 'runica','pca',n_channels-length(EEG.chaninfo.removedchans), 'extended',1,'interrupt','on');
[ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',[dset_name '_ica'],'gui','off'); 

% Run ICA Label
current_dset = current_dset+1;
EEG = pop_iclabel(EEG, 'default');
[ALLEEG EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);
step_file_path = fullfile(input_path,participant_name,'eeg/processed');
EEG = pop_saveset( EEG, 'filename',[dset_name '_icalabel'] ,'filepath',step_file_path);
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, current_dset,'setname',[dset_name '_ica'],'gui','off'); 
eeglab redraw

%%% Reject artifacts again
% Save rejected trials
%step_file_path = fullfile(input_path,participant_name,'eeg/processed');5
%rejects = EEG.reject.rejjp | EEG.reject.rejmanual | EEG.reject.rejkurt;
%csvwrite([step_file_path '/reject_after_ica.txt'],rejects)
%pop_expevents(EEG, [dset_path '/events_processed.txt'], 'samples');

