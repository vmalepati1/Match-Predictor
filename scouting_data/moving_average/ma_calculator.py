import numpy as np
import tbapy
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from scouting_data.cleaning.col_utils import *


class MACalculator:

    def __init__(self, creds_filepath, tba_key, year, event_key, current_td_spreadsheet_id, previous_td_spreadsheet_id,
                 time_period=3):
        self.year = year
        self.event_key = event_key
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

    def groupiter(self, thing, n):
        def countiter(nextthing, thingiter, n):
            yield nextthing
            for _ in range(n - 1):
                yield next(thingiter)

        thingiter = iter(thing)
        while True:
            try:
                nextthing = next(thingiter)
            except StopIteration:
                return None
            yield countiter(nextthing, thingiter, n)

    def calculate_current_mas(self):
        for match_num, two_alliances_g in enumerate(self.groupiter(self.current_td_rows, 6), 1):
            red_alliance_data = []
            blue_alliance_data = []

            for team in two_alliances_g:
                team_number = int(team[0])
                current_team_data = [float(i) for i in team[2:]]

                if team_number not in self.current_team_dict:
                    self.current_team_dict[team_number] = []

                most_recent_cur_data = self.current_team_dict[team_number]

                num_prev_matches_needed = self.time_period - len(most_recent_cur_data)
                if num_prev_matches_needed > 0:
                    # New team in this competition that was not in previous competition
                    try:
                        most_recent_prev_data = self.previous_team_dict[team_number][-num_prev_matches_needed:]
                        team_most_recent_average_stats = np.average(most_recent_prev_data + most_recent_cur_data,
                                                                    axis=0)
                    except KeyError:
                        team_known_stats = most_recent_cur_data + [current_team_data]
                        team_most_recent_average_stats = np.average(team_known_stats, axis=0)
                else:
                    team_most_recent_average_stats = np.average(most_recent_cur_data[-self.time_period:], axis=0)

                red_alliance_teams = \
                    self.tba.match(year=self.year, event=self.event_key, type='qm', number=match_num)['alliances'][
                        'red'][
                        'team_keys']

                blue_alliance_teams = \
                    self.tba.match(year=self.year, event=self.event_key, type='qm', number=match_num)['alliances'][
                        'blue'][
                        'team_keys']

                for team_key in red_alliance_teams:
                    if team_number == self.tba.team(team_key)['team_number']:
                        red_alliance_data += team_most_recent_average_stats.tolist()

                for team_key in blue_alliance_teams:
                    if team_number == self.tba.team(team_key)['team_number']:
                        blue_alliance_data += team_most_recent_average_stats.tolist()

                self.current_team_dict[team_number].append(current_team_data)

            self.red_moving_averages.append(red_alliance_data)
            self.blue_moving_averages.append(blue_alliance_data)

        np.savez('scouting_dataset.npz', red=np.array(self.red_moving_averages),
                 blue=np.array(self.blue_moving_averages))


tester = MACalculator('C:/Users/User/Documents/Programming/Private/client_secret.json',
                      '1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM', 2019, '2019gadal',
                      '1Pgf_6Te2ssrva0vlkLGMnzL7vbWpuBp_JyVZKro43b0', '10qU_UfaTLN7zof8jTD-Op1uPONufrDcSBPyfDHd2mC4')
