from match_predictor import MatchPredictor

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

class MatchClassifier(MatchPredictor):

    def __init__(self, dataset_filepath, h):
        super().__init__(dataset_filepath)

        self.h = h

        self.names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
                 "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
                 "Naive Bayes", "QDA"]

        self.classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=0.025),
            SVC(gamma=2, C=1),
            GaussianProcessClassifier(1.0 * RBF(1.0)),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
            MLPClassifier(alpha=1, max_iter=1000),
            AdaBoostClassifier(),
            GaussianNB(),
            QuadraticDiscriminantAnalysis()]

    def train(self):
        pass

    def predict_scores(self, red_status, blue_status):
        pass

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cm_bright = ListedColormap(['#FF0000', '#0000FF'])
        
        for n in range(0, self.number_of_features):
            ax.scatter(self.X_train[:, 0], self.X_train[:, 8], c=self.y_train, cmap=cm_bright, edgecolors='k')
            # Plot the testing points
            ax.scatter(self.X_test[:, 0], self.X_test[:, 8], c=self.y_test, cmap=cm_bright, alpha=0.6, edgecolors='k')
            
        plt.show()

mc = MatchClassifier('datasets/DaltonDeepSpaceClassification.npz', 0.02)
mc.visualize()
