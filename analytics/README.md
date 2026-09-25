
# Titanic Analytics Pipeline

## Overview

This module performs data profiling, cleaning, exploratory data analysis,
classification modeling, imbalance analysis, hyperparameter tuning,
regression analysis, and complete pipeline serialization.

## Dataset

The Titanic dataset was loaded once using Seaborn's built-in loader.
The original dataset was saved as titanic.csv for offline grading.

## Missing Values

Missing values were handled according to the assignment threshold rule.

## EDA

The analysis includes:
- Dataset profiling
- Missing-value analysis
- Age and fare distributions
- IQR-based outlier detection
- Survival analysis by sex
- Survival analysis by passenger class
- Survival analysis by sex and class
- Correlation heatmap
- Multivariate charts
- Standardization sanity check

## Classification

Three classifiers were trained:
- Logistic Regression
- Decision Tree
- Random Forest

All models used the same stratified train/test split and the preprocessing
steps were fitted only on the training data.

## Imbalance Handling

Baseline, class-weight-balanced, and SMOTE approaches were compared.

## Hyperparameter Tuning

Random Forest was tuned using GridSearchCV over:
- n_estimators
- max_depth
- max_features

OOB scoring was enabled.

## Regression

Linear regression was used to predict fare.

Metrics:
- MAE
- RMSE
- R²
- Adjusted R²

## Saved Model

The complete preprocessing and modeling pipeline was saved as:

titanic_best_pipeline.joblib
