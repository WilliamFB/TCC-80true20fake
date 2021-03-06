import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import (GridSearchCV, KFold, cross_val_score, cross_validate)
from sklearn.neighbors import LocalOutlierFactor

def grid_search_cv(model_obj, model_name, model_params, X, Y):
    N_TRIALS = 10
    N_SPLITS = 5

    non_nested_scores = []
    nested_scores = []
    trial_parameters = []

    microF1 = make_scorer(f1_score, average='micro')

    print(f'Performing nested cross-validation with {N_TRIALS} trials and {N_SPLITS} splits...')
    for i in range(N_TRIALS):

        print(f'\n##################################################')
        print(f'####### {model_name} : TRIAL {i+1:02} / {N_TRIALS:02} #######'.ljust(50, '#'))
        print(f'##################################################\n')

        inner_cv = KFold(n_splits=N_SPLITS, shuffle=True, random_state=i)
        outer_cv = KFold(n_splits=N_SPLITS, shuffle=True, random_state=i)

        # Non_nested parameter search and scoring
        clf = GridSearchCV(model_obj, model_params, cv=inner_cv, n_jobs=-1, scoring=microF1, verbose=1)
        clf.fit(X, Y)
        non_nested_scores.append(clf.best_score_)
        trial_parameters.append(clf.best_params_)

        # Nested CV with parameter optimization
        nested_score = cross_validate(clf, X, Y, cv=outer_cv, scoring=('accuracy', 'precision', 'recall', 'f1_micro', 'f1_macro', 'f1_weighted'), verbose=1)
        nested_scores.append(nested_score)

    print(f'Finding which nested CV produced the best result...')
    f1_micro_best = -1
    bestIndex = -1
    for i in range(N_TRIALS):
        f1_micro_avg = np.mean(nested_scores[i]['test_f1_micro'])
        if (f1_micro_avg > f1_micro_best):
            print(f'\tBest average f1_micro = {f1_micro_avg} so far found at trial # {i+1}')
            f1_micro_best = f1_micro_avg
            bestIndex = i

    print(f'Fetching test metrics from the best nested CV...')
    bestParams = trial_parameters[bestIndex]
    bestScores = \
    { 
        '_fit_time' : np.mean(nested_scores[bestIndex]['fit_time']),
        '_score_time' : np.mean(nested_scores[bestIndex]['score_time']),
        '_accuracy' : np.mean(nested_scores[bestIndex]['test_accuracy']),
        '_precision' : np.mean(nested_scores[bestIndex]['test_precision']),
        '_recall' : np.mean(nested_scores[bestIndex]['test_recall']),
        '_f1_micro' : np.mean(nested_scores[bestIndex]['test_f1_micro']),
        '_f1_macro' : np.mean(nested_scores[bestIndex]['test_f1_macro']),
        '_f1_weighted' : np.mean(nested_scores[bestIndex]['test_f1_weighted']),
    }  

    return (bestScores, bestParams)
