# import packages
import numpy as np
from scipy.spatial import ConvexHull
from floodlight import XY, Pitch
from floodlight.models.space import DiscreteVoronoiModel
import floater_processing as proc


# calculate length-per-width ratio (LpW)
def calc_lpw(player_xyobj, phases, data_tagging, t_session_begin):
    lpw = []
    length = []
    width = []

    for phase, phase_xy in zip(phases["phase"], player_xyobj):
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

        # calculate max & min x- and y-coordinates
        max_x = np.max(phase_xy[:, ::2], axis=1)
        min_x = np.min(phase_xy[:, ::2], axis=1)
        max_y = np.max(phase_xy[:, 1::2], axis=1)
        min_y = np.min(phase_xy[:, 1::2], axis=1)

        # calculate length and width
        length_width = np.column_stack((max_x - min_x, max_y - min_y))

        # calculate length-per-width ratio
        phase_lpw = length_width[:, 0] / length_width[:, 1]
        phase_length = length_width[:, 0]
        phase_width = length_width[:, 1]

        # split for each ball possession phase
        pos_phases_lpw_list = np.split(phase_lpw, np.cumsum(pos_phases_length)[:-1])
        pos_phases_length_list = np.split(phase_length, np.cumsum(pos_phases_length)[:-1])
        pos_phases_width_list = np.split(phase_width, np.cumsum(pos_phases_length)[:-1])

        lpw.append(pos_phases_lpw_list)
        length.append(pos_phases_length_list)
        width.append(pos_phases_width_list)

    return lpw, length, width


# calculate effective playing space (EPS)
def calc_eps(player_xyobj, phases, data_tagging, t_session_begin):
    eps = []

    for phase, phase_xy in zip(phases["phase"], player_xyobj):
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

        # preallocate a time-series array for EPS
        phase_eps = np.full(phase_xy.xy.shape[0], np.nan)

        for i in range(phase_xy.xy.shape[0]):
            # extract x and y coordinates
            x_coords = phase_xy[i, 0::2]
            y_coords = phase_xy[i, 1::2]

            # compute the convex hull and its surface area
            hull = ConvexHull(np.column_stack((x_coords, y_coords)))
            phase_eps[i] = hull.area

        # split for each ball possession phase
        pos_phases_eps = np.split(phase_eps, np.cumsum(pos_phases_length)[:-1])

        eps.append(pos_phases_eps)

    return eps


