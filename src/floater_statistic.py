# import packages
import pandas as pd
import numpy as np
from statsmodels.formula.api import mixedlm


# prepare results_list to save as csv
def prepare_statistic(conditions_indices, results_list):
    results_rows = []

    for cond, indices in conditions_indices.items():
        ball_pos_phase_cond_index = 1
        for phase, idx in enumerate(indices):
            if isinstance(results_list[idx], list):
                for element in results_list[idx]:
                    if isinstance(element, (float, int)):
                        results_rows.append([cond, idx + 1, element, ball_pos_phase_cond_index, None])
                        ball_pos_phase_cond_index += 1
                    elif isinstance(element, np.ndarray):
                        for value in element:
                            results_rows.append([cond, idx + 1, value, ball_pos_phase_cond_index, None])
                        ball_pos_phase_cond_index += 1
                    else:
                        for _, row in element.iterrows():
                            for col_name, value in row.items():
                                results_rows.append([cond, idx + 1, value, ball_pos_phase_cond_index, col_name])
                        ball_pos_phase_cond_index += 1

            else:
                value = results_list[idx]
                results_rows.append([cond, idx + 1, value, ball_pos_phase_cond_index, None])
                ball_pos_phase_cond_index += 1

    results_df = pd.DataFrame(results_rows, columns=["condition", "phase", "value", "ball_pos_phase", "category"])

    return results_df


def calc_statistics(conditions_indices, results_list):
    # create dummy for aggregation
    results_dummy = results_list

    # calculate mean for each possession phase if possession phase ndarray contains values for each frame
    for index_phase, phase in enumerate(results_dummy):
        if not isinstance(phase, int):
            for index_pos_phase, pos_phase in enumerate(phase):
                if isinstance(pos_phase, np.ndarray):
                    if pos_phase.shape[0] > 50:
                        results_dummy[index_phase][index_pos_phase] = np.mean(pos_phase)
                    else:
                        continue
                else:
                    continue

    # process list of data results
    results_rows = []
    for cond, indices in conditions_indices.items():
        for phase, idx, in enumerate(indices):
            if isinstance(results_dummy[idx], (list, np.ndarray)):
                for value in results_dummy[idx]:
                    results_rows.append([cond, idx + 1, value])
            else:
                value = results_dummy[idx]
                results_rows.append([cond, idx + 1, value])

    results_df = pd.DataFrame(results_rows, columns=["condition", "phase", "value"])

    # calculate mean & std
    descr_results = results_df.groupby("condition")["value"].agg(["mean", "std"]).reset_index()

    return descr_results


def calc_statistics_speed_zones_distance(conditions_indices, results_list):
    # process list of data results
    results_rows = []
    for cond, indices in conditions_indices.items():
        for phase, idx, in enumerate(indices):
            for speed_range in ["z0_7", "z7_14", "z14_19", "z19_25", "z25", "total"]:
                results_rows.append([cond, idx + 1, speed_range, results_list[idx].loc[0, speed_range]])

    results_df = pd.DataFrame(results_rows, columns=["condition", "phase", "speed_range", "value"])

    # calculate mean & std
    descr_results = results_df.groupby(["condition", "speed_range"])["value"].agg(["mean", "std"]).reset_index()

    return descr_results


def calc_statistics_technical_parameters(conditions_indices, results_list):
    # process list of data results
    results_rows = []
    for cond, indices in conditions_indices.items():
        for phase, idx, in enumerate(indices):
            for parameter in ["Pass Count", "Pass %", "Dribbling Count", "Dribbling %", "Possessions Count", "Possessions %"]:
                results_rows.append([cond, idx + 1, parameter, results_list[idx].loc["Value", parameter]])

    results_df = pd.DataFrame(results_rows, columns=["condition", "phase", "parameter", "value"])

    # calculate mean & std
    descr_results = results_df.groupby(["condition", "parameter"])["value"].agg(["mean", "std"]).reset_index()

    return descr_results
