from ping_tba_api import *
import numpy as np
import argparse
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

class DatasetFactory:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description = 'Create a dataset for training models using a combination of data from \
                            any of the following: TBA API, Sykes scouting database, and team scouting data.')
        
        parser.add_argument('out_filepath', metavar='out-filepath', type=str, help='filepath to an uncreated or already existing dataset file with extension .NPZ')
        parser.add_argument('tba_api_key', metavar='tba-api-key', type=str, help='your The Blue Alliance key that you can create in your TBA Account Dashboard')
        parser.add_argument('year', type=int, help='the year of the First Robotics Competition game')
        parser.add_argument('-t', '--use-tba-data', action='store_true', default=True, help='flag indicating whether to use TBA sort order data in the dataset (on by default)')
        parser.add_argument('-syf', '--sykes-filepath', type=str, help='filepath to a Sykes scouting database Excel file with extension .xlsx')
        parser.add_argument('-syc', '--sykes-columns', nargs='+', type=str, default=['winning Margin', 'win'],
                            help='names of the columns in the Sykes Excel sheet to use as features in the dataset')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-b', '--event-blacklist', nargs='+', type=str, help='list of official names of events on TBA record to exclude')
        group.add_argument('-w', '--event-whitelist', nargs='+', type=str, help='list of official names of events on TBA record to use only')

        args = parser.parse_args()

        self.out_filepath = args.out_filepath
        self.tba_api_key = args.tba_api_key
        self.year = args.year
        self.use_tba_data = args.use_tba_data
        self.use_sykes_data = False
        self.use_blacklist = False
        self.use_whitelist = False

        if args.sykes_filepath:
            self.use_sykes_data = True
            self.sykes_filepath = args.sykes_filepath
            self.sykes_columns = args.sykes_columns

        if args.event_blacklist:
            self.use_blacklist = True
            self.blacklist = args.event_blacklist
            
        if args.event_whitelist:
            self.use_whitelist = True
            self.whitelist = args.event_whitelist

        self.create_dataset()

    def create_dataset(self):
        # Dataset return lists
        x = []
        y = []

        # Get all events that happened during the specified year
        events = tba_get_response(self.tba_api_key, '/events/' + str(self.year))

        # Number of actual values within sort_orders that excludes any placeholder 0s at the end
        relevant_sort_order_statistics = -1

        # Load navigation page data frame beforehand for easily accessing specific event sheets
        if self.use_sykes_data:
            navigation_df = pd.read_excel(self.sykes_filepath, sheet_name='navigation', header=2)
            navigation_df.set_index('Event name', inplace=True)

        for event in events:
            event_key = event['key']
            event_name = event['name']

            # Skip over events in blacklist
            if self.use_blacklist and event_name in self.blacklist:
                continue
            # Skip over events not in whitelist
            elif self.use_whitelist and event_name not in self.whitelist:
                continue

            # Read in data frame
            if self.use_sykes_data:
                event_sheet_name = navigation_df.loc[event_name, 'Short Name']
                event_df = pd.read_excel(self.sykes_filepath, sheet_name=event_sheet_name, header=3)
                event_df.set_index('team Number', inplace=True)
                print("Column headings:")
                print(event_df.columns)
                
            for match in tba_get_response(self.tba_api_key, '/event/' + event_key + '/matches'):
                # List of team keys
                red_team_keys = match['alliances']['red']['team_keys']
                blue_team_keys = match['alliances']['blue']['team_keys']

                # Red statistics for the match
                red_input = []

                # Blue statistics for the match
                blue_input = []

                # If teams were absent or something else, skip this match
                #try:
                # Team status is nothing but the statistics for the match for the team (ex. how many hatches or cargo placed in Deep Space)
                for team_key in red_team_keys:
                    team_status = tba_get_response(self.tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    team_number = tba_get_response(self.tba_api_key, '/team/' + team_key)['team_number']

                    if self.use_tba_data:
                        # Number of features has not been set yet
                        if relevant_sort_order_statistics < 0:
                            relevant_sort_order_statistics = len(team_status['qual']['sort_order_info'])

                        red_input.append(team_status['qual']['ranking']['sort_orders'][:relevant_sort_order_statistics])

                    sykes_input = []
                                          
                    if self.use_sykes_data:
                        for column_name in self.sykes_columns:
                            sykes_input.append(event_df.loc[team_number, column_name])

                    red_input.append(sykes_input)

                for team_key in blue_team_keys:
                    team_status = tba_get_response(self.tba_api_key, '/team/' + team_key + '/event/' + event_key + '/status')
                    blue_input.append(team_status['qual']['ranking']['sort_orders'][:relevant_sort_order_statistics])

                # Flatten red input and blue input arrays to contain all three team statistics
            
                red_input = [item for sublist in red_input for item in sublist]
                blue_input = [item for sublist in blue_input for item in sublist]
                #except:
                    #continue

                red_output = match['alliances']['red']['score']
                blue_output = match['alliances']['blue']['score']

                # Input to training contains the statistics of the corresponding alliance color statistics
                # to output followed by the opposing alliance statistics
                x.append(red_input + blue_input)
                y.append(red_output)
                
                x.append(blue_input + red_input)
                y.append(blue_output)

                break
            break

        # Save our dataset to the specified file path
        np.savez(self.out_filepath, x=np.array(x), y=np.array(y))
    
if __name__ == '__main__':
    app = DatasetFactory()
