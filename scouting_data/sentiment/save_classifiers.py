import os
import pickle
import random

import nltk
# from nltk.corpus import movie_reviews
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.svm import LinearSVC

documents_f = open(os.path.join(os.path.dirname(__file__), "pickled_algos/documents.pickle"), "rb")
documents = pickle.load(documents_f)
documents_f.close()

word_features5k_f = open(os.path.join(os.path.dirname(__file__), "pickled_algos/word_features5k.pickle"), "rb")
word_features = pickle.load(word_features5k_f)
word_features5k_f.close()


def find_features(document):
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features


featuresets = [(find_features(rev), category) for (rev, category) in documents]

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/featuresets.pickle"), "wb")
pickle.dump(featuresets, open_file)
open_file.close()

random.shuffle(featuresets)
print(len(featuresets))

testing_set = featuresets[10000:]
training_set = featuresets[:10000]

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/originalnaivebayes5k.pickle"), "wb")
classifier = nltk.NaiveBayesClassifier.train(training_set)
pickle.dump(classifier, open_file)
open_file.close()

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/MNB_classifier5k.pickle"), "wb")
classifier = SklearnClassifier(MultinomialNB()).train(training_set)
pickle.dump(classifier, open_file)
open_file.close()

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/BernoulliNB_classifier5k.pickle"), "wb")
classifier = SklearnClassifier(BernoulliNB()).train(training_set)
pickle.dump(classifier, open_file)
open_file.close()

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/LogisticRegression_classifier5k.pickle"), "wb")
classifier = SklearnClassifier(LogisticRegression()).train(training_set)
pickle.dump(classifier, open_file)
open_file.close()

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/LinearSVC_classifier5k.pickle"), "wb")
classifier = SklearnClassifier(LinearSVC()).train(training_set)
pickle.dump(classifier, open_file)
open_file.close()

open_file = open(os.path.join(os.path.dirname(__file__), "pickled_algos/SGDC_classifier5k.pickle"), "wb")
classifier = SklearnClassifier(SGDClassifier()).train(training_set)
pickle.dump(classifier, open_file)
open_file.close()
