import numpy as np
from keras.layers import Dense
from keras.models import Sequential

from match_predictor import MatchPredictor

class MatchDeepLearning(MatchPredictor):

    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

        if self.header['is_classification']:
            raise ValueError('Your dataset must be compiled with the classification flag off to use the deep learning predictor.')

        self.model = Sequential()

    def train(self):
        # Add layers to model
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

    def print_predicted_outcome(self, red_status, blue_status, match_num):
        red_score_input = np.reshape(red_status + blue_status, (1, self.number_of_features))
        blue_score_input = np.reshape(blue_status + red_status, (1, self.number_of_features))

        print('Match {}: red score {} and blue score {}'.format(match_num, self.model.predict(red_score_input), self.model.predict(blue_score_input)))

dl = MatchDeepLearning('datasets/DaltonDeepSpace.npz')
#dl.visualize_input_data()
dl.train()
dl.save('pickled_predictors/DaltonDeepSpaceDL.obj')