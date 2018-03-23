# -*- coding: utf-8 -*-
import argparse
import sys

import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def Header():
    print('Estimate uncertainty by RandonForet algorithym')
    print


def ParseCmdLine():
    parser = argparse.ArgumentParser(description='Estimate uncertainty by RandonForet algorithym.')
    parser.add_argument('-w', '--workdirectory', help='File dir.')
    parser.add_argument('-t', '--train', help='Train.')
    parser.add_argument('-d', '--dump', help='Dump.')
    parser.add_argument('-f', '--file', help='Output file name.')
    parser.add_argument('-s', '--select', help='Select.')
    parser.add_argument('-d', '--drop', help='Drop.')

    try:
        return parser.parse_args()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


features, targets = None, None


def prepBoston():
    global features, targets
    boston = datasets.load_boston()
    bostonFeatures = pd.DataFrame(boston.data, columns=boston.feature_names)
    bostonTargets = boston.target


def regressionBoston():
    global bostonFeatures, bostonTargets
    X_train, X_test, y_train, y_test = train_test_split(bostonFeatures, bostonTargets, train_size=0.8, random_state=42)
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = pd.DataFrame(scaler.transform(X_train), index=X_train.index.values, columns=X_train.columns.values)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), index=X_test.index.values, columns=X_test.columns.values)
    pca = PCA()
    pca.fit(X_train)
    cpts = pd.DataFrame(pca.transform(X_train))
    x_axis = np.arange(1, pca.n_components_ + 1)
    pca_scaled = PCA()
    pca_scaled.fit(X_train_scaled)
    cpts_scaled = pd.DataFrame(pca.transform(X_train_scaled))

    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=500, oob_score=True, random_state=0)
    rf.fit(X_train, y_train)

    from sklearn.metrics import r2_score
    from scipy.stats import spearmanr, pearsonr
    predicted_train = rf.predict(X_train)
    predicted_test = rf.predict(X_test)
    test_score = r2_score(y_test, predicted_test)
    spearman = spearmanr(y_test, predicted_test)
    pearson = pearsonr(y_test, predicted_test)
    print('Out-of-bag R-2 score estimate: {0}'.format(rf.oob_score_))
    print('Test data R-2 score: {0}'.format(test_score))
    print('Test data Spearman correlation: {0}'.format(spearman[0]))
    print('Test data Pearson correlation: {0}'.format(pearson[0]))


def randomForestRegression():
    prepBoston()
    regressionBoston()


if __name__ == "__main__":
    #    randomForestClassification()
    randomForestRegression()
    print()
