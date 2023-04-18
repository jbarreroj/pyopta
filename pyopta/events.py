import base64
import io
import os
from datetime import datetime
from random import sample
import xml.etree.ElementTree as ET

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch, VerticalPitch
from xhtml2pdf import pisa 

from constants import EVENT_IDS, QUALIFIER_IDS, UNDEFINED_INT, UNDEFINED_FLOAT, UNDEFINED_DATE
from Operator import *
from criteria import Criteria
from event import Event
from game import Game
from qualifier import Qualifier


class Events:
    
    def __init__(self, file_path):
        self.__game = None
        self.__df_players = []
        self.__df_teams = []
        self.__event_list = []        
        self.__parse_f24opta_file(file_path)
        self.__set_initial_players_df()


    def set_squads_info(self, file_path):
        df = self.__parse_squad_file(file_path)
        # Due to loans or tranfers there may be duplicate players
        df.drop_duplicates(inplace = True)
        self.__df_players = pd.merge(self.__df_players, df, left_on='player_id', right_on='player_id', how='inner')


    def get_df_players(self):
        return self.__df_players


    def get_df_teams(self):
        return self.__df_teams


    def get_match_info(self):
        return self.__game


    def get_df_all_events(self):
        events_list = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "type_id": ev.type_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y,
                                            "qualifiers": [{"id": x.id, "qualifier_id": x.qualifier_id, "value": x.value} for x in ev.qualifiers_list]}, self.__filter_event_list()))
        df = pd.DataFrame(events_list)
        return self.__merge_df_with_players_and_teams_info(df)


    def get_df_passes(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Pass'])
        criteria_passes_qualifiers = Criteria(Operator.QNIN, 
                            [QUALIFIER_IDS['Cross'], QUALIFIER_IDS['Free kick taken'],
                            QUALIFIER_IDS['Corner taken'], QUALIFIER_IDS['Throw In'],
                            QUALIFIER_IDS['Keeper Throw'], QUALIFIER_IDS['Goal Kick']])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id, 
                                                crit_qualifiers = criteria_passes_qualifiers)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns = ['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start', 'x_end', 'y_end'])
        else:
            passes = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y, 
                                            "x_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End X']), None),
                                            "y_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End Y']), None)}, filtered_list))
            df = pd.DataFrame(passes)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_passes_successful(self, player_id = None, team_id = None, period_id = None):
        df_total_passes = self.get_df_passes(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total_passes.query('outcome == 1').reset_index(drop=True)


    def get_df_passes_unsuccessful(self, player_id = None, team_id = None, period_id = None):
        df_total_passes = self.get_df_passes(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total_passes.query('outcome == 0').reset_index(drop=True)


    def get_df_aerial_duels(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Aerial'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            aerials = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(aerials)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_aerial_duels_successful(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_aerial_duels(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 1').reset_index(drop=True)


    def get_df_aerial_duels_unsuccessful(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_aerial_duels(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 0').reset_index(drop=True)


    def get_df_fouls(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Free kick'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            fouls = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(fouls)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_fouls_won(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_fouls(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 1').reset_index(drop=True)


    def get_df_fouls_conceded(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_fouls(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 0').reset_index(drop=True)


    def get_df_ball_recoveries(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Ball recovery'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            recoveries = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(recoveries)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_clearances(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Clearance'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            clearances = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(clearances)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_clearances_won(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_clearances(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 1').reset_index(drop=True)


    def get_df_clearances_lost(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_clearances(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 0').reset_index(drop=True)


    def get_df_corners(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Pass'])
        criteria_corners_qualifiers = Criteria(Operator.QIN, 
                            [QUALIFIER_IDS['Corner taken']])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id, 
                                                crit_qualifiers = criteria_corners_qualifiers)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns = ['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start', 'x_end', 'y_end'])
        else:
            corners = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y, 
                                            "x_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End X']), None),
                                            "y_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End Y']), None)}, filtered_list))
            df = pd.DataFrame(corners)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_shots(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.IN, [ EVENT_IDS['Miss'], EVENT_IDS['Post'],
                                                            EVENT_IDS['Attempt Saved'], EVENT_IDS['Goal'] ])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns = ['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start', 'goalmouth_y', 'goalmouth_z'])
        else:
            shots = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "type_id": ev.type_id,
                                            "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y, 
                                            "goalmouth_y": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Goal Mouth Y Coordinate']), None),
                                            "goalmouth_z": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Goal Mouth Z Coordinate']), None)}, filtered_list))
            df = pd.DataFrame(shots)
            map_types_id = {EVENT_IDS['Miss'] : "Miss",
                     EVENT_IDS['Post'] : "Post",
                     EVENT_IDS['Attempt Saved'] : "Attempt Saved",
                     EVENT_IDS['Goal'] : "Goal"}
            df['type_name'] = df['type_id'].map(map_types_id)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_crosses(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Pass'])
        criteria_cross_qualifiers = Criteria(Operator.QIN, [QUALIFIER_IDS['Cross']])
        criteria_extra_cross_qualifiers = Criteria(Operator.QNIN, 
                            [QUALIFIER_IDS['Free kick taken'],QUALIFIER_IDS['Corner taken']])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id, 
                                                crit_qualifiers = criteria_cross_qualifiers,
                                                extra_crit_qualifiers = criteria_extra_cross_qualifiers)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns = ['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start', 'x_end', 'y_end'])
        else:
            crosses = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y, 
                                            "x_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End X']), None),
                                            "y_end": next((q.value for q in ev.qualifiers_list if q.qualifier_id == QUALIFIER_IDS['Pass End Y']), None)}, filtered_list))
            df = pd.DataFrame(crosses)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_crosses_successful(self, player_id = None, team_id = None, period_id = None):
        df_total_crosses = self.get_df_crosses(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total_crosses.query('outcome == 1').reset_index(drop=True)


    def get_df_crosses_unsuccessful(self, player_id = None, team_id = None, period_id = None):
        df_total_crosses = self.get_df_crosses(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total_crosses.query('outcome == 0').reset_index(drop=True)


    def get_df_tackles(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Tackle'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            tackles = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(tackles)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_df_tackles_won_possession(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_tackles(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 1').reset_index(drop=True)


    def get_df_tackles_no_possession(self, player_id = None, team_id = None, period_id = None):
        df_total = self.get_df_tackles(player_id = player_id, team_id = team_id, period_id = period_id)
        return df_total.query('outcome == 0').reset_index(drop=True)


    def get_df_interceptions(self, player_id = None, team_id = None, period_id = None):
        criteria_event_type_id = Criteria(Operator.EQ, EVENT_IDS['Interception'])
        criteria_player_id = None if player_id is None else Criteria(Operator.EQ, player_id)
        criteria_team_id_id = None if team_id is None else Criteria(Operator.EQ, team_id)
        criteria_period_id = None if period_id is None else Criteria(Operator.EQ, period_id)

        filtered_list = self.__filter_event_list(crit_event_type_id = criteria_event_type_id, 
                                                crit_team_id = criteria_team_id_id,
                                                crit_player_id = criteria_player_id,
                                                crit_period_id = criteria_period_id)

        if len(filtered_list) == 0:
            return pd.DataFrame(columns=['id', 'event_id', 'period_id', 'min', 'sec', 'player_id', 
                            'team_id', 'outcome', 'x_start', 'y_start'])
        else:
            interceptions = list(map(lambda ev: {"id": ev.id, "event_id": ev.event_id, "period_id": ev.period_id,
                                            "min": ev.min, "sec": ev.sec, "player_id": ev.player_id,
                                            "team_id": ev.team_id, "outcome": ev.outcome, 
                                            "x_start": ev.x, "y_start": ev.y}, filtered_list))
            df = pd.DataFrame(interceptions)
            return self.__merge_df_with_players_and_teams_info(df)


    def get_pitch_passes(self, player_id = None, team_id = None, period_id = None):        
        stat = 'passes'
        df_successful = self.get_df_passes_successful(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_passes_unsuccessful(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_lines(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle())


    def get_pitch_aerial_duels(self, player_id = None, team_id = None, period_id = None):
        stat = 'aerial duels'
        df_successful = self.get_df_aerial_duels_successful(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_aerial_duels_unsuccessful(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle())


    def get_pitch_fouls(self, player_id = None, team_id = None, period_id = None):
        stat = 'fouls'
        df_successful = self.get_df_fouls_won(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_fouls_conceded(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle(), success_stat='Won', unsuccesss_stat='Conceded')


    def get_pitch_ball_recoveries(self, player_id = None, team_id = None, period_id = None):
        stat = 'ball recoveries'
        df_successful = self.get_df_ball_recoveries(player_id, team_id, period_id)
        
        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, None, stat, 
                title, self.__perform_subtitle(), success_stat='Won')


    def get_pitch_clearances(self, player_id = None, team_id = None, period_id = None):
        stat = 'clearances'
        df_successful = self.get_df_clearances_won(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_clearances_lost(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle(), success_stat='Won', unsuccesss_stat='Lost')


    def get_pitch_corners(self, player_id = None, team_id = None, period_id = None):
        stat = 'corners'
        df_successful = self.get_df_corners(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_vertical_lines(df_successful, None, stat, 
                title, self.__perform_subtitle(), success_stat='taken')


    def get_pitch_shots(self, player_id = None, team_id = None, period_id = None):
        stat = 'shots'
        df_shots = self.get_df_shots(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_vertical_shots(df_shots, stat, title, 
                        self.__perform_subtitle())


    def get_pitch_crosses(self, player_id = None, team_id = None, period_id = None):
        stat = 'crosses'
        df_successful = self.get_df_crosses_successful(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_crosses_unsuccessful(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_lines(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle())


    def get_pitch_tackles(self, player_id = None, team_id = None, period_id = None):
        stat = 'tackles'
        df_successful = self.get_df_tackles_won_possession(player_id, team_id, period_id)
        df_unsuccessful = self.get_df_tackles_no_possession(player_id, team_id, period_id)

        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, df_unsuccessful, stat, 
                title, self.__perform_subtitle(), success_stat='Won possession', 
                unsuccesss_stat='No possession')


    def get_pitch_interceptions(self, player_id = None, team_id = None, period_id = None):
        stat = 'interceptions'
        df_successful = self.get_df_interceptions(player_id, team_id, period_id)
        
        title = self.__define_plot_title(player_id, team_id, period_id, stat)
        return self.__define_pitch_scatter(df_successful, None, stat, 
                title, self.__perform_subtitle())


    def get_stats_passes(self, team_id = None):
        return self.__get_specific_stat('passes', self.get_df_passes, team_id = team_id)


    def get_stats_aerial_duels(self, team_id = None):
        return self.__get_specific_stat('aerial duels', self.get_df_aerial_duels, team_id = team_id)


    def get_stats_fouls(self, team_id = None):
        return self.__get_specific_stat('fouls', self.get_df_fouls, team_id = team_id, 
                        label_outcome1='won', label_outcome0='conceded')


    def get_stats_ball_recoveries(self, team_id = None):
        return self.__get_specific_stat_one_outcome('ball recoveries', self.get_df_ball_recoveries, 
                        team_id = team_id, label_outcome1='won')


    def get_stats_clearances(self, team_id = None):
        return self.__get_specific_stat('clearances', self.get_df_clearances, 
                        team_id = team_id, label_outcome1='won', label_outcome0='lost')


    def get_stats_corners(self, team_id = None):
        return self.__get_specific_stat_one_outcome('corners', self.get_df_corners, 
                        team_id = team_id, label_outcome1='taken')


    def get_stats_crosses(self, team_id = None):
        return self.__get_specific_stat('crosses', self.get_df_crosses, team_id = team_id)


    def get_stats_tackles(self, team_id = None):
        return self.__get_specific_stat('tackles', self.get_df_tackles, team_id = team_id, 
                        label_outcome1='won possession', label_outcome0='no possession')


    def get_stats_shots(self, team_id = None):
        df = pd.DataFrame(columns=['player_id', 'player_name', 'on_target', 'off_target', 
                'goal', 'attempt_saved', 'post', 'miss'])
        player_ids = self.__get_dict_all_players(team_id = team_id)
        for plid in player_ids:
            df_player_shots = self.get_df_shots(player_id = plid)
            player_name = ''
            if 'player_name' in self.__df_players.columns:
                player_name = self.__df_players.loc[self.__df_players['player_id'] == plid, 'player_name'].iloc[0]
            goal = len(df_player_shots.query(f"type_id == {EVENT_IDS['Goal']}")) if not df_player_shots.empty else 0
            attempt_saved = len(df_player_shots.query(f"type_id == {EVENT_IDS['Attempt Saved']}")) if not df_player_shots.empty else 0
            post = len(df_player_shots.query(f"type_id == {EVENT_IDS['Post']}")) if not df_player_shots.empty else 0
            miss = len(df_player_shots.query(f"type_id == {EVENT_IDS['Miss']}")) if not df_player_shots.empty else 0
            on_target = int(goal) + int(attempt_saved)
            off_target = int(post) + int(miss)
            df.loc[len(df)] = [plid, player_name, on_target, off_target, goal, attempt_saved, post, miss]
        df['player_id'] = pd.Series(df['player_id'] ,dtype = pd.Int64Dtype())
        df['on_target'] = pd.Series(df['on_target'] ,dtype = pd.Int64Dtype())
        df['off_target'] = pd.Series(df['off_target'] ,dtype = pd.Int64Dtype())
        df['goal'] = pd.Series(df['goal'] ,dtype = pd.Int64Dtype())
        df['attempt_saved'] = pd.Series(df['attempt_saved'] ,dtype = pd.Int64Dtype())
        df['post'] = pd.Series(df['post'] ,dtype = pd.Int64Dtype())
        df['miss'] = pd.Series(df['miss'] ,dtype = pd.Int64Dtype())
        return df.sort_values(by=['goal', 'attempt_saved', 'post', 'miss'], ascending=[False, False, False, False])


    def get_stats_interceptions(self, team_id = None):
        return self.__get_specific_stat_one_outcome('interceptions', self.get_df_interceptions, 
                        team_id = team_id)


    def get_bar_chart_passes(self, team_id = None):
        return self.__get_concrete_bar_chart('passes', self.get_stats_passes, team_id = team_id)


    def get_bar_chart_aerial_duels(self, team_id = None):
        return self.__get_concrete_bar_chart('aerial duels', self.get_stats_aerial_duels, team_id = team_id)


    def get_bar_chart_fouls(self, team_id = None):
        return self.__get_concrete_bar_chart('fouls', self.get_stats_fouls, team_id = team_id,
                    label_outcome1='won', label_outcome0='conceded')


    def get_bar_chart_ball_recoveries(self, team_id = None):
        return self.__get_concrete_bar_chart_one_outcome('ball_recoveries', self.get_stats_ball_recoveries, 
                    team_id = team_id, label_outcome1='won')


    def get_bar_chart_clearances(self, team_id = None):
        return self.__get_concrete_bar_chart('clearances', self.get_stats_clearances, team_id = team_id,
                    label_outcome1='won', label_outcome0='lost')


    def get_bar_chart_corners(self, team_id = None):
        return self.__get_concrete_bar_chart_one_outcome('corners', self.get_stats_corners, 
                    team_id = team_id, label_outcome1='taken')


    def get_bar_chart_crosses(self, team_id = None):
        return self.__get_concrete_bar_chart('crosses', self.get_stats_crosses, team_id = team_id)


    def get_bar_chart_tackles(self, team_id = None):
        return self.__get_concrete_bar_chart('tackles', self.get_stats_tackles, team_id = team_id,  
                    label_outcome1='won possession', label_outcome0='no possession')


    def get_bar_chart_interceptions(self, team_id = None):
        return self.__get_concrete_bar_chart_one_outcome('interceptions', 
                    self.get_stats_interceptions, team_id = team_id)


    def get_bar_chart_shots(self, team_id = None):        
        columns = ['player_id', 'goal', 'attempt_saved', 'post', 'miss']
        df_index = 'player_id'
        if 'player_name' in self.__df_players.columns:
            columns = ['player_name', 'goal', 'attempt_saved', 'post', 'miss']
            df_index = 'player_name' 
        df = self.get_stats_shots(team_id = team_id).loc[:, columns]
        df.sort_values(by=['goal', 'attempt_saved', 'post', 'miss'], ascending=[True, True, True, True], inplace=True)
        df.set_index(df_index, inplace=True)

        plt.rcParams["figure.figsize"] = [10, 6]
        df.plot(kind="barh", stacked=True, bottom=0.24) \
                    .legend(loc='lower right', ncol=2, title="Type")        
        plt.title(f"Total shots" + '\n' + f"{self.__perform_subtitle()}")
        if 'player_name' in self.__df_players.columns:
            plt.ylabel("Players")
        else:
            plt.ylabel("Players IDs")
        plt.xlabel("Shorts")
        return plt


    def get_player_heatmap(self, player_id):
        df_all_events = self.get_df_all_events()
        df_player_events = df_all_events.loc[df_all_events['player_id'] == player_id]

        pitch = Pitch(pitch_type = 'opta', line_color='#000009', line_zorder=2)
        fig, ax = pitch.draw(figsize=(10, 6))
        bin_statistic = pitch.bin_statistic(df_player_events.x_start.astype(float), 
                                            df_player_events.y_start.astype(float), 
                                            statistic='count', bins=(6, 5), normalize=True)
        pitch.heatmap(bin_statistic, ax=ax, cmap='Reds', edgecolor='#f9f9f9')
        pitch.scatter(df_player_events.x_start.astype(float), df_player_events.y_start.astype(float), 
                        s=10, c='#ff0000', edgecolors='#ff0000', ax=ax)

        # Title
        player_text = f"{df_player_events.sample().iloc[0]['player_name']}" \
                                        if 'player_name' in df_player_events.columns \
                                        else f"Player ID: {df_player_events.sample().iloc[0]['player_id']}"
        ax.set_title(f"EVENT DISTRIBUTION. {player_text}" + '\n' + self.__perform_subtitle(), fontsize=12)

        return plt


    def get_team_players_heatmap(self, team_id):
        df_all_events = self.get_df_all_events()
        df_team_events = df_all_events.loc[df_all_events['team_id'] == team_id]
        player_ids_list = pd.unique(df_team_events['player_id']).tolist()

        pitch = Pitch(pitch_type = 'opta', line_color='#000009', line_zorder=2)
        fig, axs = pitch.grid(nrows=4, ncols=4, figheight=30,
                      endnote_height=0.03, endnote_space=0,
                      axis=False,
                      title_height=0.08, grid_height=0.84)
        
        for i, ax in enumerate(axs['pitch'].flat):
            if i < len(player_ids_list):
                df_player_events = df_team_events.loc[df_team_events['player_id'] == player_ids_list[i]]
                bin_statistic = pitch.bin_statistic(df_player_events.x_start.astype(float), 
                                                df_player_events.y_start.astype(float), 
                                                statistic='count', bins=(6, 5), normalize=True)
                pitch.heatmap(bin_statistic, ax=ax, cmap='Reds', edgecolor='#f9f9f9')
                pitch.scatter(df_player_events.x_start.astype(float), df_player_events.y_start.astype(float), 
                                s=2, c='#ff0000', edgecolors='#ff0000', ax=ax)
                annotation_string = f"{df_player_events.sample().iloc[0]['player_name']}" \
                                        if 'player_name' in df_player_events.columns \
                                        else f"Player ID: {df_player_events.sample().iloc[0]['player_id']}"
                ax.set_title(annotation_string, fontsize=7, pad=0, loc='left')

        # Titles
        team_name = self.__df_teams[self.__df_teams['team_id'] == team_id].iloc[0]['team_name']
        main_title = f'EVENT DISTRIBUTION FOR EACH PLAYER - {team_name}'
        subtitle = self.__perform_subtitle()
        
        axs['title'].text(0.5, 0.7, main_title, color='#000000',
                  va='center', ha='center', fontsize=18)
        axs['title'].text(0.5, 0.25, subtitle, color='#b6bfb9',
                  va='center', ha='center', fontsize=12)

        return plt


    def get_team_passes_heatmap(self, team_id):
        df_team_passes = self.get_df_passes(team_id=team_id)

        pitch = VerticalPitch(pitch_type = 'opta', line_color='#000009', line_zorder=2)
        fig, axs = pitch.grid(nrows=1, ncols=2, figheight=30,
                      endnote_height=0.03, endnote_space=0,
                      axis=False,
                      title_height=0.08, grid_height=0.84)
        
        for i, ax in enumerate(axs['pitch'].flat):
            if i == 0:
                bin_statistic = pitch.bin_statistic(df_team_passes.x_start.astype(float), 
                                                    df_team_passes.y_start.astype(float), 
                                                    statistic='count', bins=(12, 10), normalize=True)
                pitch.heatmap(bin_statistic, ax=ax, cmap='Reds', edgecolor='#f9f9f9')
            elif i == 1:
                bin_statistic = pitch.bin_statistic(df_team_passes.x_end.astype(float), 
                                                    df_team_passes.y_end.astype(float), 
                                                    statistic='count', bins=(12, 10), normalize=True)
                pitch.heatmap(bin_statistic, ax=ax, cmap='Reds', edgecolor='#f9f9f9')

        # Title
        team_text = f"{df_team_passes.sample().iloc[0]['team_name']}"
        #ax.set_title(f"PASSES DISTRIBUTION. {team_text}" + '\n' + self.__perform_subtitle(), fontsize=12)
        axs['title'].text(0.5, 0.7, 
                    f"PASSES DISTRIBUTION. {team_text}" + '\n' + self.__perform_subtitle(), 
                    color='#000000', va='center', ha='center', fontsize=10)
        return plt


    def create_team_report(self, team_id, file_output):
        __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        TEMPLATE_FILE = "./templates/template_team_report.html"

        dict_params = {}

        # TEAM_NAME
        team_name = self.__df_teams[self.__df_teams['team_id'] == team_id].iloc[0]['team_name']
        dict_params["{{ TEAM_NAME }}"] = team_name

        # MATCH_INFO
        match_info = str(self.get_match_info())
        match_info = match_info[0:match_info.index('Additional info:')]
        dict_params["{{ MATCH_INFO }}"] = f"{match_info}. TEAM REPORT: {team_name}"

        # PASSES
        columns_passes = ['player_name', 'num_passes', 'successful', 'unsuccessful', 'ratio']
        df_passes = self.get_stats_passes(team_id=team_id).loc[:, columns_passes]
        df_passes.sort_values(by=['num_passes'], ascending=[False], inplace=True)
        dict_params["{{ TABLE_PASSES }}"] = str(df_passes.to_html(index=False))

        barchart_passes = self.get_bar_chart_passes(team_id=team_id)
        dict_params["{{ BARCHART_PASSES }}"] = self.__figure_to_base64(barchart_passes)

        pitch1_passes = self.get_pitch_passes(team_id=team_id, period_id=1)
        dict_params["{{ PITCH_HALF1_PASSES }}"] = self.__figure_to_base64(pitch1_passes)
        pitch2_passes = self.get_pitch_passes(team_id=team_id, period_id=2)        
        dict_params["{{ PITCH_HALF2_PASSES }}"] = self.__figure_to_base64(pitch2_passes)

        heatmap_passes = self.get_team_passes_heatmap(team_id)
        dict_params["{{ HEATMAP_PASSES }}"] = self.__figure_to_base64(heatmap_passes)

        # SHOTS        
        df_shots = self.get_stats_shots(team_id=team_id)
        df_shots.drop('player_id', axis=1, inplace=True)
        dict_params["{{ TABLE_SHOTS }}"] = str(df_shots.to_html(index=False))

        barchart_shots = self.get_bar_chart_shots(team_id=team_id)
        dict_params["{{ BARCHART_SHOTS }}"] = self.__figure_to_base64(barchart_shots)

        pitch_shots = self.get_pitch_shots(team_id=team_id)
        dict_params["{{ PITCH_SHOTS }}"] = self.__figure_to_base64(pitch_shots)

        # CORNERS
        df_corners = self.get_stats_corners(team_id=team_id)
        df_corners.drop(['player_id', 'taken'], axis=1, inplace=True)
        dict_params["{{ TABLE_CORNERS }}"] = str(df_corners.to_html(index=False))

        pitch_corners = self.get_pitch_corners(team_id=team_id)
        dict_params["{{ PITCH_CORNERS }}"] = self.__figure_to_base64(pitch_corners)

        # CROSSES
        df_crosses = self.get_stats_crosses(team_id=team_id)
        df_crosses.drop('player_id', axis=1, inplace=True)
        df_crosses.sort_values(by=['num_crosses'], ascending=[False], inplace=True)
        dict_params["{{ TABLE_CROSSES }}"] = str(df_crosses.to_html(index=False))

        barchart_crosses = self.get_bar_chart_crosses(team_id=team_id)
        dict_params["{{ BARCHART_CROSSES }}"] = self.__figure_to_base64(barchart_crosses)

        pitch_crosses = self.get_pitch_crosses(team_id=team_id)
        dict_params["{{ PITCH_CROSSES }}"] = self.__figure_to_base64(pitch_crosses)

        # BALL RECOVERIES
        df_recoveries = self.get_stats_ball_recoveries(team_id=team_id)
        df_recoveries.drop(['player_id', 'won'], axis=1, inplace=True)
        dict_params["{{ TABLE_RECOVERIES }}"] = str(df_recoveries.to_html(index=False))
        
        pitch_recoveries = self.get_pitch_ball_recoveries(team_id=team_id)
        dict_params["{{ PITCH_RECOVERIES }}"] = self.__figure_to_base64(pitch_recoveries)

        # AERIALS
        df_aerials = self.get_stats_aerial_duels(team_id=team_id)
        df_aerials.drop('player_id', axis=1, inplace=True)
        df_aerials.sort_values(by=['num_aerial duels'], ascending=[False], inplace=True)
        dict_params["{{ TABLE_AERIALS }}"] = str(df_aerials.to_html(index=False))

        barchart_aerials = self.get_bar_chart_aerial_duels(team_id=team_id)
        dict_params["{{ BARCHART_AERIALS }}"] = self.__figure_to_base64(barchart_aerials)

        pitch_aerials = self.get_pitch_aerial_duels(team_id=team_id)
        dict_params["{{ PITCH_AERIALS }}"] = self.__figure_to_base64(pitch_aerials)

        # CLEARANCES
        df_clearances = self.get_stats_clearances(team_id=team_id)
        df_clearances.drop('player_id', axis=1, inplace=True)
        df_clearances.sort_values(by=['num_clearances'], ascending=[False], inplace=True)
        dict_params["{{ TABLE_CLEARANCES }}"] = str(df_clearances.to_html(index=False))

        barchart_clearances = self.get_bar_chart_clearances(team_id=team_id)
        dict_params["{{ BARCHART_CLEARANCES }}"] = self.__figure_to_base64(barchart_clearances)

        pitch_clearances = self.get_pitch_clearances(team_id=team_id)
        dict_params["{{ PITCH_CLEARANCES }}"] = self.__figure_to_base64(pitch_clearances)

        # EVENTS
        pitch_event_dist = self.get_team_players_heatmap(team_id=team_id)
        dict_params["{{ EVENT_DISTRIBUTION }}"] = self.__figure_to_base64(pitch_event_dist)
        
        # Create report
        report_html = self.__create_html_report(os.path.join(__location__, TEMPLATE_FILE), dict_params)
        self.__convert_html_to_pdf(report_html, file_output)


    def __parse_f24opta_file(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        game_tag = root.find('Game')
        self.__game = self.__parse_game_tag(game_tag)
        self.__event_list = self.__parse_event_tags(game_tag)


    def __parse_squad_file(self, file_path):
        df_players = pd.DataFrame(columns=['player_id', 'player_name', 'first_name', 'last_name', 'known_name'])
        tree = ET.parse(file_path)
        root = tree.getroot()        
        list_team_tag = root.findall('.//Team')
        for team_tag in list_team_tag:
            for player_tag in team_tag.iter('Player'):
                player_id = self.__tag_value_to_int(player_tag.get('uID')[1:])
                name = self.__tag_value_to_str(player_tag.find('Name').text)
                first_name = ''
                last_name = ''
                known_name = ''
                for stat_tag in player_tag.iter('Stat'):
                    if stat_tag.get('Type') == 'name':
                        name = self.__tag_value_to_str(stat_tag.text)
                    elif stat_tag.get('Type') == 'first_name':
                        first_name = self.__tag_value_to_str(stat_tag.text)
                    elif stat_tag.get('Type') == 'last_name':
                        last_name = self.__tag_value_to_str(stat_tag.text)
                    elif stat_tag.get('Type') == 'known_name':
                        known_name = self.__tag_value_to_str(stat_tag.text)
                df_players.loc[len(df_players)] = [player_id, name, first_name, last_name, known_name]
        return df_players


    def __set_initial_players_df(self):
        set_player_ids = set()
        for ev in self.__event_list:
            if ev.player_id is not None and ev.player_id != UNDEFINED_INT:
                set_player_ids.add(ev.player_id)
        df = pd.DataFrame(list(set_player_ids)) 
        df.columns = ['player_id']
        self.__df_players = df


    def __set_initial_teams_df(self, home_team_id, home_team_name, away_team_id, away_team_name):
        df_teams = pd.DataFrame(columns=['team_id', 'team_name'])
        df_teams.loc[0] = [home_team_id, home_team_name]
        df_teams.loc[1] = [away_team_id, away_team_name]
        self.__df_teams = df_teams
        

    def __parse_game_tag(self, game_tag):
        match_id = self.__tag_value_to_int(game_tag.get('id'))
        additional_info = self.__tag_value_to_str(game_tag.get('additional_info'))
        away_score = self.__tag_value_to_int(game_tag.get('away_score'))
        away_team_id = self.__tag_value_to_int(game_tag.get('away_team_id'))
        away_team_name = self.__tag_value_to_str(game_tag.get('away_team_name'))
        competition_id = self.__tag_value_to_int(game_tag.get('competition_id'))
        competition_name = self.__tag_value_to_str(game_tag.get('competition_name'))
        game_date = self.__tag_value_to_datetime(game_tag.get('game_date'))
        home_score = self.__tag_value_to_int(game_tag.get('home_score'))
        home_team_id = self.__tag_value_to_int(game_tag.get('home_team_id'))
        home_team_name = self.__tag_value_to_str(game_tag.get('home_team_name'))
        matchday = self.__tag_value_to_int(game_tag.get('matchday'))
        period_1_start = self.__tag_value_to_datetime(game_tag.get('period_1_start'))
        period_2_start = self.__tag_value_to_datetime(game_tag.get('period_2_start'))
        season_id = self.__tag_value_to_int(game_tag.get('season_id'))
        season_name = self.__tag_value_to_str(game_tag.get('season_name'))
        self.__set_initial_teams_df(home_team_id, home_team_name, away_team_id, away_team_name)
        return Game(match_id = match_id, additional_info = additional_info, away_score = away_score, 
                    away_team_id = away_team_id, away_team_name = away_team_name, 
                    competition_id = competition_id, competition_name = competition_name,
                    game_date = game_date, home_score = home_score, home_team_id= home_team_id,
                    home_team_name = home_team_name, matchday = matchday, 
                    period_1_start = period_1_start, period_2_start = period_2_start,
                    season_id = season_id, season_name = season_name)


    def __parse_event_tag(self, event_tag):
        id = self.__tag_value_to_int(event_tag.get('id'))
        event_id = self.__tag_value_to_int(event_tag.get('event_id'))
        type_id = self.__tag_value_to_int(event_tag.get('type_id'))
        period_id = self.__tag_value_to_int(event_tag.get('period_id'))
        min = self.__tag_value_to_int(event_tag.get('min'))
        sec = self.__tag_value_to_int(event_tag.get('sec'))
        team_id = self.__tag_value_to_int(event_tag.get('team_id'))
        player_id = self.__tag_value_to_int(event_tag.get('player_id'))
        outcome = self.__tag_value_to_int(event_tag.get('outcome'))
        assist = self.__tag_value_to_int(event_tag.get('assist'))
        keypass = self.__tag_value_to_int(event_tag.get('keypass'))
        x = self.__tag_value_to_float(event_tag.get('x'))
        y = self.__tag_value_to_float(event_tag.get('y'))
        timestamp = self.__tag_value_to_datetime(event_tag.get('timestamp'))
        last_modified = self.__tag_value_to_datetime(event_tag.get('last_modified'))
        qualifiers_list = self.__parse_qualifier_tags(event_tag)
        return Event(id = id, event_id = event_id, type_id = type_id, period_id = period_id,
                    min = min, sec = sec, team_id = team_id, player_id = player_id,
                    outcome = outcome, assist = assist, keypass = keypass, x = x, y = y,
                    timestamp = timestamp, last_modified = last_modified,
                    qualifiers_list = qualifiers_list)


    def __parse_qualifier_tag(self, qualifier_tag):
        id = self.__tag_value_to_int(qualifier_tag.get('id'))
        qualifier_id = self.__tag_value_to_int(qualifier_tag.get('qualifier_id'))
        value = self.__tag_value_to_str(qualifier_tag.get('value'))
        return Qualifier(id = id, qualifier_id = qualifier_id, value = value)


    def __parse_event_tags(self, game_tag):
        events_list = []
        for event in game_tag.iter('Event'):
            events_list.append(self.__parse_event_tag(event))
        return events_list


    def __parse_qualifier_tags(self, event_tag):
        qualifier_list = []
        for qualifier in event_tag.iter('Q'):
            qualifier_list.append(self.__parse_qualifier_tag(qualifier))
        return qualifier_list


    def __filter_event_list(self, crit_event_type_id = None, crit_team_id = None, crit_player_id = None,
                            crit_period_id = None, crit_min = None, crit_sec = None,
                            crit_outcome = None, crit_x = None, crit_y = None,
                            crit_qualifiers = None, extra_crit_qualifiers = None):
        return list(filter(lambda ev: self.__filter_event(ev, crit_event_type_id, crit_team_id, 
                        crit_player_id, crit_period_id, crit_min, crit_sec, crit_outcome,
                        crit_x, crit_y, crit_qualifiers, extra_crit_qualifiers), self.__event_list))


    def __filter_event(self, ev, crit_event_type_id = None, crit_team_id = None, crit_player_id = None,
                        crit_period_id = None, crit_min = None, crit_sec = None, crit_outcome = None,
                        crit_x = None, crit_y = None, crit_qualifiers = None, 
                        extra_crit_qualifiers = None):
        if (crit_event_type_id is not None and not self.__check_criteria(ev.type_id, crit_event_type_id)
            or crit_player_id is not None and not self.__check_criteria(ev.player_id, crit_player_id)
            or crit_team_id is not None and not self.__check_criteria(ev.team_id, crit_team_id)
            or crit_period_id is not None and not self.__check_criteria(ev.period_id, crit_period_id)
            or crit_min is not None and not self.__check_criteria(ev.min, crit_min)
            or crit_sec is not None and not self.__check_criteria(ev.sec, crit_sec)
            or crit_outcome is not None and not self.__check_criteria(ev.outcome, crit_outcome)
            or crit_x is not None and not self.__check_criteria(ev.x, crit_x)
            or crit_y is not None and not self.__check_criteria(ev.y, crit_y)
            or crit_qualifiers is not None and not self.__check_criteria(ev.qualifiers_list, crit_qualifiers)
            or extra_crit_qualifiers is not None and not self.__check_criteria(ev.qualifiers_list, extra_crit_qualifiers)):
            return False
        else:
            return True


    def __check_criteria(self, attr_value, criteria):
        return criteria.perform_operation(attr_value)


    def __get_dict_all_players(self, team_id = None):
        set_player_ids = set()
        for ev in self.__event_list:
            if ev.player_id is not None and ev.player_id != UNDEFINED_INT:
                if team_id is None or (ev.team_id is not None and ev.team_id == team_id):
                    set_player_ids.add(ev.player_id)
        return set_player_ids


    def __define_pitch_lines(self, df_successful, df_unsuccessful, label_stat = '', 
                                label_title = '', label_subtitle = ''):
        
        pitch = Pitch(pitch_type = 'opta', pitch_color='grass', line_color='white',
                        stripe=True)
        fig, ax = pitch.draw(figsize=(10, 6))

        # Plot successful stat
        if df_successful is not None:
            pitch.scatter(df_successful.x_start.astype(float), df_successful.y_start.astype(float), 
                        s=15, c='#ff0000', edgecolors='#ff0000', ax=ax)
        # Plot unsuccessful stat
        if df_unsuccessful is not None:
            pitch.scatter(df_unsuccessful.x_start.astype(float), df_unsuccessful.y_start.astype(float), 
                    s=15, c='#000000', edgecolors='#000000', ax=ax)
        
        # Arrow successful stat
        pitch.arrows(df_successful.x_start.astype(float), df_successful.y_start.astype(float),
                    df_successful.x_end.astype(float), df_successful.y_end.astype(float), width=2,
                    headwidth=5, headlength=5, color='#ff0000', ax=ax, label=f'Successful {label_stat}')
        # Arrow unsuccessful stat            
        pitch.arrows(df_unsuccessful.x_start.astype(float), df_unsuccessful.y_start.astype(float),
                    df_unsuccessful.x_end.astype(float), df_unsuccessful.y_end.astype(float), width=2,
                    headwidth=5, headlength=5, color='#000000', ax=ax, label=f'Unsuccessful {label_stat}')
        
        # Legend
        ax.legend(facecolor='#73a792', handlelength=4, edgecolor='None', fontsize=10, loc='upper left')
        
        # Title
        ax.set_title(label_title + '\n' + label_subtitle, fontsize=12)
       
        return plt


    def __define_pitch_vertical_lines(self, df_successful, df_unsuccessful, label_stat = '', 
                        label_title = '', label_subtitle = '', success_stat = 'Successful', 
                        unsuccesss_stat = 'Unsuccessful'):
        
        pitch = VerticalPitch(pitch_type = 'opta', pitch_color='grass', line_color='white',
                        stripe=True, pad_bottom=0.5, half=True, goal_type='box')
        fig, ax = pitch.draw(figsize=(10, 6))
        
        # Plot successful stat
        if df_successful is not None:
            pitch.arrows(df_successful.x_start.astype(float), df_successful.y_start.astype(float),
                    df_successful.x_end.astype(float), df_successful.y_end.astype(float), width=2,
                    headwidth=5, headlength=5, color='#ff0000', ax=ax, label=f'{label_stat} {success_stat}')
        # Plot unsuccessful stat
        if df_unsuccessful is not None:
            pitch.arrows(df_unsuccessful.x_start.astype(float), df_unsuccessful.y_start.astype(float),
                    df_unsuccessful.x_end.astype(float), df_unsuccessful.y_end.astype(float), width=2,
                    headwidth=5, headlength=5, color='#000000', ax=ax, label=f'{label_stat} {unsuccesss_stat}')
        
        # Legend
        ax.legend(facecolor='#73a792', handlelength=4, edgecolor='None', fontsize=10, loc='lower center')
        
        # Title
        ax.set_title(label_title + '\n' + label_subtitle, fontsize=12)
       
        return plt


    def __define_pitch_vertical_shots(self, df_shots, label_stat = '', 
                        label_title = '', label_subtitle = ''):
        
        pitch = VerticalPitch(pitch_type = 'opta', pitch_color='grass', line_color='white',
                        stripe=True, pad_bottom=0.5, half=True, goal_type='box')
        fig, ax = pitch.draw(figsize=(10, 6))
        
        df_miss = df_shots[df_shots['type_id'] == EVENT_IDS['Miss']]
        df_post = df_shots[df_shots['type_id'] == EVENT_IDS['Post']]
        df_attempt_saved = df_shots[df_shots['type_id'] == EVENT_IDS['Attempt Saved']]
        df_goal = df_shots[df_shots['type_id'] == EVENT_IDS['Goal']]

        if len(df_miss) > 0:
            pitch.scatter(df_miss.x_start.astype(float), df_miss.y_start.astype(float), 
                        s=65, c='#000000', edgecolors='#ffffff', ax=ax, label='Off target')
        
        if len(df_post) > 0:
            pitch.scatter(df_post.x_start.astype(float), df_post.y_start.astype(float), 
                        s=65, c='#f1c232', edgecolors='#ffffff', ax=ax, label='Goalpost')

        if len(df_attempt_saved) > 0:
            pitch.scatter(df_attempt_saved.x_start.astype(float), df_attempt_saved.y_start.astype(float), 
                        s=65, c='#0000ff', edgecolors='#ffffff', ax=ax, label='On target')

        if len(df_goal) > 0:
            pitch.scatter(df_goal.x_start.astype(float), df_goal.y_start.astype(float), 
                        s=80, c='#ff0000', edgecolors='#ffffff', ax=ax, label='Goal',
                        marker='*')
        
        # Legend
        ax.legend(facecolor='#73a792', handlelength=4, edgecolor='None', fontsize=10, loc='lower center')
        
        # Title
        ax.set_title(label_title + '\n' + label_subtitle, fontsize=12)
       
        return plt


    def __define_pitch_scatter(self, df_successful, df_unsuccessful, label_stat = '', 
                        label_title = '', label_subtitle = '', success_stat = 'Successful', 
                        unsuccesss_stat = 'Unsuccessful'):
        
        pitch = Pitch(pitch_type = 'opta', pitch_color='grass', line_color='white',
                        stripe=True)
        fig, ax = pitch.draw(figsize=(10, 6))
        
        # Plot successful stat
        if df_successful is not None:
            pitch.scatter(df_successful.x_start.astype(float), df_successful.y_start.astype(float), 
                        s=24, c='#ff0000', edgecolors='#383838', ax=ax, label=f'{label_stat} {success_stat}')
        # Plot unsuccessful stat
        if df_unsuccessful is not None:
            pitch.scatter(df_unsuccessful.x_start.astype(float), df_unsuccessful.y_start.astype(float), 
                    s=24, c='#000000', edgecolors='#383838', ax=ax, label=f'{label_stat} {unsuccesss_stat}')
        
        # Legend
        ax.legend(facecolor='#73a792', handlelength=4, edgecolor='None', fontsize=10, loc='upper left')
        
        # Title
        ax.set_title(label_title + '\n' + label_subtitle, fontsize=12)
       
        return plt


    def __get_specific_stat(self, stat, fn_get_stat, team_id = None,
                            label_outcome1 = 'successful', label_outcome0 = 'unsuccessful'):
        num_stat = f'num_{stat}'
        df = pd.DataFrame(columns=['player_id', 'player_name', num_stat, label_outcome1, label_outcome0, 'ratio'])
        player_ids = self.__get_dict_all_players(team_id = team_id)
        for plid in player_ids:
            df_player = fn_get_stat(player_id = plid)
            player_name = ''
            if 'player_name' in self.__df_players.columns:
                player_name = self.__df_players.loc[self.__df_players['player_id'] == plid, 'player_name'].iloc[0]
            num_successful = len(df_player.query('outcome == 1')) if not df_player.empty else 0
            num_unsuccessful = len(df_player.query('outcome == 0')) if not df_player.empty else 0
            ratio = self.__compute_percentage(num_successful / (num_successful + num_unsuccessful) if (num_successful + num_unsuccessful) else 0)
            df.loc[len(df)] = [plid, player_name, len(df_player.index), num_successful, num_unsuccessful, ratio]
        df['player_id'] = pd.Series(df['player_id'] ,dtype = pd.Int64Dtype())
        df[num_stat] = pd.Series(df[num_stat] ,dtype = pd.Int64Dtype())
        df[label_outcome1] = pd.Series(df[label_outcome1] ,dtype = pd.Int64Dtype())
        df[label_outcome0] = pd.Series(df[label_outcome0] ,dtype = pd.Int64Dtype())
        return df.sort_values(by=['ratio', label_outcome1, label_outcome0], ascending=[False, False, True])


    def __get_specific_stat_one_outcome(self, stat, fn_get_stat, team_id = None, 
                            label_outcome1 = 'successful'):
        num_stat = f'num_{stat}'
        df = pd.DataFrame(columns=['player_id', 'player_name', num_stat, label_outcome1])
        player_ids = self.__get_dict_all_players(team_id = team_id)
        for plid in player_ids:
            df_player = fn_get_stat(player_id = plid)
            player_name = ''
            if 'player_name' in self.__df_players.columns:
                player_name = self.__df_players.loc[self.__df_players['player_id'] == plid, 'player_name'].iloc[0]
            num_successful = len(df_player) if not df_player.empty else 0 
            df.loc[len(df)] = [plid, player_name, len(df_player.index), num_successful]
        df['player_id'] = pd.Series(df['player_id'] ,dtype = pd.Int64Dtype())
        df[num_stat] = pd.Series(df[num_stat] ,dtype = pd.Int64Dtype())
        df[label_outcome1] = pd.Series(df[label_outcome1] ,dtype = pd.Int64Dtype())        
        return df.sort_values(by=[label_outcome1], ascending=[False])


    def __get_concrete_bar_chart(self, stat, fn_get_stat, team_id = None,
                    label_outcome1 = 'successful', label_outcome0 = 'unsuccessful'):
        plt.rcParams["figure.figsize"] = [10, 6]
        df = fn_get_stat(team_id = team_id)
        df_for_chart = self.__prepare_df_for_chart(df, label_outcome1, label_outcome0)  
        df_for_chart.plot(kind="barh", stacked=True, bottom=0.24) \
                    .legend(loc='lower right', ncol=2, title="Type")        
        plt.title(f"Total {stat}" + '\n' + f"{self.__perform_subtitle()}")
        if 'player_name' in self.__df_players.columns:
            plt.ylabel("Players")
        else:
            plt.ylabel("Players IDs")
        plt.xlabel(f"{stat.capitalize()}")
        return plt


    def __get_concrete_bar_chart_one_outcome(self, stat, fn_get_stat, team_id = None,
                    label_outcome1 = 'successful'):
        plt.rcParams["figure.figsize"] = [10, 6]
        df = fn_get_stat(team_id = team_id)
        df_for_chart = self.__prepare_df_for_chart_one_outcome(df, label_outcome1)  
        df_for_chart.plot(kind="barh", bottom=0) \
                    .legend(loc='lower right', ncol=2, title="Type")        
        plt.title(f"Total {stat}" + '\n' + f"{self.__perform_subtitle()}")
        if 'player_name' in self.__df_players.columns:
            plt.ylabel("Players")
        else:
            plt.ylabel("Players IDs")
        plt.xlabel(f"{stat.capitalize()}")
        return plt


    def __merge_df_with_players_and_teams_info(self, df):
        df_copy = df.copy()
        df_copy = pd.merge(df_copy, self.__df_teams, left_on='team_id', right_on='team_id', how='inner')
        if 'player_name' in self.__df_players.columns:
            df_copy = pd.merge(df_copy, self.__df_players, left_on='player_id', right_on='player_id', how='inner')
        return df_copy


    def __define_plot_title(self, player_id, team_id, period_id, stat):
        label_period = ''
        if period_id is not None:
            if period_id == 1:
                label_period = '1st half'
            elif period_id == 2:
                label_period = '2nd half'
        if player_id is not None:
            label_player = ''
            if 'player_name' in self.__df_players.columns:
                player_name = self.__df_players.loc[self.__df_players['player_id'] == player_id, 'player_name'].iloc[0]
                label_player = f'Player name: {player_name}'
            else:
                label_player = f'Player id: {player_id}'
            return f'{stat.capitalize()} {label_period}. {label_player}'
        elif team_id is not None:
            team_name = self.__df_teams.loc[self.__df_teams['team_id'] == team_id, 'team_name'].iloc[0]
            label_team = f'Team name: {team_name}'
            return f'{stat.capitalize()} {label_period}. {label_team}'
        else: 
            return f'Match {stat}{label_period}'


    def __prepare_df_for_chart(self, df, label_outcome1 = 'successful', label_outcome0 = 'unsuccessful'):
        columns = ['player_id', label_outcome1, label_outcome0]
        df_index = 'player_id'
        if 'player_name' in self.__df_players.columns:
            columns = ['player_name', label_outcome1, label_outcome0]
            df_index = 'player_name'
        df2 = df.loc[:, columns]
        df2.sort_values(by=[label_outcome1, label_outcome0], ascending=[True, False], inplace=True)
        df2.set_index(df_index, inplace=True)
        return df2


    def __prepare_df_for_chart_one_outcome(self, df, label_outcome1 = 'successful'):
        columns = ['player_id', label_outcome1]
        df_index = 'player_id'
        if 'player_name' in self.__df_players.columns:
            columns = ['player_name', label_outcome1]
            df_index = 'player_name'
        df2 = df.loc[:, columns]
        df2.sort_values(by=[label_outcome1], ascending=[True], inplace=True)
        df2.set_index(df_index, inplace=True)
        return df2


    def __perform_subtitle(self):
        return f'{self.__game.competition_name} ({self.__game.season_name}). Date: {self.__game.game_date}. {self.__game.home_team_name} {self.__game.home_score} - {self.__game.away_score} {self.__game.away_team_name}'


    def __create_html_report(self, template_file, replace_params):
        template_html = ''
        with open(template_file,'r') as f:
            template_html = f.read()
        for k,v in replace_params.items():
            template_html = template_html.replace(k, v)
        return template_html


    def __convert_html_to_pdf(self, source_html, output_filename):
        with open(f"{output_filename}", "w+b") as f:
            pisa_status = pisa.CreatePDF(source_html, dest=f)
        return pisa_status.err
    

    def __figure_to_base64(self, figure):
        image_html = ""
        s = io.BytesIO()
        figure.savefig(s, format='png')
        figure.close()
        s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
        image_html += (f'<img src="data:image/png;base64,{s}"><br>')
        return image_html


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
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                pass
        return UNDEFINED_DATE


    @staticmethod
    def __compute_percentage(x):
        return round(x * 100, 2)

