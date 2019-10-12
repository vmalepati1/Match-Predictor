import argparse

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

import scouting_data.cleaning.quantifier_funcs as qf
from scouting_data.cleaning.col_utils import *


class WaltonDeepSpaceCleaner:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Quantify and prepare Walton's Deep Space match and pit scouting data and write to an output training spreadsheet.")
        parser.add_argument('creds_json_filepath', metavar='creds-json-filepath', type=str,
                            help='filepath to a credentials JSON file created by Google for your service account')
        parser.add_argument('match_scouting_spreadsheet_name', metavar='match-scouting-spreadsheet-name', type=str,
                            help='the name of the match scouting spreadsheet shared with your service account')
        parser.add_argument('event_short_name', metavar='event-short-name', type=str,
                            help='the short name for the event of the scouting data')
        parser.add_argument('email', type=str, help='the email to which the output training data will be shared')
        parser.add_argument('-mnc', '--match-number-column-name', type=str,
                            help='name of the column containing the match numbers (only specify this if your data is not ordered in ascending match number order)')

        args = parser.parse_args()

        self.creds_json_filepath = args.creds_json_filepath
        self.match_scouting_spreadsheet_name = args.match_scouting_spreadsheet_name
        self.event_short_name = args.event_short_name
        self.match_number_column_name = args.match_number_column_name
        self.email = args.email

        self.clean_and_resave_data()

    def clean_and_resave_data(self):
        # Use credentials to create client and interact with Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_json_filepath, scope)
        client = gspread.authorize(creds)

        # Open the match scouting sheet
        match_scouting_sheet = client.open(self.match_scouting_spreadsheet_name).get_worksheet(0)

        # Convert gspread spreadsheet to a dataframe for easier manipulation
        scouting_data_df = pd.DataFrame(match_scouting_sheet.get_all_values()[1:],
                                        columns=match_scouting_sheet.get_all_values()[0])

        if self.match_number_column_name:
            scouting_data_df[self.match_number_column_name] = scouting_data_df[self.match_number_column_name].astype(
                int)
            scouting_data_df.sort_values(self.match_number_column_name, inplace=True)

        quantified_spreadsheet = client.create(self.event_short_name + ' Training Data')
        quantified_worksheet = quantified_spreadsheet.sheet1

        # Add row header
        for column_num, column_name in enumerate(relevant_column_names.keys()):
            quantified_worksheet.update_cell(1, column_num + 1, column_name)

        # Add quantified data
        print('Adding quantified data')
        cell_list = quantified_worksheet.range(
            'A2:' + num_to_letter(len(relevant_column_names)) + str(scouting_data_df.shape[0] + 1))

        column_names = list(relevant_column_names.keys())

        for cell in cell_list:
            column_name = column_names[cell.col - 1]
            unconverted_val = scouting_data_df.loc[scouting_data_df.index[cell.row - 2], column_name]
            val = getattr(qf, relevant_column_names[column_name])(unconverted_val)
            if isinstance(val, (int, float, complex)):
                val = int(round(val))

            cell.value = val

        quantified_worksheet.update_cells(cell_list)
        quantified_spreadsheet.share(self.email, perm_type='user', role='writer')


if __name__ == '__main__':
    app = WaltonDeepSpaceCleaner()
