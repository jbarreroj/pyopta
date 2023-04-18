from datetime import datetime
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import pandas as pd

from mplsoccer.pitch import Pitch

from constants import UNDEFINED_DATE, UNDEFINED_FLOAT, UNDEFINED_INT
from game import Game


class PassMatrix:
    
    def __init__(self, file_path):
        self.__team_id = None
        self.__team_name = None
        self.__match = None
        self.__df_pass_matrix = None
        self.__parse_f27opta_file(file_path)


    def get_df_pass_matrix(self):
        return self.__df_pass_matrix


    def get_pitch_pass_matrix(self, with_subs = False, team_color='#FF0000', passes_color='#eeeeee', min_passes = 1):
        PASSES_MAX_LINE_WIDTH = 14
        MAX_MARKER_SIZE = 800

        df_total_passes = self.__get_df_total_passes()
        df_no_dups = self.__df_pass_matrix.loc[:, 
                                ['from_id','from_name','from_jersey_num', 'from_position', 'from_x', 'from_y']].drop_duplicates()
        df_merge = pd.merge(df_no_dups, df_total_passes, left_on='from_id', right_on='from_id', how='outer').fillna(0)
        df_merge = df_merge[(df_merge.from_id != UNDEFINED_INT) & (df_merge.from_id != 0)]
        df_mean_norm = df_merge.loc[:, 
                                ['from_id','from_name_x','from_jersey_num', 'from_position', 'from_x', 'from_y', 'total_passes']]
        df_mean_norm.rename(columns = {'from_name_x':'from_name'}, inplace = True)
        df_line_passes_norm = self.__df_pass_matrix[(self.__df_pass_matrix.to_id != UNDEFINED_INT) & 
                                (self.__df_pass_matrix.num_passes >= min_passes)]
        

        pitch = Pitch(pitch_type = 'opta', pitch_color='grass', line_color='white',
                        stripe=True) 
        fig, axs = pitch.grid(figheight=10, title_height=0.08, endnote_space=0,
                      axis=False,
                      title_space=0, grid_height=0.82, endnote_height=0.05)

        df_text = None
        df_top = None
        if not with_subs:
            df_mean_position_init = df_mean_norm[df_mean_norm.from_position != 'Substitute']
            df_line_passes_init = df_line_passes_norm[(df_line_passes_norm.from_position != 'Substitute') 
                                        & (df_line_passes_norm.to_position != 'Substitute')]
            df_mean_position_init['size'] = (200 + (df_mean_position_init['total_passes'] / df_mean_position_init['total_passes'].max() *
                            MAX_MARKER_SIZE))
            df_line_passes_init['width'] = (df_line_passes_init['num_passes'] / df_line_passes_init['num_passes'].max() *
                            PASSES_MAX_LINE_WIDTH)
            pitch.lines(df_line_passes_init['from_x'], df_line_passes_init['from_y'], 
              df_line_passes_init['to_x'], df_line_passes_init['to_y'],
              lw=df_line_passes_init['width'],
              color=passes_color, alpha=0.8, zorder=1, ax=axs['pitch'])
            pitch.scatter(df_mean_position_init['from_x'], df_mean_position_init['from_y'],
                ax=axs['pitch'], color=team_color, edgecolors='black', linewidth=1, 
                s=df_mean_position_init['size'])
            df_text = df_mean_position_init
            df_top = df_line_passes_init.sort_values('num_passes', ascending = False)
        else:
            df_mean_norm['size'] = (200 + (df_mean_norm['total_passes'] / df_mean_norm['total_passes'].max() *
                            MAX_MARKER_SIZE))
            df_line_passes_norm['width'] = (df_line_passes_norm['num_passes'] / df_line_passes_norm['num_passes'].max() *
                            PASSES_MAX_LINE_WIDTH)
            df_mean_position_init = df_mean_norm[df_mean_norm.from_position != 'Substitute']
            df_line_passes_init = df_line_passes_norm[(df_line_passes_norm.from_position != 'Substitute') 
                                        & (df_line_passes_norm.to_position != 'Substitute')]
            df_mean_position_subs = df_mean_norm[df_mean_norm.from_position == 'Substitute']
            df_line_passes_subs = df_line_passes_norm[(df_line_passes_norm.from_position == 'Substitute') 
                                        | (df_line_passes_norm.to_position == 'Substitute')]
            pitch.lines(df_line_passes_init['from_x'], df_line_passes_init['from_y'], 
              df_line_passes_init['to_x'], df_line_passes_init['to_y'],
              lw=df_line_passes_init['width'],
              color=passes_color, alpha=0.8, zorder=1, ax=axs['pitch'])
            pitch.lines(df_line_passes_subs['from_x'], df_line_passes_subs['from_y'], 
                df_line_passes_subs['to_x'], df_line_passes_subs['to_y'],
                lw=df_line_passes_subs['width'], 
                color=passes_color, alpha=0.5, zorder=1, ax=axs['pitch'])
            pitch.scatter(df_mean_position_init['from_x'], df_mean_position_init['from_y'],
                    ax=axs['pitch'], color=team_color, edgecolors='black', linewidth=1, 
                    s=df_mean_position_init['size'])
            pitch.scatter(df_mean_position_subs['from_x'], df_mean_position_subs['from_y'],
                    ax=axs['pitch'], color=team_color, edgecolors='black', linewidth=1, alpha=0.5, 
                    s=df_mean_position_subs['size'])
            df_text = df_mean_norm
            df_top = df_line_passes_norm.sort_values('num_passes', ascending = False)
            
        # TITLES
        main_title = f'Pass matrix - {self.__team_name}'
        secondary_title = f'{self.__match.competition_name} ({self.__match.season_name}). Date: {self.__match.game_date}. {self.__match.home_team_name} - {self.__match.away_team_name}'
        
        axs['title'].text(0.5, 0.7, main_title, color='#000000',
                  va='center', ha='center', fontsize=18)
        axs['title'].text(0.5, 0.25, secondary_title, color='#c7d5cc',
                  va='center', ha='center', fontsize=12)
        
        # PLAYER NAMES AND JERSEY NUMBERS
        df_ordered = self.__order_players(df_text) 
        for i in range(len(df_ordered)):
            axs['pitch'].text(85,
                            96 - 2.5 * i,
                            f"{df_ordered['from_jersey_num'].astype(int).iloc[i]} - {df_ordered['from_name'].iloc[i]}",
                            color='#000000', fontsize=6)

        for i in range(len(df_text)):
            axs['pitch'].text(df_text['from_x'].iloc[i] - 1,
                            df_text['from_y'].iloc[i] - 1,
                            df_text['from_jersey_num'].astype(int).iloc[i],
                            color='#000000', fontsize=10)

        # TOP 3
        top3 = [axs['pitch'].text(85, 15, 'TOP 3', color='#000000', fontsize=10)]
        for i in range(3 if len(df_top) >= 3 else len(df_top)):
            axs['pitch'].text(85,
                            12 - 2.5 * i,
                            f"{df_top['from_jersey_num'].astype(int).iloc[i]} --> {df_top['to_jersey_num'].iloc[i]}: {df_top['num_passes'].iloc[i]} passes.",
                            color='#000000', fontsize=6)
        return plt


    def __parse_f27opta_file(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()        
        self.__match = self.__parse_soccerfeed_tag(root)
        list_players_matrix = []
        for player_tag in root.findall('Player'):
            list_players_matrix.extend(self.__parse_player_tag(player_tag, root))
        self.__df_pass_matrix = pd.DataFrame(list_players_matrix)


    def __parse_soccerfeed_tag(self, soccerfeed_tag):
        match_id = self.__tag_value_to_int(soccerfeed_tag.get('game_id'))
        away_team_id = self.__tag_value_to_int(soccerfeed_tag.get('away_team_id'))
        away_team_name = self.__tag_value_to_str(soccerfeed_tag.get('away_team_name'))
        competition_id = self.__tag_value_to_int(soccerfeed_tag.get('competition_id'))
        competition_name = self.__tag_value_to_str(soccerfeed_tag.get('competition_name'))
        game_date = self.__tag_value_to_datetime(soccerfeed_tag.get('game_date'))
        home_team_id = self.__tag_value_to_int(soccerfeed_tag.get('home_team_id'))
        home_team_name = self.__tag_value_to_str(soccerfeed_tag.get('home_team_name'))
        season_id = self.__tag_value_to_int(soccerfeed_tag.get('season_id'))
        season_name = self.__tag_value_to_str(soccerfeed_tag.get('season_name'))
        self.__team_id = self.__tag_value_to_int(soccerfeed_tag.get('team_id'))
        self.__team_name = self.__tag_value_to_str(soccerfeed_tag.get('team_name'))
        return Game(match_id = match_id, away_team_id = away_team_id, 
                    away_team_name = away_team_name, competition_id = competition_id, 
                    competition_name = competition_name, game_date = game_date, 
                    home_team_id= home_team_id, home_team_name = home_team_name,                    
                    season_id = season_id, season_name = season_name)


    def __parse_player_tag(self, player_tag, root):        
        from_id = self.__tag_value_to_int(player_tag.get('player_id'))
        from_name = self.__tag_value_to_str(player_tag.get('player_name'))
        from_jersey_num = self.__tag_value_to_int(player_tag.get('jersey_num'))
        from_position = self.__tag_value_to_str(player_tag.get('position'))
        from_x = self.__tag_value_to_float(player_tag.get('x'))
        from_y = self.__tag_value_to_float(player_tag.get('y'))
        dict_from = {'from_id': from_id, 'from_name': from_name, 'from_jersey_num': from_jersey_num,
                        'from_position': from_position, 'from_x': from_x, 'from_y': from_y}
        to_players = player_tag.findall('Player')
        if len(to_players) == 0:
            dict_to = {'to_id': UNDEFINED_INT, 'to_name': '', 'to_position': '', 
                        'to_x': UNDEFINED_FLOAT, 'to_y': UNDEFINED_FLOAT, 'num_passes': 0}
            return [{**dict_from, **dict_to}]
        else:
            list_player_matrix = []
            for to_tag in to_players:
                to_id = self.__tag_value_to_int(to_tag.get('player_id'))
                to_name = self.__tag_value_to_str(to_tag.get('player_name'))
                num_passes = self.__tag_value_to_int(to_tag.text)
                for root_player in root.findall('Player'):
                    if self.__tag_value_to_int(root_player.get('player_id')) == to_id:
                        to_jersey_num = self.__tag_value_to_int(root_player.get('jersey_num'))
                        to_position = self.__tag_value_to_str(root_player.get('position'))
                        to_x = self.__tag_value_to_float(root_player.get('x'))
                        to_y = self.__tag_value_to_float(root_player.get('y'))
                        dict_to = {'to_id': to_id, 'to_name': to_name, 
                                        'to_jersey_num': to_jersey_num,
                                        'to_position': to_position, 'to_x': to_x, 
                                        'to_y': to_y, 'num_passes': num_passes} 
                list_player_matrix.append({**dict_from, **dict_to})
            return list_player_matrix


    def __get_df_total_passes(self):
        df_sum_from = self.__df_pass_matrix.groupby(['from_id','from_name'], as_index=False)['num_passes'].sum()
        df_sum_to = self.__df_pass_matrix.groupby(['to_id','to_name'], as_index=False)['num_passes'].sum()
        df_merge = pd.merge(df_sum_from, df_sum_to, left_on='from_id', right_on='to_id', how='outer').fillna(0)
        df_merge['total_passes'] = (df_merge['num_passes_x'] + df_merge['num_passes_y'])
        df_merge = df_merge.astype({"from_id": int, "total_passes": int})
        return df_merge.loc[:, ['from_id', 'from_name', 'total_passes']]


    @staticmethod
    def __tag_value_to_str(value):
        if value is None:
            return ''
        return str(value)


    @staticmethod
    def __tag_value_to_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return UNDEFINED_INT


    @staticmethod
    def __tag_value_to_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return UNDEFINED_FLOAT


    @staticmethod
    def __tag_value_to_datetime(value):
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                pass
        return UNDEFINED_DATE


    @staticmethod
    def __order_players(df):
        df_ordered = df.copy()
        ordered_positions = ['Goalkeeper','Defender','Midfielder','Forward','Substitute']
        df_ordered['from_position'] = pd.CategoricalIndex(df['from_position'], ordered=True, categories=ordered_positions)
        return df_ordered.sort_values(['from_position', 'from_y'],
              ascending = [True, False])


    @staticmethod
    def __complementary_color(my_hex):
        if my_hex[0] == '#':
            my_hex = my_hex[1:]
        rgb = (my_hex[0:2], my_hex[2:4], my_hex[4:6])
        comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
        return f"#{''.join(comp)}"
    