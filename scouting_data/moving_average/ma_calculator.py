import numpy as np
import tbapy
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from scouting_data.cleaning.col_utils import *


class MACalculator:

    def __init__(self, creds_filepath, tba_key, year, event_key, current_td_spreadsheet_id, previous_td_spreadsheet_id,
                 output_filepath, team_combination_metric='s', time_period=3):
        """

        :type team_combination_metric: 's' for sum, 'a' for average, 'm' for median used to condense training features
        """
        self.year = year
        self.event_key = event_key
        self.output_filepath = output_filepath
        self.team_combination_metric = team_combination_metric
        self.time_period = time_period

        # Use credentials to create client and interact with Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_filepath, scope)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        self.previous_td_rows = self.get_rows(sheet, previous_td_spreadsheet_id)
        self.current_td_rows = self.get_rows(sheet, current_td_spreadsheet_id)

        self.previous_team_dict = {}
        self.init_previous_data()

        self.tba = tbapy.TBA(tba_key)
        self.current_team_dict = {}
        self.red_moving_averages = []
        self.blue_moving_averages = []
        self.calculate_current_mas()

    def get_rows(self, sheet, spreadsheet_id):
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range='Sheet1!A2:' + num_to_letter(len(relevant_column_names))).execute()
        values = result.get('values', [])
        return values

    def init_previous_data(self):
        # Team, data

        for row in self.previous_td_rows:
            team_number = int(row[0])

            if team_number not in self.previous_team_dict:
                self.previous_team_dict[team_number] = []

            self.previous_team_dict[team_number].append([float(i) for i in row[2:]])

    def calculate_current_mas(self):
        previous_match_num = int(self.current_td_rows[0][1])

        red_alliance_data = []
        blue_alliance_data = []

        for match_rec in self.current_td_rows:
            current_match_num = int(match_rec[1])

            if current_match_num != previous_match_num:
                if self.team_combination_metric == 's':
                    red_alliance_data_metric = np.sum(red_alliance_data, axis=0)
                    blue_alliance_data_metric = np.sum(blue_alliance_data, axis=0)
                elif self.team_combination_metric == 'a':
                    red_alliance_data_metric = np.average(red_alliance_data, axis=0)
                    blue_alliance_data_metric = np.average(blue_alliance_data, axis=0)
                elif self.team_combination_metric == 'm':
                    red_alliance_data_metric = np.median(red_alliance_data, axis=0)
                    blue_alliance_data_metric = np.median(blue_alliance_data, axis=0)
                else:
                    # User does not desire to condense training features
                    red_alliance_data_metric = [item for sublist in red_alliance_data for item in sublist]
                    blue_alliance_data_metric = [item for sublist in blue_alliance_data for item in sublist]

                print(red_alliance_data_metric)
                print(blue_alliance_data_metric)

                self.red_moving_averages.append(red_alliance_data_metric)
                self.blue_moving_averages.append(blue_alliance_data_metric)

                print('Processed match number %d' % previous_match_num)

                red_alliance_data = []
                blue_alliance_data = []

            previous_match_num = current_match_num

            team_number = int(match_rec[0])
            current_team_data = [float(i) for i in match_rec[2:]]

            if team_number not in self.current_team_dict:
                self.current_team_dict[team_number] = []

            most_recent_cur_data = self.current_team_dict[team_number]

            num_prev_matches_needed = self.time_period - len(most_recent_cur_data)
            if num_prev_matches_needed > 0:
                # New team in this competition that was not in previous competition
                try:
                    most_recent_prev_data = self.previous_team_dict[team_number][-num_prev_matches_needed:]
                    if len(most_recent_cur_data) > 0:
                        team_most_recent_average_stats = np.average(most_recent_prev_data + most_recent_cur_data,
                                                                    axis=1)
                    else:
                        team_most_recent_average_stats = np.average(most_recent_prev_data, axis=0)
                except KeyError or TypeError:
                    team_known_stats = [current_team_data] + most_recent_cur_data
                    team_most_recent_average_stats = np.average(team_known_stats, axis=0)
            else:
                team_most_recent_average_stats = np.average(most_recent_cur_data[-self.time_period:], axis=0)

            red_alliance_teams = \
                self.tba.match(year=self.year, event=self.event_key, type='qm', number=current_match_num)['alliances'][
                    'red'][
                    'team_keys']

            blue_alliance_teams = \
                self.tba.match(year=self.year, event=self.event_key, type='qm', number=current_match_num)['alliances'][
                    'blue'][
                    'team_keys']

            for team_key in red_alliance_teams:
                if team_number == self.tba.team(team_key)['team_number']:
                    red_alliance_data.append(team_most_recent_average_stats.tolist())

            for team_key in blue_alliance_teams:
                if team_number == self.tba.team(team_key)['team_number']:
                    blue_alliance_data.append(team_most_recent_average_stats.tolist())

            self.current_team_dict[team_number].append(current_team_data)

        np.savez(self.output_filepath, red=np.array(self.red_moving_averages),
                 blue=np.array(self.blue_moving_averages))


tester = MACalculator('C:\\Users\\Vikas Malepati\\Documents\\Programming\\Private\\client_secret.json',
                      '1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM', 2019, '2019gadal',
                      '1Pgf_6Te2ssrva0vlkLGMnzL7vbWpuBp_JyVZKro43b0', '10qU_UfaTLN7zof8jTD-Op1uPONufrDcSBPyfDHd2mC4',
                      'scouting_input.npz',
                      team_combination_metric='s')
