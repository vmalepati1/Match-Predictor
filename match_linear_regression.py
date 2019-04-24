from sklearn.linear_model import LinearRegression
from match_predictor import MatchPredictor

class LinearRegression(MatchPredictor):
    def __init__(dataset_filepath):
        x = np.load(dataset_filepath)['x']
        Y = np.load(dataset_filepath)['y']

        
        