# calculate space control (SC)
def calc_sc(pitch_size, att_xyobj, def_xyobj, data_structure, phases, data_tagging, t_session_begin):
    # get attacking & defending players' meta_data_links number (see floodlight.io.kinexon.get_meta_data)
    start_att_player = []
    start_def_player = []

    for index, row in data_structure.iterrows():
        start_att = tuple(int(x) for x in row.iloc[4].split(","))
        start_att_player.append(start_att)

        start_def = tuple(int(x) for x in row.iloc[5].split(","))
        start_def_player.append(start_def)

    phase_number = -1
    sc = []

    for phase, phase_xy_att, phase_xy_def in zip(phases["phase"], att_xyobj, def_xyobj):
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

        # create pitch
        if pitch_size == "zones":
            if "A-" in phase:
                pitch_inner = Pitch(xlim=(-49.97, 27.03), ylim=(-12.75, 12.75), unit="m", boundaries="flexible")

                # fit model
                dvm_inner = DiscreteVoronoiModel(pitch=pitch_inner, mesh="hexagonal")
                dvm_inner.fit(phase_xy_att, phase_xy_def)

                # calculate space control
                sc_att_inner, sc_def_inner = dvm_inner.team_controls()

                # split for each ball possession phase
                pos_phases_sc = np.split(sc_att_inner.property.flatten(), np.cumsum(pos_phases_length)[:-1])

                sc.append(pos_phases_sc)

            elif "Z-" in phase:
                pitch_upper = Pitch(xlim=(-49.97, 27.03), ylim=(12.75, 25.5), unit="m", boundaries="flexible")
                pitch_lower = Pitch(xlim=(-49.97, 27.03), ylim=(-25.5, -12.75), unit="m", boundaries="flexible")

                # fit model and calculate space control for both zones
                dvm_upper = DiscreteVoronoiModel(pitch=pitch_upper, mesh="hexagonal")
                dvm_upper.fit(phase_xy_att, phase_xy_def)
                sc_att_upper, sc_def_upper = dvm_upper.team_controls()

                dvm_lower = DiscreteVoronoiModel(pitch=pitch_lower, mesh="hexagonal")
                dvm_lower.fit(phase_xy_att, phase_xy_def)
                sc_att_lower, sc_def_lower = dvm_lower.team_controls()

                sc_att_outer = np.mean([sc_att_upper.property, sc_att_lower.property], axis=0)

                # split for each ball possession phase
                pos_phases_sc = np.split(sc_att_outer.flatten(), np.cumsum(pos_phases_length)[:-1])

                sc.append(pos_phases_sc)

        elif pitch_size == "final_third":
            phase_number += 1

            # cut xy_objs to all possession phases of the current phase & add to list
            pos_phases_xy_att = []
            pos_phases_xy_def = []
            for start, end in pos_phases:
                rel_start = start - f_start
                rel_end = end - f_start + 1
                pos_phases_xy_att.append(XY(phase_xy_att.xy[rel_start:rel_end], framerate=20))
                pos_phases_xy_def.append(XY(phase_xy_def.xy[rel_start:rel_end], framerate=20))

            # calculate SC for each ball possession phase
            phase_sc = []
            start_attacker = True

            for pos_phase, pos_phase_xy_att, pos_phase_xy_def in zip(pos_phases, pos_phases_xy_att, pos_phases_xy_def):
                # add respective attackers for each frame considering a possible change of possession
                f_start_pos_phase = pos_phase[0]
                f_end_pos_phase = pos_phase[1]

                pos_phase_attacker_player = []

                for i in range(f_end_pos_phase - f_start_pos_phase + 1):
                    if start_attacker:
                        pos_phase_attacker_player.append(start_att_player[phase_number])
                    else:
                        pos_phase_attacker_player.append(start_def_player[phase_number])

                start_attacker = not start_attacker

                # check if start_att or start_def is in possession and select respective final third
                if pos_phase_attacker_player[0] == start_att_player[phase_number]:
                    pitch = Pitch(xlim=(-49.97, -24.27), ylim=(-25.5, 25.5), unit="m", boundaries="flexible")
                else:
                    pitch = Pitch(xlim=(1.33, 27.03), ylim=(-25.5, 25.5), unit="m", boundaries="flexible")

                # fit model
                dvm = DiscreteVoronoiModel(pitch=pitch, mesh="hexagonal")
                dvm.fit(pos_phase_xy_att, pos_phase_xy_def)

                # calculate space control
                pos_phase_sc_att, pos_phase_sc_def = dvm.team_controls()

                phase_sc.append(pos_phase_sc_att.property.flatten())

            sc.append(phase_sc)

    return sc


