# import packages
import os
import pandas as pd
from floodlight.io.kinexon import read_position_data_csv, get_meta_data, create_links_from_meta_data
from floodlight.transforms.filter import butterworth_lowpass
import floater_processing as proc
import floater_game_metrics as met
import floater_speed_zones_distance as dist
import floater_technical_parameters as tec
import floater_tactical_kpis as tac
import floater_statistic as stat
import floater_visualisation as vis

# own path
os.chdir("insert_path")

# load data
data_position = read_position_data_csv("insert_path.csv")
data_structure = pd.read_excel("insert_path.xlsx", sheet_name="sheet_name")
data_tagging = proc.read_tagging_data("insert_path", "date", ["offset_1", "offset_2", "..."])

pID_dict, _, _, t_session_begin = get_meta_data("insert_path.csv")
meta_data_links = create_links_from_meta_data(pID_dict)

phases = proc.get_phases_overview("insert_path.xlsx")

# smooth xy data -> Winter (2009) Biomechanik Buch
xy_player_filter = butterworth_lowpass(data_position[0])
xy_ball_filter = butterworth_lowpass(data_position[1])

# create list of extracted relevant players, balls & labels for each phase
xy_floater, xy_attacker, xy_defender, xy_all, xy_balls, labels = proc.extract_slice_player_label(xy_player_filter, xy_ball_filter, data_structure, meta_data_links, phases, data_tagging, t_session_begin)

# check xyobj for nans
nan_check_player = proc.detect_nans(xy_all)
nan_check_ball = proc.detect_nans(xy_balls)

# interpolate NaNs & cut out last four runs due to too many NaNs
xy_floater, xy_defender, xy_attacker, xy_all, xy_balls, labels, phases = proc.interpolate_cut_runs(xy_floater, xy_defender, xy_attacker, xy_all, xy_balls, labels, phases)

#####################################################################################################
# results

# create liste of durations of all ball position phases for each phase
results_duration = met.calc_duration(phases, data_tagging, t_session_begin)

# create list of outcomes of all ball position phases for each phase
results_outcome = met.get_outcome(labels)

# create list of number of ball possession phases for each phase
results_ball_pos_phases = met.calc_ball_pos_phases(results_duration)

# create list of calculated speed zone distances for each phase
results_speed_zones_distance_floater = dist.calc_speed_zones_distance(xy_floater, phases, data_tagging, t_session_begin)
#results_speed_zones_distance_attacker = dist.calc_speed_zones_distance(xy_attacker, phases, data_tagging, t_session_begin)
#results_speed_zones_distance_defender = dist.calc_speed_zones_distance(xy_defender, phases, data_tagging, t_session_begin)
#results_speed_zones_distance_all = dist.calc_speed_zones_distance(xy_all, phases, data_tagging, t_session_begin)

# create list of technical parameters of the floaters for each phase
results_technical_floater = tec.get_technical_parameters(labels, phases, data_tagging, t_session_begin)

# create list of calculated length-per-width ratio (LpW) for each phase
results_lpw_attacker, results_length_attacker, results_width_attacker = tac.calc_lpw(xy_attacker, phases, data_tagging, t_session_begin)
results_lpw_defender, results_length_defender, results_width_defender = tac.calc_lpw(xy_defender, phases, data_tagging, t_session_begin)

# create list of calculated effective playing space (EPS) for each phase
results_eps = tac.calc_eps(xy_all, phases, data_tagging, t_session_begin)

# create list of calculated space control (SC) for each phase
results_sc_final_third = tac.calc_sc("final_third", xy_attacker, xy_defender, data_structure, phases, data_tagging, t_session_begin)
results_sc_zones = tac.calc_sc("zones", xy_attacker, xy_defender, data_structure, phases, data_tagging, t_session_begin)

# create list of calculated overplayed defenders (OD) for each phase
results_od_max = tac.calc_od_max(xy_all, xy_defender, xy_balls, phases, data_tagging, t_session_begin)

#####################################################################################################
# statistic

# get condition indices for each phase
conditions_indices = {condition: data_structure["condition"].index[data_structure["condition"] == condition].tolist() for condition in data_structure["condition"].unique()}
for cond in conditions_indices:
    conditions_indices[cond].pop()

# prepare results_list for statistic and save as csv
statistic_duration = stat.prepare_statistic(conditions_indices, results_duration)
statistic_outcome = stat.prepare_statistic(conditions_indices, results_outcome)
statistic_ball_pos_phases = stat.prepare_statistic(conditions_indices, results_ball_pos_phases)
statistic_speed_zones_distance_floater = stat.prepare_statistic(conditions_indices, results_speed_zones_distance_floater)
statistic_technical_floater = stat.prepare_statistic(conditions_indices, results_technical_floater)
statistic_lpw_attacker = stat.prepare_statistic(conditions_indices, results_lpw_attacker)
statistic_lpw_defender = stat.prepare_statistic(conditions_indices, results_lpw_defender)
statistic_eps = stat.prepare_statistic(conditions_indices, results_eps)
statistic_sc_final_third = stat.prepare_statistic(conditions_indices, results_sc_final_third)
statistic_sc_zones = stat.prepare_statistic(conditions_indices, results_sc_zones)
statistic_od_max = stat.prepare_statistic(conditions_indices, results_od_max)

