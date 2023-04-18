import os
from match_results import MatchResults

script_dir = os.path.dirname(__file__)

PATH_F9 = f"{script_dir}/docs/f9-23-2021-2219311-matchresults.xml"

print(f"Parsing {PATH_F9}")
opta_f9 = MatchResults(PATH_F9)

print("PRINTING PLAYERS DATAFRAME...")
print("------------------")
print(opta_f9.get_df_players())
print("------------------")

print("PRINTING ALL STATS DATAFRAME...")
print("------------------")
print(opta_f9.get_df_all_stats())
print("------------------")

print("PRINTING PLAYERS STATS DATAFRAME...")
print("------------------")
print(opta_f9.get_df_players_stats())
print("------------------")

print("PRINTING TOTAL PASS DATAFRAME FOR TEAM ID=177...")
print("------------------")
print(opta_f9.get_df_specific_stat('total_pass', team_id = 173))
print("------------------")

list_params = [{'total_pass': 1}, {'interception': 1}, {'total_att_assist': 1},
                    {'challenge_lost': 0}, {'fouled_final_third': 1}]
player_radar = opta_f9.create_player_radar(169007, list_params, min_minutes = 20,
                                    normalized_to_90 = True)
comparison_radar = opta_f9.create_comparison_radar(169007, 175352, list_params, min_minutes=1)

player_radar.show()