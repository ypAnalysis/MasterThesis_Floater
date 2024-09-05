# import packages
import os
import numpy as np
import pandas as pd
import time
import datetime
from floodlight import XY
import matplotlib
matplotlib.use("Qt5Agg")


# read and process tagging data
def read_tagging_data(folder_path, date, offsets):
    all_jsonl = pd.DataFrame()

    # get all tagging files
    file_list = [f for f in os.listdir(folder_path) if f.startswith(date) and "tagging" in f]

    # process and concat all files
    for i, filename in enumerate(file_list):
        single_jsonl = pd.read_json(os.path.join(folder_path, filename), lines=True)
        single_jsonl["t_start_offset"] = round((single_jsonl["t_start"] + offsets[i]) / 30 * 20)
        single_jsonl["t_start_offset"] = single_jsonl["t_start_offset"].astype("int64")
        all_jsonl = pd.concat([all_jsonl, single_jsonl], ignore_index=True)

    # add labels
    labels_df = pd.json_normalize(all_jsonl["labels"])
    all_jsonl = all_jsonl.join(labels_df[["possession", "outcome", "technical"]])

    return all_jsonl


# get begin and end of phases
def get_phases_overview(stats_xlsx):
    xlsx_file = pd.ExcelFile(stats_xlsx)

    # extract begin and end of each phase
    phases_duration = pd.read_excel(xlsx_file, sheet_name=0, usecols=[3, 4])
    phases_begin = phases_duration.iloc[1:, 0].to_list()
    phases_end = phases_duration.iloc[1:, 1].to_list()

    # iterate over Excel sheet for each phase
    phases_data = []
    for sheet_name, begin, end in zip(xlsx_file.sheet_names[2:-1], phases_begin, phases_end):
        phases_data.append({'phase': sheet_name, 'phase_begin': begin, 'phase_end': end})

    phases_df = pd.DataFrame(phases_data, columns=['phase', 'phase_begin', 'phase_end'])

    return phases_df


# transform timestamp to index of xyobj
def time_to_index(timestamp, t_start, framerate=20, time_format="%d.%m.%Y %H:%M:%S"):
    if type(timestamp) == str:
        t_utc = int(time.mktime(datetime.datetime.strptime(timestamp, time_format).timetuple()))

    t_diff = t_utc - t_start
    frame = int(t_diff * framerate)

    return frame


# get ball on the pitch
def get_ball_on_pitch(x, y):
    return -49.97 <= x <= 27.03 and -25.5 <= y <= 25.5


# reduce player_xyobj
def reduce_player_obj(selection, player_xyobj, meta_data_links, phases, data_tagging, t_session_begin, floater_player, start_att_player, start_def_player, all_player):
    final_data = []
    phase_number = -1
    player_list = floater_player if selection == "floater" else all_player

    # process for each phase
    for phase, trial in zip(phases["phase"], player_list):
        phase_number += 1

        # get start & end frame for each phase
        f_start = time_to_index(phases.loc[phases["phase"] == phase, "phase_begin"].item(), t_session_begin / 1000)
        f_end = time_to_index(phases.loc[phases["phase"] == phase, "phase_end"].item(), t_session_begin / 1000)

        # reduce player_xyobj for floater_player & all_player
        if selection == "floater" or selection == "all":
            coordinates = []
            for player in trial:
                coordinates.append(2 * meta_data_links['"X"'][f'" Player {player}"'])
                coordinates.append(2 * meta_data_links['"X"'][f'" Player {player}"'] + 1)

            selected_data = XY(player_xyobj[f_start:f_end+1, coordinates], framerate=20)

        # reduce player_xyobj for attacker_player (start_att_player) & defender_player (start_def_player)
        else:
            selected_rows = player_xyobj[f_start:f_end+1, :]

            start_attacker = True
            defender_player = []
            attacker_player = []

            # add respective attackers & defenders for each frame considering a possible change of possession
            for i in range(len(selected_rows)):
                if i in data_tagging[data_tagging["possession"] == "pos_change"]["t_start_offset"].values - f_start:
                    if start_attacker:
                        attacker_player.append(floater_player[phase_number] + start_def_player[phase_number])
                        defender_player.append(start_att_player[phase_number])
                    else:
                        attacker_player.append(floater_player[phase_number] + start_att_player[phase_number])
                        defender_player.append(start_def_player[phase_number])

                    start_attacker = not start_attacker
                else:
                    if start_attacker:
                        attacker_player.append(floater_player[phase_number] + start_att_player[phase_number])
                        defender_player.append(start_def_player[phase_number])
                    else:
                        attacker_player.append(floater_player[phase_number] + start_def_player[phase_number])
                        defender_player.append(start_att_player[phase_number])

            coordinates = []
            pos_player = attacker_player if selection == "attacker" else defender_player

            for frame in pos_player:
                columns = []
                for player in frame:
                    columns.append(2 * meta_data_links['"X"'][f'" Player {player}"'])
                    columns.append(2 * meta_data_links['"X"'][f'" Player {player}"'] + 1)
                coordinates.append(columns)

            selected_data = []
            for i in range(selected_rows.shape[0]):
                selected_idx = coordinates[i]
                selected_row_values = selected_rows[i, selected_idx]
                selected_data.append(selected_row_values)
            selected_data = XY(np.array(selected_data), framerate=20)

        final_data.append(selected_data)

    return final_data


