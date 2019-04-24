from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

# Abstract class for match scores prediction
class MatchPredictor:

    # Trains the model
    def train():
        pass

    # Returns red score and blue score based on the status of the teams from previous matches
    def predict_scores(red_status, blue_status):
        pass
