import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from itertools import combinations
import pickle

# Abstract class for match scores prediction
class MatchPredictor:

    def __init__(self, dataset_filepath, h=0.02):
        self.h = h
        dataset = np.load(dataset_filepath, allow_pickle=True)
        self.X = dataset['x']
        self.y = dataset['y']
        self.header = dataset['header'][()]

        self.number_of_features = len(self.X[0])

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, random_state=0)

        self.scaler = MinMaxScaler()
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)

    # Trains the model
    def train(self):
        pass

    # Prints the predicted outcome (classification or score) given the status of each alliance and the match number
    def print_predicted_outcome(self, red_status, blue_status, match_num):
        pass

    # Visualize the input training and testing data
    def visualize_input_data(self):
        cm_bright = ListedColormap(['#FF0000', '#0000FF'])

        dataset_combs = list(combinations(range(self.number_of_features // 2), 2))

        figure = plt.figure(figsize=(27, 9))

        i = 1
        for first_ix, sec_ix in dataset_combs:
            ax = plt.subplot(1, len(list(dataset_combs)), i)
            # Plot the training points
            ax.scatter(self.X_train[:, first_ix], self.X_train[:, sec_ix], c=self.y_train, cmap=cm_bright, edgecolors='k')
            # Plot the testing points
            ax.scatter(self.X_test[:, first_ix], self.X_test[:, sec_ix], c=self.y_test, cmap=cm_bright, alpha=0.6, edgecolors='k')
            ax.set_title("{} vs {}".format(first_ix, sec_ix))
            ax.set_xticks(())
            ax.set_yticks(())
            i += 1

        plt.tight_layout()
        plt.show()

    def save(self, filepath):
        filehandler = open(filepath, 'wb')
        pickle.dump(self, filehandler)