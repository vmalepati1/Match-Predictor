from sklearn.linear_model import LinearRegression
from match_predictor import MatchPredictor
import numpy as np
import matplotlib.pyplot as plt

class MatchLinearRegression(MatchPredictor):
    
    def __init__(self, dataset_filepath):
        super().__init__(dataset_filepath)

    def train(self):
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)

    def predict_scores(self, red_status, blue_status):
        red_score_input = []
        red_score_input.append(red_status + blue_status)
        
        blue_score_input = []
        blue_score_input.append(blue_status + red_status)

        return self.model.predict(red_score_input), self.model.predict(blue_score_input)

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        number_of_features = len(self.X[0])

        for n in range(0, number_of_features):
            scatter_x = [i[n] for i in self.X]
            scatter_y = self.y

            ax.scatter(scatter_x, scatter_y)

        fig.show()
    
lr = MatchLinearRegression('example_dataset/StrongHold.npz')

lr.train()
lr.visualize()

red, blue = lr.predict_scores([ 34, 268, 195, 326, 510,  38, 258, 155, 410, 560,  16, 212, 100, 123,
 515,  ],
 [21, 210, 135, 181, 515,  29, 204, 130, 195, 530,  19, 234, 120,
 175, 520,])

print(red)
print(blue)
