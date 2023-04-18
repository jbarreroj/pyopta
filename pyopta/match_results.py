import xml.etree.ElementTree as ET
from typing import List

import pandas as pd
import matplotlib.pyplot as plt

from mplsoccer import Radar, FontManager, grid

from constants import UNDEFINED_INT
from player import Player
from team import Team


class MatchResults:
    
    """
    Class constructor that initializes instance variables and calls a function to parse Opta F9 xml file data

    Parameters:
    file_path (str): The path to the Opta F9 xml file that contains the data
    """    
    def __init__(self, file_path):
        self.__teams = []
        self.__players = []
        self.__players_stats = []
        self.__all_stat_types_set = set()
        self.__parse_f9opta_file(file_path)

    
    def get_df_players_stats(self):
        df = pd.DataFrame.from_dict(self.__players_stats)
        return df


    def get_df_all_stats(self):
        return pd.DataFrame(self.__all_stat_types_set, columns = ['stat'])


    def get_df_players(self):
        return pd.DataFrame([{'player_id': p.player_id, 'team_id': p.team_id, 
                            'match_position': p.match_position, 'first': p.first,
                            'last': p.last, 'known': p.known} for p in self.__players])


    def get_df_teams(self):
        """
        Returns a pandas DataFrame with information about the teams that played the match.

        Each row of the DataFrame corresponds to a team, and contains the team's
        identifier and name. 

        Returns:
            A pandas DataFrame with columns 'team_id' and 'team_name'.
        """
        return pd.DataFrame([{'team_id': t.team_id, 'team_name': t.team_name} for t in self.__teams])


    def get_df_specific_stat(self, stat, player_id = UNDEFINED_INT, team_id = UNDEFINED_INT):
        min_columns = ['player_id', 'team_id', 'match_position', 'first', 'last', 'known',
                        'shirt_number', 'status', 'captain', 'mins_played', stat]
        df = self.get_df_players_stats().loc[:, min_columns]
        if player_id != UNDEFINED_INT:
            df = df.query(f'player_id == {player_id}').reset_index(drop=True)
        if team_id != UNDEFINED_INT:
            df = df.query(f'team_id == {team_id}').reset_index(drop=True)
        
        return df.sort_values(by=[stat], ascending=False)


    def create_player_radar(self, player_id, list_params, 
                        min_minutes = 1, normalized_to_90 = False):
        # radar params        
        params = self.__reduce_params(list_params)
        # "lower number is better" list
        lower_is_better_list = self.__get_keys_value_zero(list_params)
                
        # Player stats dataframe (players with more than {min_minutes} minutes played)
        df = self.get_df_players_stats()
        df_mins = df.query(f'mins_played >= {min_minutes}').reset_index(drop=True)

        if len(df_mins.query(f'player_id == {player_id}')) == 0:
            raise("The selected player did not play the defined minimum number of minutes")

        low_values, high_values = self.__calculate_low_high_values(df_mins, params, 
                                            normalized_to_90 = normalized_to_90)
        player_values = self.__calculate_player_values(df_mins, params, player_id, 
                                            normalized_to_90 = normalized_to_90)

        # creating the figure using the grid function from mplsoccer:
        fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                        title_space=0, endnote_space=0, grid_key='radar', axis=False)

        radar = Radar(params, low_values, high_values,
              lower_is_better=lower_is_better_list,
              round_int=[False]*len(params),
              num_rings=4, 
              ring_width=1, center_circle_radius=1)

        # Plot radar
        radar.setup_axis(ax=axs['radar'])
        rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#6fa8dc', edgecolor='#2c4358')
        radar_output = radar.draw_radar(player_values, ax=axs['radar'],
                                        kwargs_radar={'facecolor': '#dca36f'},
                                        kwargs_rings={'facecolor': '#66d8ba'})
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=12)
        param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=12)
        axs['radar'].scatter(vertices[:, 0], vertices[:, 1], c='#00f2c1', edgecolors='#6d6c6d', 
                                marker='o', s=40, zorder=2)

        # Legends
        # Player info
        obj_player = self.__get_player(player_id)        
        obj_team = self.__get_team(UNDEFINED_INT if obj_player is None else obj_player.team_id)
        player_name = "" if obj_player is None else f"{obj_player.first} {obj_player.last}"
        player_team_name = "" if obj_team is None else obj_team.team_name
        title1_text = axs['title'].text(0.04, 0.65, player_name, fontsize=16,
                                        ha='left', va='center')
        title2_text = axs['title'].text(0.90, 0.65, player_team_name, fontsize=14,
                                        ha='right', va='center')
        # Endnote
        min_minutes_text = f"Players who played at least {min_minutes} minutes."
        normalized_text = "Values normalized to 90 mins." if normalized_to_90 else "Absolute values."
        endnote_text = f"INFO: {min_minutes_text}{normalized_text}"
        endnote_text = axs['endnote'].text(0.04, 0.5, endnote_text, fontsize=10,
                                   ha='left', va='center')
        
        return plt


    def create_comparison_radar(self, player1_id, player2_id, list_params, 
                        min_minutes = 1, normalized_to_90 = False):
        # radar params        
        params = self.__reduce_params(list_params)
        # "lower number is better" list
        lower_is_better_list = self.__get_keys_value_zero(list_params)

        # Player stats dataframe (players with more than 0 minutes played)
        df = self.get_df_players_stats()
        df_mins = df.query(f'mins_played >= {min_minutes}').reset_index(drop=True)

        if len(df_mins.query(f'player_id == {player1_id}')) == 0 or \
            len(df_mins.query(f'player_id == {player2_id}')) == 0:
            raise("One of the selected players did not play the defined minimum number of minutes")
        low_values, high_values = self.__calculate_low_high_values(df_mins, params, 
                                            normalized_to_90 = normalized_to_90)
        player1_values = self.__calculate_player_values(df_mins, params, player1_id, 
                                            normalized_to_90 = normalized_to_90)
        player2_values = self.__calculate_player_values(df_mins, params, player2_id, 
                                            normalized_to_90 = normalized_to_90)

        radar = Radar(params, low_values, high_values,
              lower_is_better=lower_is_better_list,
              round_int=[False]*len(params),
              num_rings=4, 
              ring_width=1, center_circle_radius=1)
        
        # creating the figure using the grid function from mplsoccer:
        fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                title_space=0, endnote_space=0, grid_key='radar', axis=False)

        # plot radar
        radar.setup_axis(ax=axs['radar'])  # format axis as a radar
        rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#ffb2b2', edgecolor='#fc5f5f')
        radar_output = radar.draw_radar_compare(player1_values, player2_values, ax=axs['radar'],
                                                kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                                kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
        radar_poly, radar_poly2, vertices1, vertices2 = radar_output
        range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=12)
        param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=12)
        axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1],
                            c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=40, zorder=2)
        axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1],
                            c='#d80499', edgecolors='#6d6c6d', marker='o', s=40, zorder=2)
        # Legend
        obj_player1 = self.__get_player(player1_id)
        obj_player2 = self.__get_player(player2_id)
        obj_team1 = self.__get_team(UNDEFINED_INT if obj_player1 is None else obj_player1.team_id)
        obj_team2 = self.__get_team(UNDEFINED_INT if obj_player2 is None else obj_player2.team_id)
        player1_name = "" if obj_player1 is None else f"{obj_player1.first} {obj_player1.last}"
        player1_team_name = "" if obj_team1 is None else obj_team1.team_name
        player2_name = "" if obj_player2 is None else f"{obj_player2.first} {obj_player2.last}"
        player2_team_name = "" if obj_team2 is None else obj_team2.team_name
        title1_text = axs['title'].text(0.01, 0.65, player1_name, fontsize=16, color='#01c49d',
                                        ha='left', va='center')
        title2_text = axs['title'].text(0.01, 0.25, player1_team_name, fontsize=10,
                                        ha='left', va='center', color='#01c49d')
        title3_text = axs['title'].text(0.99, 0.65, player2_name, fontsize=16,
                                        ha='right', va='center', color='#d80499')
        title4_text = axs['title'].text(0.99, 0.25, player2_team_name, fontsize=10,
                                        ha='right', va='center', color='#d80499')
        return plt


    def __parse_f9opta_file(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        list_team_tag = root.findall('.//Team')
        for team_tag in list_team_tag:
            obj_team = self.__parse_team_tag(team_tag)
            self.__teams.append(obj_team)
            for player_tag in team_tag.iter('Player'):
                obj_player = self.__parse_player_tag(player_tag, obj_team.team_id)
                self.__players.append(obj_player)
        
        list_team_data_tag = root.findall('.//MatchData/TeamData')
        for team_data_tag in list_team_data_tag:
            player_lineup_tag = team_data_tag.find('PlayerLineUp')
            for match_player_tag in player_lineup_tag.iter('MatchPlayer'):
                obj_match_player = self.__parse_match_player_tag(match_player_tag)
                self.__players_stats.append(obj_match_player)
        #adjust player stats with all stats
        self.__adjust_player_stats()


    def __parse_team_tag(self, team_tag):
        id = self.__tag_value_to_int(team_tag.get('uID')[1:])
        name = self.__tag_value_to_str(team_tag.find('Name').text)
        return Team(team_id=id, team_name=name)


    def __parse_player_tag(self, player_tag, team_id):
        id = self.__tag_value_to_int(player_tag.get('uID')[1:])
        match_position = self.__tag_value_to_str(player_tag.get('Position'))
        first_tag = player_tag.find('.//First')
        last_tag = player_tag.find('.//Last')
        known_tag = player_tag.find('.//Known')
        first = self.__tag_value_to_str(None if first_tag is None else first_tag.text)
        last = self.__tag_value_to_str(None if last_tag is None else last_tag.text)
        known = self.__tag_value_to_str(None if known_tag is None else known_tag.text)
        return Player(player_id=id, team_id=team_id, match_position=match_position, 
                        first=first, last=last, known=known)


    def __parse_match_player_tag(self, match_player_tag):
        id = self.__tag_value_to_int(match_player_tag.get('PlayerRef')[1:])
        match_position = self.__tag_value_to_str(match_player_tag.get('Position'))
        shirt_number = self.__tag_value_to_int(match_player_tag.get('ShirtNumber'))
        status = self.__tag_value_to_str(match_player_tag.get('Status'))
        captain = self.__tag_value_to_int(match_player_tag.get('Captain'), error_value=0)
        player = next(filter(lambda p: p.player_id == id, self.__players))
        dict_player = {'player_id':id, 'team_id': player.team_id, 'match_position': match_position,
                        'first': player.first, 'last': player.last, 'known': player.known,
                        'shirt_number': shirt_number, 'status': status, 'captain': captain}
        for stat_tag in match_player_tag.iter('Stat'):
            stat_type = self.__tag_value_to_str(stat_tag.get('Type'))
            stat_value = self.__tag_value_to_int(stat_tag.text, error_value=0)
            dict_player.update({stat_type:stat_value})
            self.__all_stat_types_set.add(stat_type)
        return dict_player


    def __adjust_player_stats(self):
        for player_stats in self.__players_stats:
            for stat_type in self.__all_stat_types_set:
                if stat_type not in player_stats:
                    player_stats.update({stat_type: 0})


    def __get_player(self, player_id):
        filtered = [pl for pl in self.__players if pl.player_id == player_id]
        if len(filtered) == 0:
            return None
        else:
            return filtered[0]


    def __get_team(self, team_id):
        filtered = [t for t in self.__teams if t.team_id == team_id]
        if len(filtered) == 0:
            return None
        else:
            return filtered[0]


    @staticmethod
    def __tag_value_to_int(value, error_value = UNDEFINED_INT):
        try:
            return int(value)
        except (ValueError, TypeError):
            return error_value


    @staticmethod
    def __tag_value_to_str(value):
        if value is None:
            return ''
        return str(value)


    @staticmethod
    def __reduce_params(list_params):
        return list(map(lambda d: list(d.keys())[0], list_params))


    @staticmethod
    def __get_keys_value_zero(list_params):
        return list(map(lambda d: list(d.keys())[0], 
                    filter(lambda d: d[list(d.keys())[0]] == 0, list_params)))


    @staticmethod
    def __calculate_low_high_values(df, list_params, normalized_to_90 = False):
        df_copy = df.copy()
        low_values = []
        high_values = []
        for param in list_params:
            if normalized_to_90:
                df_copy[param] = df_copy.apply(lambda x: 90 * x[param] / x['mins_played'], axis=1)            
            low_values.append(df_copy[param].min())
            high_values.append(df_copy[param].max())
        return low_values, high_values


    @staticmethod
    def __calculate_player_values(df, list_params, player_id, normalized_to_90 = False):
        df_copy = df.copy()
        player_values = []
        for param in list_params:
            if normalized_to_90:
                df_copy[param] = df_copy.apply(lambda x: 90 * x[param] / x['mins_played'], axis=1)
            player_values.append(df_copy.loc[df_copy['player_id'] == player_id, param].iloc[0])
        return player_values
