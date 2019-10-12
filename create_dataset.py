import argparse

import numpy as np
import pandas as pd

from ping_tba_api import *


class DatasetFactory:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Create a dataset for training models using a combination of data from \
                            any of the following: TBA API, Sykes scouting database, and team scouting data.')

        parser.add_argument('out_filepath', metavar='out-filepath', type=str,
                            help='filepath to an uncreated or already existing dataset file with extension .NPZ')
        parser.add_argument('tba_api_key', metavar='tba-api-key', type=str,
                            help='your The Blue Alliance key that you can create in your TBA Account Dashboard')
        parser.add_argument('year', type=int, help='the year of the First Robotics Competition game')
        parser.add_argument('-t', '--use-tba-data', action='store_true',
                            help='flag indicating whether to use TBA sort order data in the dataset')
        parser.add_argument('-syf', '--sykes-filepath', type=str,
                            help='filepath to a Sykes scouting database Excel file with extension .xlsx')
        parser.add_argument('-syc', '--sykes-columns', nargs='+', type=str, default=['winning Margin', 'win'],
                            help='names of the columns in the Sykes Excel sheet to use as features in the dataset')
        parser.add_argument('-c', '--classification', action='store_true',
                            help='flag indicating whether the dataset is for winner classification instead of actual score prediction')
        list_group = parser.add_mutually_exclusive_group()
        list_group.add_argument('-b', '--event-blacklist', nargs='+', type=str,
                                help='list of official names of events on TBA record to exclude')
        list_group.add_argument('-w', '--event-whitelist', nargs='+', type=str,
                                help='list of official names of events on TBA record to use only')
        measures_group = parser.add_mutually_exclusive_group()
        measures_group.add_argument('-s', '--sum', action='store_true',
                                    help="take the sum of each team's statistics for the entire alliance to reduce training features")
        measures_group.add_argument('-a', '--average', action='store_true',
                                    help="take the average of each team's statistics for the entire alliance to reduce training features")
        measures_group.add_argument('-m', '--median', action='store_true',
                                    help="take the median of each team's statistics for the entire alliance to reduce training features")

        args = parser.parse_args()

        self.out_filepath = args.out_filepath
        self.tba_api_key = args.tba_api_key
        self.year = args.year
        self.use_tba_data = args.use_tba_data
        self.use_sykes_data = False
        self.is_classification = args.classification

        if args.sykes_filepath:
            self.use_sykes_data = True
            self.sykes_filepath = args.sykes_filepath
            self.sykes_columns = args.sykes_columns

        self.blacklist = args.event_blacklist
        self.whitelist = args.event_whitelist

        self.use_sum = args.sum
        self.use_average = args.average
        self.use_median = args.median

        self.create_dataset()

    def create_dataset(self):
        # Dataset return lists
        x = []
        y = []

        # Get all events that happened during the specified year
        events = tba_get_response(self.tba_api_key, '/events/' + str(self.year))

        # Number of actual values within sort_orders that excludes any placeholder 0s at the end
        relevant_sort_order_statistics = -1

        for event in events:
            event_key = event['key']
            event_name = event['name']
            event_short_name = event['short_name']

            # Skip over events in blacklist
            if self.blacklist and event_name in self.blacklist:
                continue
            # Skip over events not in whitelist
            elif self.whitelist and event_name not in self.whitelist:
                continue

            # Read in data frame
            if self.use_sykes_data:
                event_df = pd.read_excel(self.sykes_filepath, sheet_name=event_short_name)

                # Find and set the proper header of the dataframe as the position of the header is variable
                for index, row in event_df.iterrows():
                    if str(row[0])[:4] == 'team':
                        break

                # Set header and subsequent rows
                new_header = event_df.iloc[index]  # Grab the correct row for the header
                event_df = event_df[index + 1:]  # Take the data less the header row
                event_df.columns = new_header  # Set the header row as the dataframe header

                # First column titled 'team Number' is just 'team' in other year datasets, so set it to 'team Number' if it is 'team'

                if event_df.columns.values[0] == 'team':
                    event_df.rename(columns={'team': 'team Number'}, inplace=True)

                event_df.set_index('team Number', inplace=True)

            for match in tba_get_response(self.tba_api_key, '/event/' + event_key + '/matches'):
                match_number = match['match_number']

                # List of team keys
                red_team_keys = match['alliances']['red']['team_keys']
                blue_team_keys = match['alliances']['blue']['team_keys']

                # Red statistics for the match
                red_tba_data = []
                red_sykes_data = []

                # Blue statistics for the match
                blue_tba_data = []
                blue_sykes_data = []

                # If teams were absent or something else, skip this match
                try:
                    # Team status is nothing but the statistics for the match for the team (ex. how many hatches or cargo placed in Deep Space)
                    for team_key in red_team_keys:
                        team_status = tba_get_response(self.tba_api_key,
                                                       '/team/' + team_key + '/event/' + event_key + '/status')
                        team_number = tba_get_response(self.tba_api_key, '/team/' + team_key)['team_number']

                        if self.use_tba_data:
                            # Number of features has not been set yet
                            if relevant_sort_order_statistics < 0:
                                relevant_sort_order_statistics = len(team_status['qual']['sort_order_info'])

                            red_tba_data.append(
                                team_status['qual']['ranking']['sort_orders'][:relevant_sort_order_statistics])

                        if self.use_sykes_data:
                            red_sykes_data.append(self.get_team_sykes_data(event_df, team_number))

                    for team_key in blue_team_keys:
                        team_status = tba_get_response(self.tba_api_key,
                                                       '/team/' + team_key + '/event/' + event_key + '/status')
                        team_number = tba_get_response(self.tba_api_key, '/team/' + team_key)['team_number']

                        if self.use_tba_data:
                            blue_tba_data.append(
                                team_status['qual']['ranking']['sort_orders'][:relevant_sort_order_statistics])

                        if self.use_sykes_data:
                            blue_sykes_data.append(self.get_team_sykes_data(event_df, team_number))

                    # Perform the indicated statistics operation (sum, average, or median) to combine each team's statistics into one alliance input
                    if self.use_sum:
                        red_tba_data = np.sum(red_tba_data, axis=0) if len(red_tba_data) > 0 else []
                        red_sykes_data = np.sum(red_sykes_data, axis=0) if len(red_sykes_data) > 0 else []
                        blue_tba_data = np.sum(blue_tba_data, axis=0) if len(blue_tba_data) > 0 else []
                        blue_sykes_data = np.sum(blue_sykes_data, axis=0) if len(blue_sykes_data) > 0 else []
                    elif self.use_average:
                        red_tba_data = np.average(red_tba_data, axis=0) if len(red_tba_data) > 0 else []
                        red_sykes_data = np.average(red_sykes_data, axis=0) if len(red_sykes_data) > 0 else []
                        blue_tba_data = np.average(blue_tba_data, axis=0) if len(blue_tba_data) > 0 else []
                        blue_sykes_data = np.average(blue_sykes_data, axis=0) if len(blue_sykes_data) > 0 else []
                    elif self.use_median:
                        red_tba_data = np.median(red_tba_data, axis=0) if len(red_tba_data) > 0 else []
                        red_sykes_data = np.median(red_sykes_data, axis=0) if len(red_sykes_data) > 0 else []
                        blue_tba_data = np.median(blue_tba_data, axis=0) if len(blue_tba_data) > 0 else []
                        blue_sykes_data = np.median(blue_sykes_data, axis=0) if len(blue_sykes_data) > 0 else []

                    # Flatten red input and blue input arrays to contain all alliance information
                    red_input = np.concatenate((red_tba_data, red_sykes_data), axis=None).tolist()
                    blue_input = np.concatenate((blue_tba_data, blue_sykes_data), axis=None).tolist()
                    print(red_input)
                except:
                    print('Error at event %s match number %d! Skipping...' % (event_short_name, match_number))
                    continue

                red_score = match['alliances']['red']['score']
                blue_score = match['alliances']['blue']['score']

                if self.is_classification:
                    # Classes: 0 = tied, 1 = red won, 2 = blue won
                    match_classification = 0

                    if red_score > blue_score:
                        match_classification = 1
                    elif blue_score > red_score:
                        match_classification = 2

                    x.append(red_input + blue_input)
                    y.append(match_classification)
                else:
                    # Input to training contains the statistics of the corresponding alliance color statistics
                    # to output followed by the opposing alliance statistics
                    x.append(red_input + blue_input)
                    y.append(red_score)

                    x.append(blue_input + red_input)
                    y.append(blue_score)

        # Save our dataset to the specified file path
        np.savez(self.out_filepath, header=np.array({'is_classification': self.is_classification}), x=np.array(x),
                 y=np.array(y))

    def get_team_sykes_data(self, event_df: object, team_number: int):
        sykes_data = []

        for column_name in self.sykes_columns:
            sykes_data.append(event_df.loc[team_number, column_name])

        return sykes_data


if __name__ == '__main__':
    app = DatasetFactory()
