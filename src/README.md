# Source Code Overview

## floater_main.py:

Main file in which all functions are executed / analyses are performed

## floater_processing.py:

Functions required for reading and processing the data to subsequently analyse them

## floater_game_metrics.py

Functions used to calculate duration, outcome and number of ball possession phases

## floater_speed_zones_distance.py:

Function used to calculate the distance covered in different speed zones

## floater_technical_parameters.py:

Functions used to calculate absolute number and success rate of passes, dribbles, shots and overall ball possession actions

## floater_tactical_kpis.py:

Functions used to calculate the respective tactical KPIs

#### length-per-width ratio (lpw)

Description:
* Team length divided by team width
* Team length: distance between the most advanced and least advanced player
* Team width: distance between the two widest players on the pitch
* Implications: larger values, more elongated playing shape; smaller values, more flattened playing shape

Steps:
1. Input must be arranged in alternating x- and y- columns for each unit of time series
2. Output is an array in time series

#### effective playing space (eps)

Description:
* Polygonal area of all players on the periphery of play, calculated using a convex hull method

Steps:
1. Input must be arranged in alternating x- and y- columns for each unit of time series
2. Output is an array in time series

#### space control (sc)

Description:
* Percentage of the pitch controlled by each team, calculated using discretized versions of the Voronoi tessellation
* Using a mesh grid, each point on the pitch is assigned to the nearest player

Steps:
1. Input must be arranged in alternating x- and y- columns for each unit of time series for each of the two teams
2. Output is an property object for each team in time series

#### max overplayed defenders (od_max)

Description:
* Maximum value of overplayed opponents
* Can take values between 0 & n<sub>opposing team size</sub>

Steps:
1. Input must be arranged in alternating x- and y- columns for each unit of time series for all players, the defenders & the ball
2. Output is a single integer

## floater_statistic.py / floater_statistic.qmd

Functions used to prepare data for statistical analysis & calculate descriptive and inferential analysis

## floater_visualisation.py:

Functions used to create graphics of the experimental setup, the conditions and the KPIs for the master thesis / paper
