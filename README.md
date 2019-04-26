# Match-Predictor
Prediction of FRC matches using TBA API and machine learning.

## Getting Started
All python source files are command-line based and will need to be run from the command line/terminal (ex. on Windows: `python create_dataset.py [arguments]`).
First, you will need to create a dataset for the year's game by running `create_dataset.py` with the following usage:
`python create_dataset.py out_filepath tba_api_key year`
where out_filepath is a file path to an uncreated or already existing dataset file (with format .NPZ), tba_api_key is a valid The Blue Alliance key that you can create in your TBA Account Dashboard: <https://www.thebluealliance.com/account>.

Then, you can start predicting matches by using (currently) either the `match_linear_regression` or `match_deep_learning` predictors.
The arguments for both of these programs are the same:
`python match_deep_learning.py dataset_filepath tba_api_key year event_name current_match match_type`
`python match_linear_regression.py dataset_filepath tba_api_key year event_name current_match match_type`
where `current_match` is the number of the current match that you want to predict and match_type is either qm, ef, qf, sf, or f (see the [api docs](https://www.thebluealliance.com/apidocs/v3) for more information).

The scripts will first output a visualization of the model which you will need to close and then the red and blue scores.

### Prerequisites
Keras==2.2.4
matplotlib==2.2.2
numpy==1.14.5
requests==2.18.4
scikit-learn==0.20.2
scikit-plot==0.3.7

### Installing
Simply download the source files and the required prerequisites above.

### Results
Shown below are the inputs of the 2016 StrongHold game (Ranking Score, Auto, Scale/Challenge, Goals, and Defense) and their correlation with the number of points that the alliance earned).

[logo]: https://www.dropbox.com/s/7urnl0kzd2qsxru/MLMatchPrediction.PNG?dl=0 "Linear Regression Results"
