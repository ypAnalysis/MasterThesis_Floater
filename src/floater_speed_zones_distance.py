# import packages
import pandas as pd
from floodlight.models.kinematics import VelocityModel
import floater_processing as proc
import matplotlib
matplotlib.use('module://backend_interagg')


# calculate speed zone distances
def calc_speed_zones_distance(player_xyobj, phases, data_tagging, t_session_begin):
    speed_zones_distance = []

    # calculate speed zones distances for each phase
    for phase, phase_xy in zip(phases["phase"], player_xyobj):
        # calculate velocity
        vm = VelocityModel()
        vm.fit(phase_xy)
        xyobj_vel = vm.velocity()

        # convert to km/h & concat values of respective players
        xyobj_vel_kmh = pd.DataFrame(xyobj_vel.property * 3.6)

        # configure speed zones
        zone_bins = [0, 7.1, 14.3, 19.7, 25.1, float('inf')]
        zone_labels = ['z0_7', 'z7_14', 'z14_19', 'z19_25', 'z25']

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

        # calculate speed zones distances for each ball possession phase
        pos_phases_speed_zones_distance = []
        start_index = 0

        for pos_phase_length in pos_phases_length:
            end_index = start_index + pos_phase_length
            pos_phase_xyobj_vel_kmh = xyobj_vel_kmh.iloc[start_index:end_index]

            # get df to long format
            pos_phase_data = pd.DataFrame({"velocity": pd.concat([pos_phase_xyobj_vel_kmh[col] for col in pos_phase_xyobj_vel_kmh.columns], axis=0)})

            # add speed zones
            pos_phase_data["zone"] = pd.cut(pos_phase_data["velocity"], bins=zone_bins, labels=zone_labels, right=False)

            # calculate the total number of frames in the respective speed zones
            frames_per_zone = pos_phase_data.groupby("zone", observed=False).size()

            # calculate distance per frame (assuming a frame rate of 20 Hz and converting velocity back to m/s)
            mean_velocity = pos_phase_data.groupby("zone", observed=False)["velocity"].mean()
            mean_distance_per_frame = (mean_velocity / 3.6 / 20)

            # calculate distances for each zone
            pos_phase_speed_zones_distance = frames_per_zone * mean_distance_per_frame
            pos_phase_speed_zones_distance.fillna(0, inplace=True)
            pos_phase_speed_zones_distance["total"] = pos_phase_speed_zones_distance.sum()

            # transpose to df
            pos_phase_speed_zones_distance = pos_phase_speed_zones_distance.to_frame().T

            # divide by length of the respective ball possession phase for weighted aggregation
            pos_phase_speed_zones_distance = pos_phase_speed_zones_distance * (pos_phase_length / 4801)

            pos_phases_speed_zones_distance.append(pos_phase_speed_zones_distance)

            start_index = end_index

        speed_zones_distance.append(pos_phases_speed_zones_distance)

    return speed_zones_distance
