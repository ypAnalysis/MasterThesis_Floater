# import packages
import pandas as pd
import numpy as np
from floodlight.vis.pitches import plot_football_pitch
from floodlight.vis.positions import plot_trajectories
from mplsoccer import Pitch
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('module://backend_interagg')


# visualize a specific phase
def visualize_phase(xyobj):
    # create matplotlib.axes
    ax = plt.subplots()[1]

    # create pitch object
    plot_football_pitch(xlim=(-49.97, 49.97), ylim=(-32.94, 32.94), length=99.94, width=65.88, unit='m', color_scheme='standard', show_axis_ticks=False, ax=ax)

    # plot positions on ax
    plot_trajectories(xy=xyobj, start_frame=0, end_frame=224, ball=False, ax=ax)

    return plt.show()


# visualize experimental setup
def visualize_experimental_setup():
    # create pitch
    pitch = Pitch(pitch_type="custom", pitch_length=99.94, pitch_width=65.88, line_alpha=0.3, line_color="grey", pitch_color="white", corner_arcs=True, linewidth=0.4)
    fig, ax = pitch.draw(figsize=(10, 7))

    # add study pitch size
    floater_pitch = Pitch(pitch_type="custom", pitch_length=77, pitch_width=51, line_alpha=1, line_color="orange", pitch_color="none", corner_arcs=True, linewidth=1.3)
    floater_pitch.draw(ax=fig.add_axes([1.35/99.94, 7.44/65.88, 77/99.94, 51/65.88], zorder=2))

    ax.plot([-0.15, -0.15], [28.44, 37.44], color="orange", linewidth=2.5, zorder=0)
    ax.plot([77.6, 77.6], [28.44, 37.44], color="orange", linewidth=2.5, zorder=0)

    # add player & ball
    red_positions = [(4, 32.94),     # gk
                     (26.5, 25),     # def right
                     (30, 43),       # def left
                     (23.5, 34),     # def middle
                     (43.5, 28),     # off right
                     (45, 40),       # off left
                     (36, 32)]       # off middle

    green_positions = [(70, 32.94),  # gk
                       (46.5, 21),   # def left
                       (49, 44),     # def right
                       (52, 31),     # def middle
                       (28, 28),     # off left
                       (40, 38.5),   # off right
                       (30, 37)]     # off middle

    floater_positions = [(34.5, 13), (40, 52)]

    for pos in red_positions:
        ax.plot(pos[0], pos[1], "o", color='red', markersize=15, zorder=1)
    for pos in green_positions:
        ax.plot(pos[0], pos[1], "o", color='green', markersize=15, zorder=1)
    for pos in floater_positions:
        ax.plot(pos[0], pos[1], "o", color='grey', markersize=15, markeredgewidth=3, zorder=1)

    ax.plot(red_positions[0][0], red_positions[0][1], "o", color="red", markersize=15, markeredgecolor="black", zorder=2)
    ax.plot(green_positions[0][0], green_positions[0][1], "o", color="green", markersize=15, markeredgecolor="black", zorder=2)

    ax.plot(51.2, 30.8, "o", color="black", markersize=10, zorder=2)

    # add Kinexon sensors
    kinexon_sensors_corners = [(-2, -2), (-2, 67.88), (101.94, -2), (101.94, 67.88)]
    kinexon_sensors = [(-2.5, 20), (-2.5, 45.88), (18.49, 68.38), (39.48, 68.38), (60.46, 68.38), (81.45, 68.38), (102.44, 45.88), (102.44, 20), (81.45, -2.5), (60.46, -2.5), (39.48, -2.5), (18.49, -2.5)]

    for sensor in kinexon_sensors_corners:
        ax.plot(sensor[0], sensor[1], "D", color="black", markersize=10, zorder=2)
    for sensor in kinexon_sensors:
        ax.plot(sensor[0], sensor[1], "s", color="black", markersize=10, zorder=2)

    plt.show()

    return fig