# calculate overplayed defenders (OD)
def calc_od_max(all_xyobj, def_xyobj, balls_xyobj, phases, data_tagging, t_session_begin):
    od = []

    for phase, phase_xy_all, phase_xy_def, phase_xy_balls in zip(phases["phase"], all_xyobj, def_xyobj, balls_xyobj):
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

        # cut xy_obj to all possession phases of the current phase & add to list
        pos_phases_xy_all = []
        pos_phases_xy_def = []
        pos_phases_xy_balls = []
        for start, end in pos_phases:
            rel_start = start - f_start
            rel_end = end - f_start + 1
            pos_phases_xy_all.append(phase_xy_all.xy[rel_start:rel_end])
            pos_phases_xy_def.append(phase_xy_def.xy[rel_start:rel_end])
            pos_phases_xy_balls.append(phase_xy_balls.xy[rel_start:rel_end])

        start_attacker = True
        phase_od = []

        for index, (pos_phase_xy_all, pos_phase_xy_def, pos_phase_xy_balls) in enumerate(zip(pos_phases_xy_all, pos_phases_xy_def, pos_phases_xy_balls)):
            pos_phase_all_dist = np.zeros((len(pos_phase_xy_all), pos_phase_xy_all.shape[1] // 2))

            # calculate distance to the ball for each player
            for i in range(pos_phase_xy_all.shape[1] // 2):
                player_x = pos_phase_xy_all[:, 2 * i]
                player_y = pos_phase_xy_all[:, 2 * i + 1]
                ball_x = pos_phase_xy_balls[:, 0]
                ball_y = pos_phase_xy_balls[:, 1]

                pos_phase_all_dist[:, i] = np.sqrt((player_x - ball_x) ** 2 + (player_y - ball_y) ** 2)

            # add nearest player to the ball
            pos_phase_all_dist = np.hstack((pos_phase_all_dist, np.argmin(pos_phase_all_dist, axis=1).reshape(-1, 1)))

            # select lines in which nearest player = attacker
            attacker_rows = []
            for frame in range(pos_phase_all_dist.shape[0]):
                closest_col = int(pos_phase_all_dist[frame][-1])
                if start_attacker:
                    if closest_col in [0, 1, 2, 3, 4, 5, 6, 7]:
                        attacker_rows.append(pos_phase_all_dist[frame])
                else:
                    if closest_col in [0, 1, 8, 9, 10, 11, 12, 13]:
                        attacker_rows.append(pos_phase_all_dist[frame])

            if len(attacker_rows) == 0:
                phase_od.append(0)
            else:
                pos_phase_all_dist = np.array(attacker_rows)

                # select lines where the min. distance is < 2m
                pos_phase_all_dist = pos_phase_all_dist[np.any(pos_phase_all_dist < 2, axis=1)]

                if len(pos_phase_all_dist) == 0:
                    phase_od.append(0)
                else:
                    # select the lines where duration >= 0.8sec (>= 16 lines, because 20 Hz)
                    selected_rows = []
                    start_frame = 0

                    while start_frame <= len(pos_phase_all_dist) - 16:
                        player = pos_phase_all_dist[start_frame, -1]
                        end_frame = start_frame
                        while end_frame < len(pos_phase_all_dist) and pos_phase_all_dist[end_frame, -1] == player:
                            end_frame += 1
                        if end_frame - start_frame >= 16:
                            selected_rows.extend(range(start_frame, end_frame))

                        start_frame = end_frame

                    if len(selected_rows) == 0:
                        phase_od.append(0)
                    else:
                        # slice dataframes of defender and ball to selected lines (ball control of any attacking player)
                        pos_phase_xy_def = pos_phase_xy_def[np.unique(selected_rows)]
                        pos_phase_xy_balls = pos_phase_xy_balls[np.unique(selected_rows)]

                        # calculate distance to the goal line for each defender & the ball
                        pos_phase_xy_def_dist = np.zeros((len(pos_phase_xy_def), pos_phase_xy_def.shape[1] // 2))
                        pos_phase_xy_balls_dist = np.zeros((len(pos_phase_xy_balls), pos_phase_xy_balls.shape[1] // 2))

                        for i in range(pos_phase_xy_def.shape[1] // 2):
                            player_x = pos_phase_xy_def[:, 2 * i]
                            player_y = pos_phase_xy_def[:, 2 * i + 1]
                            if index % 2 == 0:
                                centre_goal_x = -49.97
                                centre_goal_y = 0
                            else:
                                centre_goal_x = 27.03
                                centre_goal_y = 0

                            pos_phase_xy_def_dist[:, i] = np.sqrt((player_x - centre_goal_x) ** 2 + (player_y - centre_goal_y) ** 2)

                        for i in range(pos_phase_xy_balls.shape[1] // 2):
                            ball_x = pos_phase_xy_balls[:, 2 * i]
                            ball_y = pos_phase_xy_balls[:, 2 * i + 1]
                            if index % 2 == 0:
                                centre_goal_x = -49.97
                                centre_goal_y = 0
                            else:
                                centre_goal_x = 27.03
                                centre_goal_y = 0

                            pos_phase_xy_balls_dist[:, i] = np.sqrt((ball_x - centre_goal_x) ** 2 + (ball_y - centre_goal_y) ** 2)

                        # calculate maximum number of defenders who are further away from the centre of the goal than the ball (max OD)
                        pos_phase_od = np.zeros(len(pos_phase_xy_def_dist), dtype=int)

                        for x in range(len(pos_phase_xy_def_dist)):
                            pos_phase_od[x] = np.sum(pos_phase_xy_def_dist[x, :] > pos_phase_xy_balls_dist[x])

                        pos_phase_od_max = np.max(pos_phase_od).item()

                        phase_od.append(pos_phase_od_max)

        od.append(phase_od)

    return od