# reduce ball_obj & label_obj
def reduce_other_obj(player_list, ball_xyobj, phases, data_tagging, t_session_begin):
    final_data = []
    phase_number = -1

    # process for each phase
    for phase in phases["phase"]:
        phase_number += 1

        # get start & end frame for each phase
        f_start = time_to_index(phases.loc[phases["phase"] == phase, "phase_begin"].item(), t_session_begin / 1000)
        f_end = time_to_index(phases.loc[phases["phase"] == phase, "phase_end"].item(), t_session_begin / 1000)

        # reduce ball_xyobj
        if player_list == "balls":
            selected_rows = ball_xyobj[f_start:f_end + 1, :]
            selected_data = []
            last_ball = None

            for frame in selected_rows:
                # get (x, y) coords for each ball
                balls_x_y = [(frame[0], frame[1]), (frame[2], frame[3]), (frame[4], frame[5])]

                # check which ball is on the pitch
                ball_on_pitch = [get_ball_on_pitch(ball[0], ball[1]) for ball in balls_x_y]

                # append respective row
                if any(ball_on_pitch):
                    if last_ball is not None and ball_on_pitch[last_ball]:
                        selected_data.append(balls_x_y[last_ball])
                    else:
                        for i, boolean in enumerate(ball_on_pitch):
                            if boolean:
                                selected_data.append(balls_x_y[i])
                                last_ball = i
                                break
                else:
                    selected_data.append((np.nan, np.nan))
                    last_ball = None

            selected_data = XY(np.array(selected_data), framerate=20)

        # reduce labels
        elif player_list == "labels":
            selected_data = np.full((f_end - f_start + 1, 2), None, dtype=object)
            selected_data[0, 0] = "start"
            selected_data[-1, 0] = "end"
            selected_data[:, 1] = phase

            for f_label in data_tagging.loc[(data_tagging["possession"] != "") | (data_tagging["outcome"] != "") | (data_tagging["technical"] != ""), "t_start_offset"]:
                if f_start < f_label < f_end:
                    if data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["possession"] != "":
                        label = data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["possession"]
                    elif data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["outcome"] != "":
                        label = data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["outcome"]
                    elif data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["technical"] != "":
                        label = data_tagging[data_tagging["t_start_offset"] == f_label].iloc[0]["technical"]
                    label_offset = f_label - f_start
                    selected_data[label_offset, 0] = label

        final_data.append(selected_data)

    return final_data


