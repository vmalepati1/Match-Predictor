import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from itertools import combinations

# Abstract class for match scores prediction
class MatchPredictor:

    def __init__(self, dataset_filepath):
        self.X = np.load(dataset_filepath)['x']
        self.y = np.load(dataset_filepath)['y']

        self.number_of_features = len(self.X[0])

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, random_state=0)

        self.scaler = MinMaxScaler()
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)

    # Trains the model
    def train(self):
        pass

    # Returns red score and blue score based on the status of the teams from previous matches
    def predict_scores(self, red_status, blue_status):
        pass

    # Visualize the input training and testing data
    def visualize_input_data(self):
        cm_bright = ListedColormap(['#FF0000', '#0000FF'])

        dataset_combs = combinations(range(self.number_of_features // 2), 2)

        figure = plt.figure(figsize=(27, 9))

        i = 1
        print('test')
        for first_ix, sec_ix in dataset_combs:
            print('hello')
            ax = plt.subplot(1, len(list(dataset_combs)), i)
            ax.scatter(self.X_train[:, first_ix], self.X_train[:, sec_ix], c=self.y_train, cmap=cm_bright, edgecolors='k')
            # Plot the testing points
            ax.scatter(self.X_test[:, first_ix], self.X_test[:, sec_ix], c=self.y_test, cmap=cm_bright, alpha=0.6, edgecolors='k')
            i += 1

        plt.tight_layout()
        plt.show()

    # Visualize the model
    def visualize_model(self):
        pass
