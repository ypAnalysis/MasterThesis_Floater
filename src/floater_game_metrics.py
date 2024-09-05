# import packages
import numpy as np
import floater_processing as proc


# calculate duration
def calc_duration(phases, data_tagging, t_session_begin):
    durations = []

    for phase in phases["phase"]:
        # get start & end frame for each phase
        f_start = proc.time_to_index(phases.loc[phases["phase"] == phase, "phase_begin"].item(), t_session_begin / 1000)
        f_end = proc.time_to_index(phases.loc[phases["phase"] == phase, "phase_end"].item(), t_session_begin / 1000)

        # create list of all position phases of the current phase
        phase_labels = [label for label in data_tagging[data_tagging["possession"] == "pos_change"]["t_start_offset"].values if f_start <= label <= f_end]
        pos_phases = []
        current_start = f_start

        for frame in phase_labels:
            current_end = frame - 1
            pos_phases.append((current_start, current_end))
            current_start = frame

        if current_start <= f_end:
            pos_phases.append((current_start, f_end))

        # create a list of all calculated position phase durations
        pos_phase_durations = [(pos_phase_end - pos_phase_start + 1) / 20 for pos_phase_start, pos_phase_end in pos_phases]

        durations.append(pos_phase_durations)

    return durations


# get outcome
def get_outcome(labels):
    results_outcome = []
    for phase in labels:
        outcome = phase[np.isin(phase[:, 0], ["1", "2", "3", "4"])][:, 0]
        outcome = outcome.astype(int).tolist()
        results_outcome.append(outcome)

    return results_outcome


# get number of ball possession phases
def calc_ball_pos_phases(results_duration):
    ball_pos_phases = []
    for phase in results_duration:
        phase_ball_pos_phases = len(phase)
        ball_pos_phases.append(phase_ball_pos_phases)

    return ball_pos_phases