# extract relevant cells (trial & player) and labels
def extract_slice_player_label(player_xyobj, ball_xyobj, data_structure, meta_data_links, phases, data_tagging, t_session_begin):
    # extract relevant players from excel file
    floater_player = []
    start_att_player = []
    start_def_player = []
    all_player = []

    for index, row in data_structure.iterrows():
        floater = (row.iloc[2], row.iloc[3])
        floater_player.append(floater)

        start_att = tuple(int(x) for x in row.iloc[4].split(","))
        start_att_player.append(start_att)

        start_def = tuple(int(x) for x in row.iloc[5].split(","))
        start_def_player.append(start_def)

        all_player.append(floater + start_att + start_def)

    # reduce player_xyobj
    final_floater_data_list = reduce_player_obj("floater", player_xyobj, meta_data_links, phases, data_tagging, t_session_begin, floater_player, start_att_player, start_def_player, all_player)
    final_attacker_data_list = reduce_player_obj("attacker", player_xyobj, meta_data_links, phases, data_tagging, t_session_begin, floater_player, start_att_player, start_def_player, all_player)
    final_defender_data_list = reduce_player_obj("defender", player_xyobj, meta_data_links, phases, data_tagging, t_session_begin, floater_player, start_att_player, start_def_player, all_player)
    final_all_data_list = reduce_player_obj("all", player_xyobj, meta_data_links, phases, data_tagging, t_session_begin, floater_player, start_att_player, start_def_player, all_player)

    # reduce ball_xyobj
    final_ball_data_list = reduce_other_obj("balls", ball_xyobj, phases, data_tagging, t_session_begin)

    # reduce labels
    final_labels_list = reduce_other_obj("labels", ball_xyobj, phases, data_tagging, t_session_begin)

    return final_floater_data_list, final_attacker_data_list, final_defender_data_list, final_all_data_list, final_ball_data_list, final_labels_list


# check xyobj for nans
def detect_nans(xyobj_list):
    nan_details = []

    for i, xy_obj in enumerate(xyobj_list):
        xy_array = xy_obj.xy

        # count NaNs per column
        nan_counts = np.isnan(xy_array).sum(axis=0)

        # get row of first NaN
        first_nan_indices = np.argmax(np.isnan(xy_array), axis=0)
        first_nan_indices[first_nan_indices == 0] = -1

        nan_details.append((nan_counts, first_nan_indices))

        print(f"XY object {i + 1}:")
        for col_index, (count, first_index) in enumerate(zip(nan_counts, first_nan_indices)):
            if count > 0:
                print(f"  Column {col_index + 1}: {count} NaN values, first NaN at row {first_index + 1}")
            else:
                print(f"  Column {col_index + 1}: No NaN values")


# interpolate & cut out runs
def interpolate_cut_runs(xy_floater, xy_defender, xy_attacker, xy_all, xy_balls, labels, phases):
    # interpolate NaNs
    for x in [xy_floater, xy_defender, xy_attacker, xy_all, xy_balls]:
        for i in range(8):
            xy_array = x[i].xy
            xy_df = pd.DataFrame(xy_array)

            # linear interpolation
            xy_df_interpolated = xy_df.interpolate(method='linear', limit_direction='both', axis=0)
            xy_df_interpolated = xy_df_interpolated.fillna(method='bfill').fillna(method='ffill')

            x[i].xy = xy_df_interpolated.to_numpy()

            print(f"NaNs in XY object {i + 1} interpolated and filled.")

    # cut out last four runs
    xy_all = xy_all[:8]
    xy_defender = xy_defender[:8]
    xy_attacker = xy_attacker[:8]
    xy_floater = xy_floater[:8]
    xy_balls = xy_balls[:8]
    labels = labels[:8]
    phases = phases.iloc[:8]

    return xy_floater, xy_defender, xy_attacker, xy_all, xy_balls, labels, phases


def xy_to_one_direction(xyobj, phases, data_tagging, t_session_begin):
    xy_one_direction = []

    # for each phase
    for phase, phase_xy in zip(phases["phase"], xyobj):
        # get start & end frame for each phase
        f_start = time_to_index(phases.loc[phases["phase"] == phase, "phase_begin"].item(), t_session_begin / 1000)
        f_end = time_to_index(phases.loc[phases["phase"] == phase, "phase_end"].item(), t_session_begin / 1000)

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

        # get x/y coordinates
        pos_phases = []
        start_index = 0

        for index, pos_phase_length in enumerate(pos_phases_length):
            end_index = start_index + pos_phase_length
            pos_phase_xy = phase_xy[start_index:end_index]

            # mirror data if uneven
            if index % 2 != 0:
                pos_phase_xy = -pos_phase_xy

            pos_phases.append(pos_phase_xy)

            start_index = end_index

        pos_phases_combined = np.concatenate(pos_phases, axis=0)

        xy_one_direction.append(XY(pos_phases_combined, framerate=20))

    return xy_one_direction
