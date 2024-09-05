# import packages
import numpy as np
import pandas as pd
import floater_processing as proc


# calculate technical parameters
def get_technical_parameters(labels, phases, data_tagging, t_session_begin):
    tech_parameters = []

    # get number of actions for each phase
    for phase, label_xy in zip(phases["phase"], labels):
        # get start & end frame for each phase
        f_start = proc.time_to_index(phases.loc[phases["phase"] == phase, "phase_begin"].item(), t_session_begin / 1000)
        f_end = proc.time_to_index(phases.loc[phases["phase"] == phase, "phase_end"].item(), t_session_begin / 1000)

        # create list of all possession phases of the current phase
        phase_labels = [label for label in data_tagging[data_tagging["possession"] == "pos_change"]["t_start_offset"].values if f_start <= label <= f_end]
        pos_phases = []
        current_start = f_start

        for frame in phase_labels:
            current_end = frame - 1
            pos_phases.append((current_start, current_end))
            current_start = frame

        if current_start <= f_end:
            pos_phases.append((current_start, f_end))

        # calculate frame length of each ball possession phase
        pos_phases_length = [(end - start + 1) for start, end in pos_phases]

        # get number of actions for each ball possession phase
        pos_phases_tech_parameters = []
        start_index = 0
        columns_absolute_value = ["Pass Count", "Dribbling Count", "Shot Count", "Possessions Count"]

        for pos_phase_length in pos_phases_length:
            end_index = start_index + pos_phase_length

            pos_phase_pass_successful_count = 0
            pos_phase_pass_unsuccessful_count = 0
            pos_phase_dribbling_successful_count = 0
            pos_phase_dribbling_unsuccessful_count = 0
            pos_phase_shot_successful_count = 0
            pos_phase_shot_unsuccessful_count = 0

            pos_phase_pass_successful_count += np.isin(label_xy[start_index:end_index, 0], ["pass_successful"]).sum()
            pos_phase_pass_unsuccessful_count += np.isin(label_xy[start_index:end_index, 0], ["pass_unsuccessful"]).sum()
            pos_phase_dribbling_successful_count += np.isin(label_xy[start_index:end_index, 0], ["dribbling_successful"]).sum()
            pos_phase_dribbling_unsuccessful_count += np.isin(label_xy[start_index:end_index, 0], ["dribbling_unsuccessful"]).sum()
            pos_phase_shot_successful_count += np.isin(label_xy[start_index:end_index, 0], ["shot_successful"]).sum()
            pos_phase_shot_unsuccessful_count += np.isin(label_xy[start_index:end_index, 0], ["shot_unsuccessful"]).sum()

            # Berechnung der Erfolgsquoten
            pos_phase_pass_success_rate = pos_phase_pass_successful_count / (pos_phase_pass_successful_count + pos_phase_pass_unsuccessful_count) if (pos_phase_pass_successful_count + pos_phase_pass_unsuccessful_count) > 0 else np.nan
            pos_phase_dribbling_success_rate = pos_phase_dribbling_successful_count / (pos_phase_dribbling_successful_count + pos_phase_dribbling_unsuccessful_count) if (pos_phase_dribbling_successful_count + pos_phase_dribbling_unsuccessful_count) > 0 else np.nan
            pos_phase_shot_success_rate = pos_phase_shot_successful_count / (pos_phase_shot_successful_count + pos_phase_shot_unsuccessful_count) if (pos_phase_shot_successful_count + pos_phase_shot_unsuccessful_count) > 0 else np.nan

            # Berechnung der Ballbesitzaktionen
            pos_phase_possessions_successful = pos_phase_pass_successful_count + pos_phase_dribbling_successful_count + pos_phase_shot_successful_count
            pos_phase_possessions_unsuccessful = pos_phase_pass_unsuccessful_count + pos_phase_dribbling_unsuccessful_count + pos_phase_shot_unsuccessful_count
            pos_phase_possessions_total = pos_phase_possessions_successful + pos_phase_possessions_unsuccessful
            pos_phase_possession_success_rate = pos_phase_possessions_successful / pos_phase_possessions_total if pos_phase_possessions_total > 0 else np.nan

            pos_phase_tech_parameters = pd.DataFrame({
                "Metric": ["Pass Count", "Pass %", "Dribbling Count", "Dribbling %", "Shot Count", "Shot %", "Possessions Count", "Possessions %"],
                "Value": [pos_phase_pass_successful_count + pos_phase_pass_unsuccessful_count, pos_phase_pass_success_rate, pos_phase_dribbling_successful_count + pos_phase_dribbling_unsuccessful_count, pos_phase_dribbling_success_rate,
                          pos_phase_shot_successful_count + pos_phase_shot_unsuccessful_count, pos_phase_shot_success_rate, pos_phase_possessions_total, pos_phase_possession_success_rate]
                }).set_index("Metric").T

            # divide by length of the respective ball possession phase for weighted aggregation
            for column in columns_absolute_value:
                pos_phase_tech_parameters[column] = pos_phase_tech_parameters[column] * (pos_phase_length / 4801)

            pos_phases_tech_parameters.append(pos_phase_tech_parameters)

            start_index = end_index

        tech_parameters.append(pos_phases_tech_parameters)

    return tech_parameters
