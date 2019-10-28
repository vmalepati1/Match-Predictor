import numpy as np
from sklearn.linear_model import LinearRegression

from match_predictor import MatchPredictor


class MatchLinearRegression(MatchPredictor):

    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

        self.model = LinearRegression()

    def train(self):
        self.model.fit(self.X_train, self.y_train)
        print('Accuracy: ' + str(self.model.score(self.X_test, self.y_test)))

    def print_predicted_outcome(self, red_status, blue_status, match_num):
        red_score_input = np.reshape(red_status + blue_status, (1, self.number_of_features))
        blue_score_input = np.reshape(blue_status + red_status, (1, self.number_of_features))

        print('Match {}: red score {} and blue score {}'.format(match_num, self.model.predict(
            self.scaler.transform(red_score_input)), self.model.predict(self.scaler.transform(blue_score_input))))


if __name__ == '__main__':
    lr = MatchLinearRegression('datasets/ColumbusDeepSpace.npz')
    # lr.visualize_input_data()
    lr.train()
    lr.save('pickled_predictors/ColumbusDeepSpaceLR.obj')
