import argparse

class MARealTime:

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Analyze an event in real-time using scouting data and optional TBA data or Sykes data.')

        parser.add_argument('predictor_filepath', metavar='predictor-filepath', type=str, help='filepath to a pickled match predictor file')

if __name__ == '__main__':
    app = MARealTime()