# visualize conditions
def visualize_conditions(zone, circle_color):
    # create pitch
    pitch = Pitch(pitch_type="custom", pitch_length=77, pitch_width=51, line_alpha=0.6, line_color="grey",
                  pitch_color="white", corner_arcs=True, linewidth=0.4)
    fig, ax = pitch.draw(figsize=(10, 7))

    # add outside line
    floater_pitch = plt.Rectangle((0, 0), 77, 51, edgecolor="black", facecolor="none", linewidth=1)
    ax.add_patch(floater_pitch)

    # add goal line
    ax.plot([0, 0], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)
    ax.plot([77, 77], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)

    # add dashed lines
    ax.plot([0, 77], [12.75, 12.75], color="black", linestyle="dashed", linewidth=1)
    ax.plot([0, 77], [38.25, 38.25], color="black", linestyle="dashed", linewidth=1)

    # add player & ball
    if zone == "inner":
        red_positions = [(4, 32.94 - 7.44),     # gk
                         (26.5, 25 - 7.44),     # def right
                         (30, 43 - 7.44),       # def left
                         (23.5, 34 - 7.44),     # def middle
                         (43.5, 28 - 7.44),     # off right
                         (43, 41 - 7.44),       # off left
                         (36, 32 - 7.44)]       # off middle

        green_positions = [(67, 32.94 - 7.44),  # gk
                           (46, 16.5 - 7.44),   # def left
                           (49.5, 45 - 7.44),   # def right
                           (53, 31 - 7.44),     # def middle
                           (32, 27 - 7.44),     # off left
                           (35.5, 52 - 7.44),   # off right
                           (29, 38 - 7.44)]     # off middle

        floater_positions = [(38, 24 - 7.44), (34.5, 38 - 7.44)]

        ball_position = (52.2, 31.3 - 7.44)

    elif zone == "outer":
        red_positions = [(4, 32.94 - 7.44),     # gk
                         (26.5, 25 - 7.44),     # def right
                         (30, 43 - 7.44),       # def left
                         (23.5, 34 - 7.44),     # def middle
                         (43.5, 28 - 7.44),     # off right
                         (45, 40 - 7.44),       # off left
                         (36, 32 - 7.44)]       # off middle

        green_positions = [(70, 32.94 - 7.44),  # gk
                           (46.5, 21 - 7.44),   # def left
                           (49, 44 - 7.44),     # def right
                           (52, 31 - 7.44),     # def middle
                           (28, 28 - 7.44),     # off left
                           (40, 38.5 - 7.44),   # off right
                           (30, 37 - 7.44)]     # off middle

        floater_positions = [(34.5, 13 - 7.44), (40, 52 - 7.44)]

        ball_position = (51.2, 30.8 - 7.44)

    for pos in red_positions:
        ax.plot(pos[0], pos[1], "o", color='red', markersize=15)
    for pos in green_positions:
        ax.plot(pos[0], pos[1], "o", color='green', markersize=15)
    for pos in floater_positions:
        ax.plot(pos[0], pos[1], "o", color='grey', markerfacecolor=circle_color, markersize=15, markeredgewidth=3)

    ax.plot(red_positions[0][0], red_positions[0][1], "o", color="red", markersize=15, markeredgecolor="black")
    ax.plot(green_positions[0][0], green_positions[0][1], "o", color="green", markersize=15, markeredgecolor="black")

    ax.plot(ball_position[0], ball_position[1], "o", color="black", markersize=10)

    plt.show()

    return fig


