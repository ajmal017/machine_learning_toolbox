import random
import numpy as np

def inverse_dict(dictionary):
    #Inverse a dictionary
    dictionary_reverse = {}
    for k, v in dictionary.items():
        dictionary_reverse[v] = k
    return dictionary_reverse

def get_data_subset_index(numberOfSamples, X):
    #Get a random subset of data from a set
    np.random.seed(0)
    if X.shape[0] > numberOfSamples:
        X_index_subset = random.sample(list(range(0, X.shape[0], 1)), k=numberOfSamples)
        print("Cutting the data to ", numberOfSamples)
    else:
        X_index_subset = list(range(0, X.shape[0], 1))
        print("No change of data. Size remains ", X.shape[0])
    print("Created a training subset")
    
    return X_index_subset

def is_multi_class(y_classes):
    # Check if y is binarized
    if len(y_classes) == 2 and np.max(list(y_classes.keys())) == 1:
        is_multiclass = False
        print("Classes are binarized, 2 classes.")
    else:
        is_multiclass = True
        print("Classes are not binarized, {} classes with values {}. "
              "For a binarized class, the values should be [0, 1].".format(len(y_classes), list(y_classes.keys())))
    return is_multiclass

#class ColumnExtractor(object):
#    '''Column extractor method to extract selected columns from a list. This is used as a feature selector. Source
#    https://stackoverflow.com/questions/25250654/how-can-i-use-a-custom-feature-selection-function-in-scikit-learns-pipeline.'''#
#
#    def __init__(self, cols):
#        self.cols = cols
#
#    def transform(self, X):
#        col_list = []
#        #for c in self.cols:
#        #    col_list.append(X[:, c:c+1])
#        #return np.concatenate(col_list, axis=1)
#        return X[self.cols]
#
#    def fit(self, X, y=None):
#        return self

def getListFromColumn(df, df_source, col_number):
    '''Get a list of column indices from a source'''
    #Get list of column names from a column number
    col_names = list(df[df.columns[col_number]].dropna().values)
    #Get list of column indices in the other data frame.
    col_index = [i for i, col in enumerate(df_source) if col in col_names]

    return col_index

def get_unique_values_from_list_of_dicts(key, list_of_dicts, is_item_string=True):
    '''
        Get all unique values from a list of dictionaries for a certain key

        :key: key in the dicts
        :list_of_dicts: list of dictionaries
        :is_item_string: If true, then all values are converted to string and then compared. If False, object id
        is compared

        :return: list of unique values
    '''

    # Get all values from all keys scaler in a list
    sublist = [x[key] for x in list_of_dicts] # Get a list of lists with all values from all keys
    flatten = lambda l: [item for sublist in l for item in sublist]  # Lambda flatten function
    flattended_list = flatten(sublist) #Flatten the lists of lists

    if is_item_string==True: #Make string
        elements = [str(element) for element in flattended_list]
    else:
        elements = flattended_list
    unique_list = list(set(elements)) #Get unique values of list by converting it into a set and then to list

    # Replace strings with their original values
    unique_list_instance = list()
    for element_string in unique_list:
        for element in flattended_list:
            if element_string == str(element):
                unique_list_instance.append(element)
                break

    return unique_list_instance

def get_median_values_from_distributions(method_name, unique_param_values, model_results, refit_scorer_name):
    '''Extract the median values from a list of distributions

    :method_name: Parameter name, e.g. scaler
    :unique_param_values: list of unique parameter values
    :model_results: grid search results
    :refit_scorer_name: refit scorer name for the end scores

    :return: dict of median values for each unique parameter value

    '''
    median_result = dict()
    for i in unique_param_values:
        p0 = model_results[model_results['param_' + method_name].astype(str) == str(i)]['mean_test_' + refit_scorer_name]
        if (len(p0) > 0):
            median_hist = np.round(np.percentile(p0, 50), 3)
            median_result[i] = median_hist

    return median_result

def list_to_name(list_of_lists, list_names, result):
    '''
    In a series, replace a list of integers with a string. This is used in grid search to give a list of columns
    a certain name.

    :list_of_lists: list of lists with selected features [[list1], [list2]]. This list have the keys
    :list_names: list of names for the list of lists [name1, name2]
    :result: Input Series, where the values shall be replaced. The values in the format of a list are replaced by
    strings. This is done inplace

    :return: None

    '''

    for k, value in enumerate(result):
        indices = [i for i, x in enumerate(list_of_lists) if x == value]
        if len(indices) > 0:
            first_index = indices[0]
            result.iloc[k] = list_names[first_index]
        if k % 50 == 0:
            print("run ", k)

def replace_lists_in_grid_search_params_with_strings(selected_features, feature_dict, params_run1_copy):
    '''
    In a list of dict, which are parameters for a grid search, replace certain lists with a string. This is used to
    replace a list of selected features in the grid search

    :selected_features: list of lists with selected features [[list1], [list2]]. This list have the keys
    :feature_dict: list of names for the list of lists [name1, name2]
    :params_run1_copy: [dict(), dict()] with parameters

    :return: None

    '''
    for i, value in enumerate(params_run1_copy):
        #print(value['feat__cols'])
        for k, f in enumerate(value['feat__cols']):
            indices = [i for i, x in enumerate(selected_features) if x == f]
            if len(indices) > 0:
                first_index = indices[0]
                new_value = list(feature_dict.keys())[first_index]
                params_run1_copy[i]['feat__cols'][k] = new_value
                print("Replaced {} with {}".format(selected_features[first_index], new_value))