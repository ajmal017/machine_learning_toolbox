from IPython.core.display import display
from sklearn.dummy import DummyClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
import numpy as np
from sklearn.utils import check_X_y
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score
import time
import random
import Sklearn_model_utils as modelutil

from sklearn.preprocessing import StandardScaler, RobustScaler, QuantileTransformer, Normalizer
# from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn import feature_selection

from sklearn.impute import SimpleImputer
# from sklearn.impute import IterativeImputer

from imblearn.over_sampling import SMOTE
from imblearn.over_sampling import ADASYN
from imblearn.over_sampling import RandomOverSampler
from imblearn.combine import SMOTEENN
from imblearn.combine import SMOTETomek
from imblearn.under_sampling import ClusterCentroids
from imblearn.under_sampling import RandomUnderSampler
from imblearn.under_sampling import EditedNearestNeighbours
from imblearn.under_sampling import CondensedNearestNeighbour
from imblearn.under_sampling import NearMiss
from imblearn.under_sampling import AllKNN
from imblearn.under_sampling import NeighbourhoodCleaningRule
from imblearn.under_sampling import InstanceHardnessThreshold
from imblearn.ensemble import BalancedBaggingClassifier  # Does not work
from imblearn.ensemble import BalancedRandomForestClassifier  # Does not work
from imblearn.ensemble import RUSBoostClassifier  # Does not work

from sklearn.linear_model import LogisticRegression  # For InstanceHardnessThreshold
from sklearn.tree import DecisionTreeClassifier  # For Random Forest Balancer

from imblearn.pipeline import Pipeline



def execute_baseline_classifier(X_train, y_train, X_test, y_test, y_classes, scorer):
    '''Baseline classifiers Most frequent class and stratified results '''

    # Dummy Classifier Most Frequent
    # Negative class (0) is most frequent
    dummy_majority = DummyClassifier(strategy='most_frequent').fit(X_train.values, y_train)

    # X_converted, y_converted = check_X_y(X=X_cross, y=y_cross)

    # Therefore the dummy 'most_frequent' classifier always predicts class 0
    y_dummy_pred = dummy_majority.predict(X_test.values)

    confusion = confusion_matrix(y_test, y_dummy_pred)

    class_names = np.array(list(y_classes.keys()))

    metric_majority = dummy_majority.score(X_test, y_test) #scorer(dummy_majority, y_test, y_dummy_pred) #f1_score(y_test, y_dummy_pred, average=f1_average_method)

    print("Accuracy of the most frequent predictor on training data: " + str(dummy_majority.score(X_train, y_train)))
    print('Most frequent class (dummy classifier)\n', confusion)
    print('F1 score={}'.format(metric_majority))

    # #### Stratified Class Prediction Results

    # Dummy classifier for stratified results, i.e. according to class distribution
    np.random.seed(0)
    dummy_majority = DummyClassifier(strategy='stratified').fit(X_train.values, y_train)
    y_dummy_pred = dummy_majority.predict(X_test.values)

    confusion = confusion_matrix(y_test, y_dummy_pred)

    metric_stratified = dummy_majority.score(X_test, y_test) #scorer(y_test, y_dummy_pred) #f1_score(y_test, y_dummy_pred, average=f1_average_method)

    print(
        "Accuracy of the stratified (generates predictions by respecting the training set’s class distribution) predictor on training data: " + str(
            dummy_majority.score(X_train, y_train)))
    print('Stratified classes (dummy classifier)\n', confusion)
    print('F1 score={}'.format(metric_stratified))

    return {'majority': metric_majority, 'stratified': metric_stratified}


def estimate_training_duration(model_clf, X_train, y_train, X_test, y_test, sample_numbers, scorer):
    """ Estimate training duration by executing smaller sizes of training data and measuring training time and score
    Example SVM scaling: O(n_samples^2 * n_features). 5000->40s, 500000 -> 40*10000=400000
    input: sample_numbers: list(range(100, 6500+1, 500))
    input: model_clf: svm.SVC(probability=True, C=1, gamma=0.01, kernel='rbf', verbose=False)
    """
    np.random.seed(0)
    durations = []
    scores = []
    for i in sample_numbers:
        # Set the number of samples fr
        numberOfSamples = i

        if X_train.shape[0] > numberOfSamples:
            _, X_train_subset, _, y_train_subset = train_test_split(X_train, y_train, random_state=0,
                                                                    test_size=numberOfSamples / X_train.shape[0],
                                                                    shuffle=True, stratify=y_train)
        else:
            X_train_subset = X_train
            y_train_subset = y_train
            print("No change of data. Size of X_train={}. Current size={}".format(X_train.shape[0], i))

        t = time.time()
        # local_time = time.ctime(t)
        # print("Start training the SVM at ", local_time)
        model_clf.fit(X_train_subset.values, y_train_subset)
        elapsed = time.time() - t
        durations.append(elapsed)
        y_test_pred = model_clf.predict(X_test)
        score = model_clf.score(X_test, y_test) #f1_score(y_test, y_test_pred, average=f1_average_method)  # Micro, consider skewed data for the whole dataset
        scores.append(score)
        print("Training of {} examples; duration {}s; f1-score={}".format(i, np.round(elapsed, 3), np.round(score, 3)))

    return sample_numbers, durations, scores

