from match_predictor import MatchPredictor

import numpy as np
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

    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

        if not self.header['is_classification']:
            raise ValueError('Your dataset must be compiled with the classification flag to use the match classifier.')

        self.classifiers = {
            # Classifier obj, score
            KNeighborsClassifier(3): 0.0,
            SVC(kernel="linear", C=0.025): 0.0,
            SVC(gamma=2, C=1): 0.0,
            GaussianProcessClassifier(1.0 * RBF(1.0)): 0.0,
            DecisionTreeClassifier(max_depth=5): 0.0,
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1): 0.0,
            MLPClassifier(alpha=1, max_iter=1000): 0.0,
            AdaBoostClassifier(): 0.0,
            GaussianNB(): 0.0,
            QuadraticDiscriminantAnalysis(): 0.0
        }

    def train(self):
        for clf in self.classifiers:
            try:
                clf.fit(self.X_train, self.y_train)
            except ValueError:
                # Most likely there were not enough ties to learn from
                tie_train_indices = [i for i in range(len(self.y_train)) if self.y_train[i] == 1]
                tie_test_indices = [i for i in range(len(self.y_test)) if self.y_test[i] == 1]

                for i in tie_train_indices:
                    self.X_train = np.delete(self.X_train, i, 0)
                    self.y_train = np.delete(self.y_train, i, 0)

                for i in tie_test_indices:
                    self.X_test = np.delete(self.X_test, i, 0)
                    self.y_test = np.delete(self.y_test, i, 0)

                clf.fit(self.X_train, self.y_train)

            self.classifiers[clf] = clf.score(self.X_test, self.y_test)

        self.best_clf = max(self.classifiers, key=self.classifiers.get)
        print('Best classifier score: %f' % self.classifiers[self.best_clf])

    def print_predicted_outcome(self, red_status, blue_status, match_num):
        outcome_classification = self.best_clf.predict(red_status + blue_status)

        if outcome_classification == 1:
            print('Match {}: tie'.format(match_num))
        elif outcome_classification == 2:
            print('Match {}: red win'.format(match_num))
        elif outcome_classification == 3:
            print('Match {}: blue win'.format(match_num))
        else:
            print('Match {}: unknown classification id {}'.format(match_num, outcome_classification))


cl = MatchClassifier('datasets/DaltonDeepSpaceClassification.npz')
#mc.visualize_input_data()
cl.train()
cl.save('pickled_predictors/DaltonDeepSpaceCL.obj')