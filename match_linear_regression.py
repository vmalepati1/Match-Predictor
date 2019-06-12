from sklearn.linear_model import LinearRegression
from match_predictor import MatchPredictor
from scrape_alliance_data import *
import numpy as np
import matplotlib.pyplot as plt
import sys

class MatchLinearRegression(MatchPredictor):
    
    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

    def train(self):
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)
        print('Accuracy: ' + str(self.model.score(self.X, self.y)))

    def predict_scores(self, red_status, blue_status):
        red_score_input = np.reshape(red_status + blue_status, (1, self.number_of_features))
        blue_score_input = np.reshape(blue_status + red_status, (1, self.number_of_features))

        return self.model.predict(red_score_input), self.model.predict(blue_score_input)

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for n in range(0, self.number_of_features):
            scatter_x = [i[n] for i in self.X]
            scatter_y = self.y

            ax.set_ylabel('Game Points')
            ax.scatter(scatter_x, scatter_y)

        plt.show()
        
if sys.argv[1].lower() == 'usage':
    print('Usage: python match_linear_regression.py dataset_filepath tba_api_key year event_name current_match match_type')
    exit()

lr = MatchLinearRegression(dataset_filepath=sys.argv[1])

lr.train()
lr.visualize()

red_input, blue_input = scrape_alliance_data(tba_api_key=sys.argv[2],
                                             year=int(sys.argv[3]),
                                             event_name=sys.argv[4],
                                             current_match=int(sys.argv[5]),
                                             match_type=sys.argv[6])

red_score, blue_score = lr.predict_scores(red_input, blue_input)

print('Red score: ' + str(red_score))
print('Blue score: ' + str(blue_score))
