import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Abstract class for match scores prediction
class MatchPredictor:

    def __init__(self, dataset_filepath):
        X = np.load(dataset_filepath)['x']
        y = np.load(dataset_filepath)['y']

        self.number_of_features = len(X[0])

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, random_state=0)

        self.scaler = MinMaxScaler()
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)

    # Trains the model
    def train(self):
        pass

    # Returns red score and blue score based on the status of the teams from previous matches
    def predict_scores(self, red_status, blue_status):
        pass

    # Visualize the model
    def visualize():
        pass
