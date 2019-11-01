import argparse
import tbapy
import numpy as np
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from scouting_data.cleaning.col_utils import *
import operator

class AllianceSelectionUtil:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Analyze the performance of a robot using a combination of TBA and/or scouting data.')

        parser.add_argument('tba_api_key', metavar='tba-api-key', type=str,
                            help='your The Blue Alliance key that you can create in your TBA Account Dashboard')
        parser.add_argument('event_key', metavar='event-key', type=str, help='TBA event key of the competition')
        parser.add_argument('-tsm', '--tba-sorting-method', type=str, help="sorting method for ranking teams; can be "
                                                                           "'opr,' 'dpr,' 'ccwm,' or 'so' (sort "
                                                                           "orders). Note for sort orders, "
                                                                           "you may specify which values you would "
                                                                           "like to use")
        parser.add_argument('-soi', '--sort-order-indices', nargs='+', type=int, help='indices of sort order data to use (starting from 0)')
        parser.add_argument('-gsc', '--google-sheets-creds-filepath', type=str,
                            help='filepath to a credentials JSON file created by Google for your service account')
        parser.add_argument('-csi', '--current-scouting-spreadsheet-id', type=str,
                            help='the key of the real-time updating scouting spreadsheet shared with your service '
                                 'account')
        parser.add_argument('-lnm', '--last-n-matches', type=int, help="how many last matches of a team to average; if this parameter is not set, all matches will be averaged")
        parser.add_argument('-scn', '--scouting-column-names', nargs='+', type=str, help="column names within the scouting spreadsheet to average for a team's selection ranking")
        parser.add_argument('-stn', '--self-team-number', type=int, default=2974, help="your own team number to ignore in the rankings")

        args = parser.parse_args()

        self.tba = tbapy.TBA(args.tba_api_key)
        self.event_key = args.event_key
        self.self_team_number = args.self_team_number

        self.using_tba_data = False
        self.using_scouting_data = False

        # Validate parameters
        if args.tba_sorting_method or args.sort_order_indices:
            if not args.tba_sorting_method or not args.sort_order_indices:
                raise ValueError('Parameters -tsm and -sov must be set together to use TBA data')

            self.using_tba_data = True
            self.tba_sorting_method = args.tba_sorting_method.lower()
            self.sort_order_indices = args.sort_order_indices

            if self.tba_sorting_method != 'opr' and self.tba_sorting_method != 'dpr' and self.tba_sorting_method != 'ccwm' and self.tba_sorting_method != 'so':
                raise ValueError("The parameter -tsm must be either 'opr,' 'dpr,' 'ccwm,' or 'so' (sort orders)")

        if args.google_sheets_creds_filepath or args.current_scouting_spreadsheet_id or args.scouting_column_names:
            if not args.google_sheets_creds_filepath or not args.current_scouting_spreadsheet_id or not args.scouting_column_names:
                raise ValueError('All parameters within the scouting info group must be set together')

            self.using_scouting_data = True
            self.gs_creds_filepath = args.google_sheets_creds_filepath
            self.current_scouting_spreadsheet_id = args.current_scouting_spreadsheet_id
            self.scouting_column_names = args.scouting_column_names
            self.last_n_matches = -1

            if args.last_n_matches:
                self.last_n_matches = args.last_n_matches

            self.standings = {}
            self.populate_standings()

        if not self.using_tba_data and not self.using_scouting_data:
            raise ValueError('You must be specifying parameters for either tba data or scouting data or both')

        self.team_rankings_dict = {}
        self.print_rankings()

    def get_rows(self, sheet, spreadsheet_id):
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range='Sheet1!A2:' + num_to_letter(len(relevant_column_names))).execute()
        values = result.get('values', [])
        return values

    def populate_standings(self):
        # Use credentials to create client and interact with Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.gs_creds_filepath, scope)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        rows = self.get_rows(sheet, self.current_scouting_spreadsheet_id)

        relevant_column_names_list = list(relevant_column_names.keys())

        for row in rows:
            team_number = int(row[0])

            if team_number not in self.standings:
                self.standings[team_number] = []

            team_status = []

            for c in self.scouting_column_names:
                team_status.append(float(row[relevant_column_names_list.index(c)]))

            self.standings[team_number].append(team_status)

    def print_rankings(self):
        for team in self.tba.event_teams(self.event_key):
            total_ranking = 0.0

            team_key = team['key']
            team_name = team['nickname']
            team_number = team['team_number']

            if team_number == self.self_team_number:
                continue

            team_name_and_number = '{:>5} | {:>95}'.format(str(team_number), team_name)

            if self.using_tba_data:
                if self.tba_sorting_method == 'so':
                    status = self.tba.team_status(team_key, self.event_key)

                    indexed_status = [status[i] for i in self.sort_order_indices]

                    total_ranking += np.sum(indexed_status)
                else:
                    total_ranking += self.tba.event_oprs(self.event_key)[self.tba_sorting_method + 's'][team_key]

            if self.using_scouting_data:
                team_standing = self.standings[team_number]

                if self.last_n_matches:
                    total_ranking += np.sum(np.average(team_standing[-self.last_n_matches:], axis=0))
                else:
                    total_ranking += np.sum(np.average(team_standing, axis=0))

            self.team_rankings_dict[team_name_and_number] = total_ranking

        sorted_teams_by_rank = sorted(self.team_rankings_dict.items(), key=operator.itemgetter(1), reverse=True)

        for rank, (team_identifier, score) in enumerate(sorted_teams_by_rank):
            print('{:>3}. {:>100}'.format(rank + 1, team_identifier))

if __name__ == '__main__':
    app = AllianceSelectionUtil()