# visualize KPIs
def visualize_kpis(kpi):
    # create pitch
    pitch = Pitch(pitch_type="custom", pitch_length=77, pitch_width=51, line_alpha=0.6, line_color="grey", pitch_color="white", corner_arcs=True, linewidth=0.4)
    fig, ax = pitch.draw(figsize=(10, 7))

    # add outside line
    floater_pitch = plt.Rectangle((0, 0), 77, 51, edgecolor="black", facecolor="none", linewidth=1)
    ax.add_patch(floater_pitch)

    # add goal line
    ax.plot([0, 0], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)
    ax.plot([77, 77], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)

    # add player & ball
    if kpi == "sc":
        red_positions = [(4, 32.94 - 7.44),     # gk
                         (26.5, 25 - 7.44),     # def right
                         (30, 43 - 7.44),       # def left
                         (23.5, 34 - 7.44),     # def middle
                         (43.5, 28 - 7.44),     # off right
                         (43, 41 - 7.44),       # off left
                         (36, 32 - 7.44)]       # off middle

        green_positions = [(67, 32.94 - 7.44),  # gk
                           (46, 16.5 - 7.44),   # def left
                           (49.5, 45 - 7.44),   # def right
                           (53, 31 - 7.44),     # def middle
                           (32, 27 - 7.44),     # off left
                           (35.5, 52 - 7.44),   # off right
                           (29, 38 - 7.44)]     # off middle

        floater_positions = [(38, 24 - 7.44), (34.5, 38 - 7.44)]

    else:
        red_positions = [(4, 32.94 - 7.44),     # gk
                         (26.5, 25 - 7.44),     # def right
                         (30, 43 - 7.44),       # def left
                         (23.5, 34 - 7.44),     # def middle
                         (43.5, 28 - 7.44),     # off right
                         (45, 40 - 7.44),       # off left
                         (36, 32 - 7.44)]       # off middle

        green_positions = [(70, 32.94 - 7.44),  # gk
                           (46.5, 21 - 7.44),   # def left
                           (49, 44 - 7.44),     # def right
                           (52, 31 - 7.44),     # def middle
                           (28, 28 - 7.44),     # off left
                           (40, 38.5 - 7.44),   # off right
                           (30, 37 - 7.44)]     # off middle

        floater_positions = [(34.5, 13 - 7.44), (40, 52 - 7.44)]

    for pos in red_positions:
        ax.plot(pos[0], pos[1], "o", color='red', markersize=15)
    for pos in green_positions:
        ax.plot(pos[0], pos[1], "o", color='green', markersize=15)
    for pos in floater_positions:
        ax.plot(pos[0], pos[1], "o", color='grey', markersize=15, markeredgewidth=3)

    ax.plot(red_positions[0][0], red_positions[0][1], "o", color="red", markersize=15, markeredgecolor="black")
    ax.plot(green_positions[0][0], green_positions[0][1], "o", color="green", markersize=15, markeredgecolor="black")

    if kpi == "lpw":
        ax.plot(51.2, 30.8-7.44, "o", color="black", markersize=10)

        ax.add_patch(plt.Rectangle((23.5, 25 - 7.44), 21.5, 18, edgecolor="red", facecolor="red", alpha=0.3, linewidth=1.5, zorder=7))
        ax.add_patch(plt.Rectangle((28, 13 - 7.44), 24, 39, edgecolor="green", facecolor="green", alpha=0.3, linewidth=1.5, zorder=7))

    elif kpi == "eps":
        ax.plot(51.2, 30.8-7.44, "o", color="black", markersize=10)

        df = pd.DataFrame(red_positions[1:] + green_positions[1:] + floater_positions)

        hull = pitch.convexhull(df.iloc[:, 0], df.iloc[:, 1])
        poly = pitch.polygon(hull, ax=ax, edgecolor="cornflowerblue", facecolor="cornflowerblue", alpha=0.3)

    elif kpi == "sc":
        ax.plot(51.2, 30.8 - 7.44, "o", color="black", markersize=10)

        df = pd.DataFrame(red_positions[1:] + green_positions[1:] + floater_positions)
        df["attacker"] = [False] * (len(red_positions) - 1) + [True] * (len(green_positions) - 1 + len(floater_positions))
        df_visible_area = pd.DataFrame([(0, 12.75), (0, 38.25), (77, 38.25), (77, 12.75), (0, 12.75)])

        voronoi_red, voronoi_green = pitch.voronoi(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2])
        polygon_red = pitch.polygon(voronoi_red, ax=ax, fc='green', ec='white', lw=3, alpha=0.4)
        polygon_green = pitch.polygon(voronoi_green, ax=ax, fc='red', ec='white', lw=3, alpha=0.4)

        visible = pitch.polygon([df_visible_area], color='None', ec='k', linestyle='--', lw=1, ax=ax)
        for player in polygon_red:
            player.set_clip_path(visible[0])
        for player in polygon_green:
            player.set_clip_path(visible[0])

    elif kpi == "od_max":
        ax.plot(40.8, 38.1 - 7.44, "o", color="black", markersize=10)

    plt.show()

    return fig


# visualize heatmaps
def visualize_heatmaps(condition, conditions_indices, xyobj):
    # get condition indices
    indices = conditions_indices[condition]

    # create pitch
    pitch = Pitch(pitch_type="custom", pitch_length=77, pitch_width=51, line_alpha=0.6, line_color="grey", pitch_color="white", corner_arcs=True, linewidth=0.4)
    fig, ax = pitch.draw(figsize=(10, 7))

    # combine arrays & players
    array1 = xyobj[indices[0]]
    array2 = xyobj[indices[1]]

    x_combined = np.concatenate([array1[:, i] for i in range(0, array1.xy.shape[1], 2)] +
                                [array2[:, i] for i in range(0, array2.xy.shape[1], 2)])
    y_combined = np.concatenate([array1[:, i + 1] for i in range(0, array1.xy.shape[1], 2)] +
                                [array2[:, i + 1] for i in range(0, array2.xy.shape[1], 2)])

    # filter coordinates on the pitch
    valid_indices = (x_combined >= -49.97) & (x_combined <= 27.03) & (y_combined >= -25.5) & (y_combined <= 25.5)

    x_filtered = x_combined[valid_indices]
    y_filtered = y_combined[valid_indices]

    # create heatmap
    sns.kdeplot(x=x_filtered + 38.5, y=y_filtered + 25.5, ax=ax, fill=True, cmap='Reds', alpha=1, clip=((0, 77), (0, 51)))

    # add outside line
    floater_pitch = plt.Rectangle((0, 0), 77, 51, edgecolor="black", facecolor="none", linewidth=1)
    ax.add_patch(floater_pitch)

    # add goal line
    ax.plot([0, 0], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)
    ax.plot([77, 77], [28.44 - 7.44, 37.44 - 7.44], color="black", linewidth=2.5)

    plt.show()

    return fig
