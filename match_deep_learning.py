from keras.models import Sequential
from keras.layers import Dense
from match_predictor import MatchPredictor
from scrape_alliance_data import *
import numpy as np
import sys

class MatchDeepLearning(MatchPredictor):

    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

    def train(self):
        # Add layers to model
        self.model = Sequential()

        # Reduces input by half for output
        self.model.add(Dense(self.number_of_features // 2, input_dim=self.number_of_features, activation='relu'))
        # Reduces input by half for output
        self.model.add(Dense(self.number_of_features // 4, activation='relu'))
        # Outputs one unit for score
        self.model.add(Dense(1, activation='linear'))

        # Use Adam optimization
        self.model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_squared_error'])

        # Fit the model
        self.model.fit(self.X, self.y, epochs=5000, verbose=0)

        print('Mean squared error: ' + str(self.model.evaluate(self.X, self.y)[1]))
        
    def predict_scores(self, red_status, blue_status):
        red_score_input = np.reshape(red_status + blue_status, (1, self.number_of_features))
        blue_score_input = np.reshape(blue_status + red_status, (1, self.number_of_features))
        
        return self.model.predict(red_score_input), self.model.predict(blue_score_input)

    def visualize(self):
        # TODO: display the layers of the model
        return

if sys.argv[1].lower() == 'usage':
    print('Usage: python match_deep_learning.py dataset_filepath tba_api_key year event_name current_match match_type')
    exit()
    
dl = MatchDeepLearning(dataset_filepath=sys.argv[1])

dl.train()
dl.visualize()

red_input, blue_input = scrape_alliance_data(tba_api_key=sys.argv[2],
                                             year=int(sys.argv[3]),
                                             event_name=sys.argv[4],
                                             current_match=int(sys.argv[5]),
                                             match_type=sys.argv[6])


red_score, blue_score = dl.predict_scores(red_input, blue_input)

print('Red score: ' + str(red_score))
print('Blue score: ' + str(blue_score))