statistic_duration.to_csv("insert_path.csv")
statistic_outcome.to_csv("insert_path.csv")
statistic_ball_pos_phases.to_csv("insert_path.csv")
statistic_speed_zones_distance_floater.to_csv("insert_path.csv")
statistic_technical_floater.to_csv("insert_path.csv")
statistic_lpw_attacker.to_csv("insert_path.csv")
statistic_lpw_defender.to_csv("insert_path.csv")
statistic_eps.to_csv("insert_path.csv")
statistic_sc_final_third.to_csv("insert_path.csv")
statistic_sc_zones.to_csv("insert_path.csv")
statistic_od_max.to_csv("insert_path.csv")

# duration
stats_duration_descr = stat.calc_statistics(conditions_indices, results_duration)

# outcome
stats_outcome_descr = stat.calc_statistics(conditions_indices, results_outcome)

# number of ball possession phases
stats_ball_pos_phases_descr = stat.calc_statistics(conditions_indices, results_ball_pos_phases)

# speed_zones_distance - , stats_speed_zones_distance_floater_inf
stats_speed_zones_distance_floater_descr = stat.calc_statistics_speed_zones_distance(conditions_indices, results_speed_zones_distance_floater)

# technical parameters - , stats_technical_floater_inf
stats_technical_floater_descr = stat.calc_statistics_technical_parameters(conditions_indices, results_technical_floater)

# length-per-width ratio (LpW)
stats_lpw_attacker_descr = stat.calc_statistics(conditions_indices, results_lpw_attacker)
stats_length_attacker_descr = stat.calc_statistics(conditions_indices, results_length_attacker)
stats_width_attacker_descr = stat.calc_statistics(conditions_indices, results_width_attacker)

stats_lpw_defender_descr = stat.calc_statistics(conditions_indices, results_lpw_defender)
stats_length_defender_descr = stat.calc_statistics(conditions_indices, results_length_defender)
stats_width_defender_descr = stat.calc_statistics(conditions_indices, results_width_defender)

# effective playing space (EPS)
stats_eps_descr = stat.calc_statistics(conditions_indices, results_eps)

# space control (SC)
stats_sc_final_third_descr = stat.calc_statistics(conditions_indices, results_sc_final_third)
stats_sc_zones_descr = stat.calc_statistics(conditions_indices, results_sc_zones)

# overplayed defenders (OD)
stats_od_max_descr = stat.calc_statistics(conditions_indices, results_od_max)

#####################################################################################################
# visualizations

# visualize a specific phase
vis.visualize_phase(xy_all[0])

# visualize experimental setup
graphic_experimental_setup = vis.visualize_experimental_setup()
graphic_experimental_setup.savefig("insert_path.png", dpi=300)

# visualize conditions
graphic_condition_a_a = vis.visualize_conditions("outer", "none")
graphic_condition_a_a.savefig("insert_path.png", dpi=300)

graphic_condition_a_z = vis.visualize_conditions("outer", "grey")
graphic_condition_a_z.savefig("insert_path.png", dpi=300)

graphic_condition_z_a = vis.visualize_conditions("inner", "none")
graphic_condition_z_a.savefig("insert_path.png", dpi=300)

graphic_condition_z_z = vis.visualize_conditions("inner", "grey")
graphic_condition_z_z.savefig("insert_path", dpi=300)

# visualize KPIs
graphic_lpw = vis.visualize_kpis("lpw")
graphic_lpw.savefig("insert_path", dpi=300)

graphic_eps = vis.visualize_kpis("eps")
graphic_eps.savefig("insert_path", dpi=300)

graphic_sc = vis.visualize_kpis("sc")
graphic_sc.savefig("insert_path.png", dpi=300)

graphic_od_max = vis.visualize_kpis("od_max")
graphic_od_max.savefig("insert_path.png", dpi=300)

# visualize regular heatmaps
graphic_heatmap_a_a = vis.visualize_heatmaps("A-A", conditions_indices, xy_floater)
graphic_heatmap_a_a.savefig("insert_path.png", dpi=300)

graphic_heatmap_a_z = vis.visualize_heatmaps("A-Z", conditions_indices, xy_floater)
graphic_heatmap_a_z.savefig("insert_path.png", dpi=300)

graphic_heatmap_z_a = vis.visualize_heatmaps("Z-A", conditions_indices, xy_floater)
graphic_heatmap_z_a.savefig("insert_path.png", dpi=300)

graphic_heatmap_z_z = vis.visualize_heatmaps("Z-Z", conditions_indices, xy_floater)
graphic_heatmap_z_z.savefig("insert_path.png", dpi=300)

# visualize one directional heatmaps
xy_floater_one_direction = proc.xy_to_one_direction(xy_floater, phases, data_tagging, t_session_begin)

graphic_heatmap_1direction_a_a = vis.visualize_heatmaps("A-A", conditions_indices, xy_floater_one_direction)
graphic_heatmap_1direction_a_a.savefig("insert_path.png", dpi=300)

graphic_heatmap_1direction_a_z = vis.visualize_heatmaps("A-Z", conditions_indices, xy_floater_one_direction)
graphic_heatmap_1direction_a_z.savefig("insert_path.png", dpi=300)

graphic_heatmap_1direction_z_a = vis.visualize_heatmaps("Z-A", conditions_indices, xy_floater_one_direction)
graphic_heatmap_1direction_z_a.savefig("insert_path.png", dpi=300)

graphic_heatmap_1direction_z_z = vis.visualize_heatmaps("Z-Z", conditions_indices, xy_floater_one_direction)
graphic_heatmap_1direction_z_z.savefig("insert_path.png", dpi=300)
