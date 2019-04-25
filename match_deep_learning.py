from keras.models import Sequential
from keras.layers import Dense
from match_predictor import MatchPredictor
import numpy as np

class MatchDeepLearning(MatchPredictor):

    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)
        self.number_of_features = len(self.X[0])

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
        self.model.compile(loss='mse', optimizer='adam')

        # Fit the model
        self.model.fit(self.X, self.y, epochs=1000)
        
    def predict_scores(self, red_status, blue_status):
        red_score_input = np.reshape(red_status + blue_status, (1, 30))
        blue_score_input = np.reshape(blue_status + red_status, (1, 30))
        
        return self.model.predict(red_score_input), self.model.predict(blue_score_input)

dl = MatchDeepLearning('example_dataset/StrongHold.npz')

dl.train()

red, blue = dl.predict_scores([ 34, 268, 195, 326, 510,  38, 258, 155, 410, 560,  16, 212, 100, 123,
 515,  ],
 [21, 210, 135, 181, 515,  29, 204, 130, 195, 530,  19, 234, 120,
 175, 520,])

print(red)
print(blue)
