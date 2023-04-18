import os
from events import Events

script_dir = os.path.dirname(__file__)

PATH_F24 = f"{script_dir}/docs/f24-23-2021-2219577-eventdetails.xml"
PATH_FILE_SQUAD = f"{script_dir}/docs/srml-23-2021-squads.xml"

print(f"Parsing {PATH_F24}")
opta_f24 = Events(PATH_F24)
opta_f24.set_squads_info(PATH_FILE_SQUAD)

print("PRINTING MATCH INFO...")
print("------------------")
print(opta_f24.get_match_info())
print("------------------")

print("PRINTING PLAYERS DATAFRAME...")
print("------------------")
print(opta_f24.get_df_players())
print("------------------")

print("PRINTING TEAMS DATAFRAME...")
print("------------------")
print(opta_f24.get_df_teams())
print("------------------")

print("PRINTING SHOTS DATAFRAME FOR TEAM.ID=175...")
print("------------------")
print(opta_f24.get_df_shots(team_id=175))
print("------------------")

print("PRINTING SHOTS STATS...")
print("------------------")
print(opta_f24.get_stats_shots())
print("------------------")

print(f"CREATING REPORT... Path: {script_dir}/test_report.pdf")
print("------------------")
opta_f24.create_team_report(175, f"{script_dir}/test_report.pdf")
print("------------------")

pitch_corners = opta_f24.get_pitch_corners(team_id=5683)
barchart = opta_f24.get_bar_chart_passes()
players_heatmap = opta_f24.get_team_players_heatmap(5683)
passes_heatmap = opta_f24.get_team_passes_heatmap(175)

passes_heatmap.show()