def get_top_median_method(method_name, model_results, refit_scorer_name, top_share=0.10):
    ''' inputs: name='scaler' '''
    # View best scaler

    #Merge results from all subsets
    merged_params_of_model_results = {}
    for d in model_results:
        merged_params_of_model_results.update(d)
    
    indexList=[model_results.loc[model_results['param_' + method_name] == model_results['param_' + method_name].unique()[i]].iloc[0, :].name for i in range(0, len(merged_params_of_model_results[method_name]))]
    print("Plot best {} values".format(method_name))
    display(model_results.loc[indexList].round(3))

    #number of results to consider
    number_results = np.int(model_results.shape[0]*top_share)
    print("The top 10% of the results are used, i.e {} samples".format(number_results))
    hist_label = model_results['param_' + method_name][0:number_results]#.apply(str).apply(lambda x: x[:20])
    source = hist_label.value_counts()/number_results #

    import DatavisualizationFunctions as vis

    median_values = vis.get_median_values_from_distributions(method_name, merged_params_of_model_results[method_name], model_results, refit_scorer_name)

    return median_values, source

def run_basic_svm(X_train, y_train, selected_features, scorers, refit_scorer_name, subset_share=0.1, n_splits=10, parameters=None):
    '''Run an extensive grid search over all parameters to find the best parameters for SVM Classifier.
    The search shall be done only with a subset of the data. Default subset is 0.1. Input is training and test data.

    subset_share=0.1'''

    #Create a subset to train on
    print("[Step 1]: Create a data subset")
    subset_min = 300    #Minimal subset is 100 samples.

    if subset_share * X_train.shape[0] < subset_min:
        number_of_samples = subset_min
        print("minimal number of samples used: ", number_of_samples)
    else:
        number_of_samples = subset_share * X_train.shape[0]

    X_train_subset, y_train_subset = modelutil.extract_data_subset(X_train, y_train, number_of_samples)
    print("Got subset sizes X train: {} and y train: {}".format(X_train_subset.shape, y_train_subset.shape))

    print("[Step 2]: Define test parameters")
    if parameters is None:  #If no parameters have been defined, then do full definition
        # Guides used from
        # https://www.kaggle.com/evanmiller/pipelines-gridsearch-awesome-ml-pipelines
        # Main set of parameters for the grid search run 1: Select scaler, sampler and kernel for the problem
        test_scaler = [StandardScaler(), RobustScaler(), QuantileTransformer(), Normalizer()]
        test_sampling = [modelutil.Nosampler(), ClusterCentroids(), RandomUnderSampler(), NearMiss(version=1),
                         EditedNearestNeighbours(),
                         AllKNN(), CondensedNearestNeighbour(random_state=0),
                         InstanceHardnessThreshold(random_state=0,
                                                   estimator=LogisticRegression(solver='lbfgs', multi_class='auto')),
                         SMOTE(), SMOTEENN(), SMOTETomek(), ADASYN()]
        test_C = [1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2, 1e3]

        # gamma default parameters
        param_scale = 1 / (X_train.shape[1] * np.mean(X_train.var()))

        parameters = [
            {
                'scaler': test_scaler,
                'sampling': test_sampling,
                'feat__cols': selected_features,
                'svm__C': test_C,  # default C=1
                'svm__kernel': ['linear', 'sigmoid']
            },
            {
                'scaler': test_scaler,
                'sampling': test_sampling,
                'feat__cols': selected_features,
                'svm__C': test_C,  # default C=1
                'svm__kernel': ['poly'],
                'svm__degree': [2, 3]  # Only relevant for poly
            },
            {
                'scaler': test_scaler,
                'sampling': test_sampling,
                'feat__cols': selected_features,
                'svm__C': test_C,  # default C=1
                'svm__kernel': ['rbf'],
                'svm__gamma': [param_scale, 1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2, 1e3]  # Only relevant in rbf, default='auto'=1/n_features
            }]

        # If no missing values, only one imputer strategy shall be used
        if X_train.isna().sum().sum() > 0:
            parameters['imputer__strategy'] = ['mean', 'median', 'most_frequent']
            print("Missing values used. Test different imputer strategies")
        else:
            print("No missing values. No imputer necessary")

        print("Selected Parameters: ", parameters)
    else:
        print("Parameters defined in the input: ", parameters)

    # Main pipeline for the grid search
    pipe_run1 = Pipeline([
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='median')),
        ('scaler', StandardScaler()),
        ('sampling', modelutil.Nosampler()),
        ('feat', modelutil.ColumnExtractor(cols=None)),
        ('svm', SVC())
    ])

    print("Pipeline: ", pipe_run1)

    print("Stratified KFold={} used.".format(n_splits))
    skf = StratifiedKFold(n_splits=n_splits)

    pipe_run1 = pipe_run1
    params_run1 = parameters #params_debug #params_run1
    grid_search_run1 = GridSearchCV(pipe_run1, params_run1, verbose=1, cv=skf, scoring=scorers, refit=refit_scorer_name,
                                   return_train_score=True, iid=True, n_jobs=-1).fit(X_train_subset, y_train_subset)

    results_run1 = modelutil.generate_result_table(grid_search_run1, params_run1, refit_scorer_name)
    print("Result size=", results_run1.shape)
    print("Number of NaN results: {}. Replace them with 0".format(
        np.sum(results_run1['mean_test_' + refit_scorer_name].isna())))

    return grid_search_run1, params_run1, pipe_run1, results_run1
