import argparse
import pickle
import time
from collections import OrderedDict

import numpy as np
import pandas as pd
import tbapy
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from scouting_data.cleaning.col_utils import *
import scouting_data.cleaning.quantifier_funcs as qf

from match_classifier import MatchClassifier
from match_deep_learning import MatchDeepLearning
from match_linear_regression import MatchLinearRegression


class MARealTime:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Analyze an event in real-time using scouting data and optional TBA data or Sykes data.')

        parser.add_argument('predictor_filepath', metavar='predictor-filepath', type=str,
                            help='filepath to a pickled match predictor file')
        parser.add_argument('tba_api_key', metavar='tba-api-key', type=str,
                            help='your The Blue Alliance key that you can create in your TBA Account Dashboard')
        parser.add_argument('event_key', metavar='event-key', type=str, help='TBA event key of the competition')
        parser.add_argument('relevant_sort_order_stats', metavar='relevant-sort-order-stats', type=int, default=-1,
                            help='number of actual values within sort_orders that excludes any placeholder 0s at the '
                                 'end')
        parser.add_argument('comp_year', metavar='comp-year', type=int, help='year of the competition')
        parser.add_argument('update_wait_time', metavar='--update-wait-time', type=float, default=1.5,
                            help="time between real-time updates")
        parser.add_argument('-nspf', '--no-scouting-data-predictor-filepath', type=str,
                            help="filepath to a predictor trained without scouting data which will be used if a new "
                                 "team showed up in the current competition and wasn't scouted in the previous "
                                 "competitions")
        parser.add_argument('-gsc', '--google-sheets-creds-filepath', type=str,
                            help='filepath to a credentials JSON file created by Google for your service account')
        parser.add_argument('-csi', '--current-scouting-spreadsheet-id', type=str,
                            help='the key of the real-time updating scouting spreadsheet shared with your service '
                                 'account')
        parser.add_argument('-psi', '--previous-scouting-spreadsheet-ids', nargs='+', type=str,
                            help='sorted priority list of the names of the previous competition scouting spreadsheets '
                                 'shared with your service account which are used as a reference for first matches')
        parser.add_argument('-map', '--moving-average-time-period', type=int,
                            help="number of previous matches averaged per team before each prediction")
        parser.add_argument('-syf', '--sykes-filepath', type=str,
                            help='filepath to a Sykes scouting database Excel file with extension .xlsx')

        args = parser.parse_args()

        predictor_file = open(args.predictor_filepath, 'rb')
        self.predictor = pickle.load(predictor_file)

        self.has_no_scouting_predictor = False

        if args.no_scouting_data_predictor_filepath:
            self.has_no_scouting_predictor = True
            no_scouting_predictor_file = open(args.no_scouting_data_predictor_filepath, 'rb')
            self.no_scouting_predictor = pickle.load(no_scouting_predictor_file)

        self.tba = tbapy.TBA(args.tba_api_key)
        self.event_key = args.event_key
        self.relevant_sort_order_stats = args.relevant_sort_order_stats
        self.comp_year = args.comp_year

        if args.google_sheets_creds_filepath or args.current_scouting_spreadsheet_id \
                or args.previous_scouting_spreadsheet_ids or args.moving_average_time_period:
            # Mutually inclusive arguments
            if not args.google_sheets_creds_filepath or not args.current_scouting_spreadsheet_id \
                    or not args.previous_scouting_spreadsheet_ids or not args.moving_average_time_period:
                raise ValueError('-gsc -csi -psi and -map must all be specified if you wish to use scouting data')

            self.gs_creds_filepath = args.google_sheets_creds_filepath
            self.current_scouting_spreadsheet_id = args.current_scouting_spreadsheet_id
            self.previous_scouting_spreadsheet_ids = args.previous_scouting_spreadsheet_ids
            self.moving_average_time_period = args.moving_average_time_period
        else:
            # None were specified but are required
            if self.predictor.header['use_scouting_data']:
                raise ValueError('You must specify arguments -gsc -csi -psi and -map to make predictions')

        if not args.sykes_filepath and self.predictor.header['use_sykes_data']:
            raise ValueError('You must provide a sykes filepath to make predictions')
        elif self.has_no_scouting_predictor:
            if not args.sykes_filepath and self.no_scouting_predictor.header['use_sykes_data']:
                raise ValueError('You must provide a sykes filepath to make predictions')
        else:
            self.sykes_filepath = args.sykes_filepath

        self.current_team_dict = {}
        self.run()

    def get_rows(self, sheet, spreadsheet_id):
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range='Sheet1!A2:' + num_to_letter(len(relevant_column_names))).execute()
        values = result.get('values', [])
        return values

    def get_team_last_event(self, team_key):
        events = self.tba.team_events(team_key, self.comp_year)

        event_dict_unordered = dict((x['start_date'], x) for x in events)
        event_dict_ordered = OrderedDict(sorted(event_dict_unordered.items(), key=lambda t: t[0]))

        return list(event_dict_ordered.items())[-1][1]

    def get_team_sykes_data(self, event_df, team_number):
        sykes_data = []

        for column_name in self.predictor.header['sykes_columns']:
            sykes_data.append(event_df.loc[team_number, column_name])

        return sykes_data

    def process_alliance(self, alliance_teams, list_of_previous_event_team_stats=None):
        # Statistics for the match
        tba_data = []
        scouting_data = []
        sykes_data = []

        use_no_scouting_predictor = False

        for team in alliance_teams:
            team_number = self.tba.team(team)['team_number']
            team_last_event = self.get_team_last_event(team)

            if self.predictor.header['use_tba_data']:
                team_status = self.tba.team_status(team, self.event_key)

                relevant_sort_order_stats = self.relevant_sort_order_stats

                if relevant_sort_order_stats < 0:
                    relevant_sort_order_stats = len(team_status['qual']['sort_order_info'])

                team_tba_data = team_status['qual']['ranking']['sort_orders'][:relevant_sort_order_stats]

                if not np.array(team_tba_data).any():
                    # Team hasn't played yet, so get their status from their last competition

                    team_tba_data = self.tba.team_status(team, team_last_event['key'])['qual']['ranking'][
                                        'sort_orders'][:relevant_sort_order_stats]

                tba_data.append(team_tba_data)

            if self.predictor.header['use_sykes_data']:
                event_df = pd.read_excel(self.sykes_filepath, sheet_name=team_last_event['short_name'])

                index = 0
                # Find and set the proper header of the dataframe as the position of the header is variable
                for index, row in event_df.iterrows():
                    if str(row[0])[:4] == 'team':
                        break

                # Set header and subsequent rows
                new_header = event_df.iloc[index]  # Grab the correct row for the header
                event_df = event_df[index + 1:]  # Take the data less the header row
                event_df.columns = new_header  # Set the header row as the dataframe header

                # First column titled 'team Number' is just 'team' in other year datasets, so set it to 'team Number'
                # if it is 'team'

                if event_df.columns.values[0] == 'team':
                    event_df.rename(columns={'team': 'team Number'}, inplace=True)

                event_df.set_index('team Number', inplace=True)

                sykes_data.append(self.get_team_sykes_data(event_df, team_number))

            if self.predictor.header['use_scouting_data'] and not use_no_scouting_predictor:
                if team_number not in self.current_team_dict:
                    self.current_team_dict[team_number] = []

                most_recent_cur_data = self.current_team_dict[team_number]

                num_prev_matches_needed = self.moving_average_time_period - len(most_recent_cur_data)

                if num_prev_matches_needed > 0:
                    last_event_dict = {}

                    found = False

                    for event_dict in list_of_previous_event_team_stats:
                        if team_number in event_dict:
                            last_event_dict = event_dict
                            found = True
                            break

                    if not found and not self.has_no_scouting_predictor:
                        raise RuntimeError(
                            'Team was not scouted in previous scouting spreadsheets and no fallback predictor was '
                            'provided')
                    elif not found and self.has_no_scouting_predictor:
                        use_no_scouting_predictor = True
                        continue

                    most_recent_prev_data = last_event_dict[team_number][-num_prev_matches_needed:]
                    if len(most_recent_cur_data) > 0:
                        team_most_recent_average_stats = np.average(most_recent_prev_data + most_recent_cur_data,
                                                                    axis=0)
                    else:
                        team_most_recent_average_stats = np.average(most_recent_prev_data, axis=0)
                else:
                    team_most_recent_average_stats = np.average(most_recent_cur_data[-self.moving_average_time_period:],
                                                                axis=0)

                scouting_data.append(team_most_recent_average_stats)

        if use_no_scouting_predictor:
            if self.predictor.header['use_sum']:
                tba_data = np.sum(tba_data, axis=0) if len(tba_data) > 0 else []
                sykes_data = np.sum(sykes_data, axis=0) if len(sykes_data) > 0 else []
            elif self.predictor.header['use_average']:
                tba_data = np.average(tba_data, axis=0) if len(tba_data) > 0 else []
                sykes_data = np.average(sykes_data, axis=0) if len(sykes_data) > 0 else []
            elif self.predictor.header['use_median']:
                tba_data = np.median(tba_data, axis=0) if len(tba_data) > 0 else []
                sykes_data = np.median(sykes_data, axis=0) if len(sykes_data) > 0 else []

            return np.concatenate((tba_data, sykes_data), axis=None).tolist()
        else:
            if self.predictor.header['use_sum']:
                tba_data = np.sum(tba_data, axis=0) if len(tba_data) > 0 else []
                scouting_data = np.sum(scouting_data, axis=0) if len(scouting_data) > 0 else []
                sykes_data = np.sum(sykes_data, axis=0) if len(sykes_data) > 0 else []
            elif self.predictor.header['use_average']:
                tba_data = np.average(tba_data, axis=0) if len(tba_data) > 0 else []
                scouting_data = np.average(scouting_data, axis=0) if len(scouting_data) > 0 else []
                sykes_data = np.average(sykes_data, axis=0) if len(sykes_data) > 0 else []
            elif self.predictor.header['use_median']:
                tba_data = np.median(tba_data, axis=0) if len(tba_data) > 0 else []
                scouting_data = np.median(scouting_data, axis=0) if len(scouting_data) > 0 else []
                sykes_data = np.median(sykes_data, axis=0) if len(sykes_data) > 0 else []

            return np.concatenate((tba_data, scouting_data, sykes_data), axis=None).tolist()

    def run(self):

        if self.predictor.header['use_scouting_data']:
            # Use credentials to create client and interact with Google Drive API
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.gs_creds_filepath, scope)

            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            match_scouting_sheets = service.spreadsheets()

            list_of_previous_event_team_stats = []

            for spreadsheet_id in self.previous_scouting_spreadsheet_ids:
                team_dict = {}

                for row in self.get_rows(match_scouting_sheets, spreadsheet_id):
                    team_number = int(row[0])

                    if team_number not in team_dict:
                        team_dict[team_number] = []

                    team_dict[team_number].append([float(i) for i in row[2:]])

                list_of_previous_event_team_stats.append(team_dict)

            total_num_matches = sum(m['comp_level'] == 'qm' for m in self.tba.event_matches(self.event_key))

            previous_match_num = 0
            current_match_num = 0
            previous_num_rows = 0

            # current_rows = self.get_rows(match_scouting_sheets, self.current_scouting_spreadsheet_id)
            # for current_row in current_rows:
            #     team_number = int(current_row[0])
            #     current_match_num = int(current_row[1])
            #
            #     if team_number not in self.current_team_dict:
            #         self.current_team_dict[team_number] = []
            #
            #     self.current_team_dict[team_number].append([float(i) for i in current_row[2:]])
            #
            #     if current_match_num != previous_match_num:
            #         # Print prediction for next match
            #         next_match_num = current_match_num + 1
            #
            #         if next_match_num > total_num_matches:
            #             print(self.predictor.errors)
            #             return
            #
            #         red_alliance_teams = \
            #             self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
            #                 'alliances']['red']['team_keys']
            #         blue_alliance_teams = \
            #             self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
            #                 'alliances']['blue']['team_keys']
            #
            #         red_input = self.process_alliance(red_alliance_teams, list_of_previous_event_team_stats)
            #         blue_input = self.process_alliance(blue_alliance_teams, list_of_previous_event_team_stats)
            #
            #         self.predictor.print_predicted_outcome(red_input, blue_input, next_match_num)
            #
            #     previous_match_num = current_match_num

            while True:
                current_rows = self.get_rows(match_scouting_sheets, self.current_scouting_spreadsheet_id)
                current_num_rows = len(current_rows)
                if current_num_rows != previous_num_rows:
                    last_row = current_rows[current_num_rows - 1]

                    quan_row = []

                    for i, quan_func in zip(relevant_column_indices.values(), relevant_column_names.values()):
                        val = getattr(qf, quan_func)(last_row[i])
                        if isinstance(val, (int, float, complex)):
                            val = int(round(val))

                        quan_row.append(val)

                    # Get team number and match number
                    team_number = int(quan_row[0])
                    current_match_num = int(quan_row[1])

                    # Update team stats
                    if team_number not in self.current_team_dict:
                        self.current_team_dict[team_number] = []

                    self.current_team_dict[team_number].append([float(i) for i in quan_row[2:]])

                previous_num_rows = current_num_rows

                if current_match_num != previous_match_num:
                    # Print prediction for next match
                    next_match_num = current_match_num + 1

                    if next_match_num > total_num_matches:
                        print(self.predictor)
                        return

                    red_alliance_teams = \
                        self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
                            'alliances']['red']['team_keys']
                    blue_alliance_teams = \
                        self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
                            'alliances']['blue']['team_keys']

                    red_input = self.process_alliance(red_alliance_teams, list_of_previous_event_team_stats)
                    blue_input = self.process_alliance(blue_alliance_teams, list_of_previous_event_team_stats)

                    self.predictor.print_predicted_outcome(red_input, blue_input, next_match_num)

                previous_match_num = current_match_num

                time.sleep(1.5)
        else:
            # TODO: Make real-time algorithm better

            current_match_num = 1
            previous_post_time_status = False

            while True:
                current_post_time_status = \
                    self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=current_match_num)[
                        'post_result_time'] > 0

                if current_post_time_status != previous_post_time_status:
                    next_match_num = current_match_num + 1

                    red_alliance_teams = \
                        self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
                            'alliances'][
                            'red']['team_keys']
                    blue_alliance_teams = \
                        self.tba.match(year=self.comp_year, event=self.event_key, type='qm', number=next_match_num)[
                            'alliances'][
                            'blue']['team_keys']

                    red_input = self.process_alliance(red_alliance_teams)
                    blue_input = self.process_alliance(blue_alliance_teams)

                    self.predictor.print_predicted_outcome(red_input, blue_input, next_match_num)

                    current_match_num = next_match_num
                    previous_post_time_status = False


if __name__ == '__main__':
    app = MARealTime()
