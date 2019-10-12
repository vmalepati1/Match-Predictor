import numpy as np


# Abstract class for match scores prediction
class MatchPredictor:

    def __init__(self, dataset_filepath):
        self.X = np.load(dataset_filepath)['x']
        self.y = np.load(dataset_filepath)['y']
        self.number_of_features = len(self.X[0])

    # Trains the model
    def train(self):
        pass

    # Returns red score and blue score based on the status of the teams from previous matches
    def predict_scores(self, red_status, blue_status):
        pass

    # Visualize the model
    def visualize():
        pass
