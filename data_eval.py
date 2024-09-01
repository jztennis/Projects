"""Machine learning algorithm evaluation functions. 

NAME: <your name here>
DATE: Fall 2023
CLASS: CPSC 322

"""

from data_table import *
from data_util import *
from data_learn import *
from random import randint



#----------------------------------------------------------------------
# HW-8
#----------------------------------------------------------------------

def bootstrap(table): 
    """Creates a training and testing set using the bootstrap method.

    Args: 
        table: The table to create the train and test sets from.

    Returns: The pair (training_set, testing_set)

    """

    n = table.row_count()
    train = DataTable(table.columns())
    test = DataTable(table.columns())
    listnums = []
    for i in range(n):
        num = randint(0, n-1)
        train.append(table[num].values())
        if num not in listnums:
            listnums.append(num)
    for i in range(n):
        if i not in listnums:
            test.append(table[i].values())
    return train, test



def stratified_holdout(table, label_col, test_set_size):
    """Partitions the table into a training and test set using the holdout
    method such that the test set has a similar distribution as the
    table.

    Args:
        table: The table to partition.
        label_col: The column with the class labels. 
        test_set_size: The number of rows to include in the test set.

    Returns: The pair (training_set, test_set)

    """

    train = DataTable(table.columns())
    test = DataTable(table.columns())
    if test_set_size == 0:
        [train.append(row.values()) for row in table]
    else:
        labels_train = {}
        labels_test = {}
        count = 0
        for row in table:
            if count <= test_set_size:
                if row[label_col] not in list(labels_train.keys()):
                    labels_train[row[label_col]] = 1
                    train.append(row.values())
                elif row[label_col] not in list(labels_test.keys()):
                    labels_test[row[label_col]] = 1
                    test.append(row.values())
                    count += 1
                elif labels_test[row[label_col]] == labels_train[row[label_col]]:
                    labels_train[row[label_col]] += 1
                    train.append(row.values())
                else:
                    labels_test[row[label_col]] += 1
                    test.append(row.values())
                    count += 1
            else:
                train.append(row.values())
    return train, test
    


def tdidt_eval_with_tree(dt_root, test, label_col, columns):
    """Evaluates the given test set using tdidt over the training
    set, returning a corresponding confusion matrix.

    Args:
       td_root: The decision tree to use.
       test: The testing data set.
       label_col: The column being predicted.
       columns: The categorical columns

    Returns: A data table with n rows (one per label), n+1 columns (an
        'actual' column plus n label columns), and corresponding
        prediction vs actual label counts.

    Notes: If the naive bayes returns multiple labels for a given test
        instance, the first such label is selected.

    """

    labels = distinct_values(test, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)

    for label in labels:
        for row_test in test:
            if row_test[label_col] == label:

                pred = tdidt_predict(dt_root, row_test)

                if pred != None:
                    for row in conf_matrix:
                        if row["actual"] == label:
                            row[pred[0]] += 1
                            
    return conf_matrix



def random_forest(table, remainder, F, M, N, label_col, columns):
    """Returns a random forest build from the given table. 
    
    Args:
        table: The original table for cleaning up the decision tree.
        remainder: The table to use to build the random forest.
        F: The subset of columns to use for each classifier.
        M: The number of unique accuracy values to return.
        N: The total number of decision trees to build initially.
        label_col: The column with the class labels.
        columns: The categorical columns used for building the forest.

    Returns: A list of (at most) M pairs (tree, accuracy) consisting
        of the "best" decision trees and their corresponding accuracy
        values. The exact number of trees (pairs) returned depends on
        the other parameters (F, M, N, and so on).

    """

    forest = {}
    temp = 0
    while temp < N:
        tree = tdidt_F(table, label_col, F, columns)
        if type(tree) == AttributeNode:
            tree = resolve_attribute_values(tree, table)
        tree = resolve_leaf_nodes(tree)
        train, test = bootstrap(remainder)
        if test.row_count() != 0:
            conf_matrix = tdidt_eval(train, test, label_col, columns)
            acc = []
            dist = conf_matrix.columns()[1:]
            test = False
            for row in conf_matrix:
                for d in dist:
                    if row[d] != 0:
                        break
                    else:
                        test = True
            if not test:
                temp += 1
                for d in dist:
                    acc.append(accuracy(conf_matrix, d))
                avg = sum(acc) / len(dist)
                if avg not in list(forest.keys()):
                    forest[avg] = [tree]
                else:
                    forest[avg].append(tree)
    final = []
    temp = []
    count = 0
    while count < M:
        for tree in forest[max(list(forest.keys()))]:
            if count < M:
                count += 1
                temp.append(tree)
                temp.append(max(list(forest.keys())))
                final.append(temp)
            else:
                break
        del forest[max(list(forest.keys()))]
    return final



def random_forest_eval(table, train, test, F, M, N, label_col, columns):
    """Builds a random forest and evaluate's it given a training and
    testing set.

    Args: 
        table: The initial table.
        train: The training set from the initial table.
        test: The testing set from the initial table.
        F: Number of features (columns) to select.
        M: Number of trees to include in random forest.
        N: Number of trees to initially generate.
        label_col: The column with class labels. 
        columns: The categorical columns to use for classification.

    Returns: A confusion matrix containing the results. 

    Notes: Assumes weighted voting (based on each tree's accuracy) is
        used to select predicted label for each test row.

    """

    labels = distinct_values(train, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)

    forest = random_forest(table, train, F, M, N, label_col, columns)
    # ea. pair = (tree, accuracy)
    # for label in labels:
    for row_test in test:
            label_weight = {}
            for tree in forest:
                pred = tdidt_predict(tree[0], row_test)

                if pred not in list(label_weight.keys()) and pred != None:
                    label_weight[pred[0]] = pred[1]
                else:
                    if pred != None:
                        label_weight[pred[0]] += pred[1]
            if pred != None:
                for key, val in list(label_weight.items()):
                    if val == max(list(label_weight.values())):
                        final_pred = key
                for row in conf_matrix:
                    if row["actual"] == row_test[label_col]:
                        row[final_pred] += 1
    return conf_matrix
        


#----------------------------------------------------------------------
# HW-7
#----------------------------------------------------------------------



def tdidt_eval(train, test, label_col, columns):
    """Evaluates the given test set using tdidt over the training
    set, returning a corresponding confusion matrix.

    Args:
       train: The training data set.
       test: The testing data set.
       label_col: The column being predicted.
       columns: The categorical columns

    Returns: A data table with n rows (one per label), n+1 columns (an
        'actual' column plus n label columns), and corresponding
        prediction vs actual label counts.

    Notes: If the naive bayes returns multiple labels for a given test
        instance, the first such label is selected.

    """

    labels = distinct_values(train, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)
        
    tree = tdidt(train, label_col, columns)
    if type(tree) == AttributeNode:
        tree = resolve_attribute_values(tree, train)
    tree = resolve_leaf_nodes(tree)
                
    for label in labels:
        for row_test in test:
            if row_test[label_col] == label:

                pred = tdidt_predict(tree, row_test)

                if pred != None:
                    for row in conf_matrix:
                        if row["actual"] == label:
                            row[pred[0]] += 1
                            
    return conf_matrix


def tdidt_stratified(table, k_folds, label_col, columns):
    """Evaluates tdidt prediction approach over the table using stratified
    k-fold cross validation, returning a single confusion matrix of
    the results.

    Args:
        table: The data table.
        k_folds: The number of stratified folds to use.
        label_col: The column with labels to predict. 
        columns: The categorical columns for tdidt. 

    Notes: Each fold created is used as the test set whose results are
        added to a combined confusion matrix from evaluating each
        fold.

    """

    tablelist = stratify(table, label_col, k_folds)
    labels = distinct_values(table, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)
        
    for x in range(len(tablelist)):
        list1 = tablelist[:x] + tablelist[x+1:]
        train = union_all(list1)

        tree = tdidt(train, label_col, columns)
        if type(tree) == AttributeNode:
            tree = resolve_attribute_values(tree, train)
        tree = resolve_leaf_nodes(tree)
                
        if tablelist[x] != None:
            for row_test in tablelist[x]:
                # if row_test[label_col] == label:

                pred = tdidt_predict(tree, row_test)

                if pred != None:
                    for row in conf_matrix:
                        if row["actual"] == row_test[label_col]:
                            row[pred[0]] += 1

    return conf_matrix


#----------------------------------------------------------------------
# HW-6
#----------------------------------------------------------------------

def stratify(table, label_column, k):
    """Returns a list of k stratified folds as data tables from the given
    data table based on the label column.

    Args:
        table: The data table to partition.
        label_column: The column to use for the label. 
        k: The number of folds to return. 

    Note: Does not randomly select instances for the folds, and
        instead produces folds in order of the instances given in the
        table.

    """
    
    list = []
    list1 = []
    count = []
    for x in range(k):
        list.append(DataTable(table.columns()))
        list1.append([])
    for row in table:
        test = False
        for x in range(len(list)):
            if row[label_column] not in list1[x]:
                list[x].append(row.values())
                list1[x].append(row[label_column])
                test = True
                break
        if not test:
            count = []
            for x in range(k):
                count.append(0)
            for x in range(len(list1)):
                for y in list1[x]:
                    if row[label_column] == y:
                        count[x] += 1
            for x in range(len(count)):
                if count[x] == min(count):
                    list[x].append(row.values())
                    list1[x].append(row[label_column])
                    break
    return list



def union_all(tables):
    """Returns a table containing all instances in the given list of data
    tables.

    Args:
        tables: A list of data tables. 

    Notes: Returns a new data table that contains all the instances of
       the first table in tables, followed by all the instances in the
       second table in tables, and so on. The tables must have the
       exact same columns, and the list of tables must be non-empty.

    """

    if tables == []:
        raise ValueError('No Tables')
    for table in tables:
        table1 = table
        for table in tables:
            if table.columns() != table1.columns():
                raise ValueError('Mismatched Columns')
    
    newtable = DataTable(tables[0].columns())
    for table in tables:
        for row in table:
            newtable.append(row.values())
    return newtable




def naive_bayes_eval(train, test, label_col, continuous_cols, categorical_cols=[]):
    """Evaluates the given test set using naive bayes over the training
    set, returning a corresponding confusion matrix.

    Args:
       train: The training data set.
       test: The testing data set.
       label_col: The column being predicted.
       continuous_cols: The continuous columns (estimated via PDF)
       categorical_cols: The categorical columns

    Returns: A data table with n rows (one per label), n+1 columns (an
        'actual' column plus n label columns), and corresponding
        prediction vs actual label counts.

    Notes: If the naive bayes returns multiple labels for a given test
        instance, the first such label is selected.

    """
    
    labels = []
    for row in train:
        if row[label_col] not in labels:
            labels.append(row[label_col])
    labels = sorted(labels)
    conf_matrix = DataTable(["actual"] + labels)

    for label in labels:
        row = [label]
        for l in labels:
            row.append(0)
        for row_test in test:
            if row_test[label_col] == label:
                lab, lab_prob = naive_bayes(train, row_test, label_col, continuous_cols, categorical_cols)

                for x in range(len(labels)-1):
                    if lab[0] == labels[x+1]:
                        row[x] += 1
        conf_matrix.append(row)


    return conf_matrix



def naive_bayes_stratified(table, k_folds, label_col, cont_cols, cat_cols=[]):
    """Evaluates naive bayes over the table using stratified k-fold cross
    validation, returning a single confusion matrix of the results.

    Args:
        table: The data table.
        k_folds: The number of stratified folds to use.
        label_col: The column with labels to predict. 
        cont_cols: The continuous columns for naive bayes. 
        cat_cols: The categorical columns for naive bayes. 

    Notes: Each fold created is used as the test set whose results are
        added to a combined confusion matrix from evaluating each
        fold.

    """
    
    tablelist = stratify(table, label_col, k_folds)
    labels = distinct_values(table, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)

    for x in range(len(tablelist)):
        list1 = tablelist[:x] + tablelist[x+1:]
        train = union_all(list1)
                
        for label in labels:
            for row_test in tablelist[x]:
                if row_test[label_col] == label:
                    lab, lab_prob = naive_bayes(train, row_test, label_col, cont_cols, cat_cols)

                    for row in conf_matrix:
                        if row["actual"] == label:
                            row[lab[0]] += 1

    return conf_matrix


def knn_stratified(table, k_folds, label_col, vote_fun, k, num_cols, nom_cols=[]):
    """Evaluates knn over the table using stratified k-fold cross
    validation, returning a single confusion matrix of the results.

    Args:
        table: The data table.
        k_folds: The number of stratified folds to use.
        label_col: The column with labels to predict. 
        vote_fun: The voting function to use with knn.
        num_cols: The numeric columns for knn.
        nom_cols: The nominal columns for knn.

    Notes: Each fold created is used as the test set whose results are
        added to a combined confusion matrix from evaluating each
        fold.

    """
    
    tablelist = stratify(table, label_col, k_folds)
    labels = distinct_values(table, label_col)
    conf_matrix = DataTable(["actual"] + labels)
    for l in labels:
        row = [l]
        for _ in labels:
            row.append(0)
        conf_matrix.append(row)

    for x in range(len(tablelist)):
        list1 = tablelist[:x] + tablelist[x+1:]
        train = union_all(list1)
                
        for label in labels:
            for row_test in tablelist[x]:
                if row_test[label_col] == label:
                    pred = knn(train, row_test, k, num_cols, nom_cols)

                    keys = []
                    values = []
                    for key, value in pred.items():
                        for val in value:
                            values.append(val)
                        keys.append(key)

                    predicted_label = vote_fun(pred[min(keys)], keys, label_col)

                    for row in conf_matrix:
                        if row["actual"] == label:
                            row[predicted_label[0]] += 1

    return conf_matrix


#----------------------------------------------------------------------
# HW-5
#----------------------------------------------------------------------

def holdout(table, test_set_size):
    """Partitions the table into a training and test set using the holdout method. 

    Args:
        table: The table to partition.
        test_set_size: The number of rows to include in the test set.

    Returns: The pair (training_set, test_set)

    """

    train = DataTable(table.columns())
    test = DataTable(table.columns())
    total = table.row_count()
    count = 0
    rowlist = []
    while count < total:
        x = randint(0, total-1)
        if x not in rowlist:
            count += 1
            rowlist.append(x)

    count = 0
    for i in rowlist:
        if count < total - test_set_size:
            count += 1
            train.append(table[i].values())
        else:
            test.append(table[i].values())
    return train, test
    



def knn_eval(train, test, vote_fun, k, label_col, numeric_cols, nominal_cols=[]):
    """Returns a confusion matrix resulting from running knn over the
    given test set. 

    Args:
        train: The training set.
        test: The test set.
        vote_fun: The function to use for selecting labels.
        k: The k nearest neighbors for knn.
        label_col: The column to use for predictions. 
        numeric_cols: The columns compared using Euclidean distance.
        nominal_cols: The nominal columns for knn (match or no match).

    Returns: A data table with n rows (one per label), n+1 columns (an
        'actual' column plus n label columns), and corresponding
        prediction vs actual label counts.

    Notes: If the given voting function returns multiple labels, the
        first such label is selected.

    """

    labels = []
    for row in train:
        if row[label_col] not in labels:
            labels.append(row[label_col])
    labels = sorted(labels) 
    conf_matrix = DataTable(["actual"] + labels)

    for actual_label in labels:
        row = [actual_label] 
        for l in labels:
            row.append(0)

        for row_test in test:
            if row_test[label_col] == actual_label:
                pred = knn(train, row_test, k, numeric_cols, nominal_cols)

                keys = []
                values = []
                for key, value in pred.items():
                    for val in value:
                        values.append(val)
                        keys.append(key)

                predicted_label = vote_fun(values, keys, label_col)
            
                row[predicted_label[0]] += 1
                    
        conf_matrix.append(row)

    return conf_matrix



def accuracy(confusion_matrix, label):
    """Returns the accuracy for the given label from the confusion matrix.
    
    Args:
        confusion_matrix: The confusion matrix.
        label: The class label to measure the accuracy of.

    """

    list = 0
    total = 0
    for row in confusion_matrix:
        for x in confusion_matrix.columns():
            if x != 'actual':
                if row['actual'] == label and x == label:
                    list += row[x]
                    total += row[x]
                elif row['actual'] == label and x != label:
                    total += row[x]
                elif row['actual'] != label and x == label:
                    total += row[x]
                else:
                    list += row[x]
                    total += row[x]
    acc = list / total
    return acc



def precision(confusion_matrix, label):
    """Returns the precision for the given label from the confusion
    matrix.

    Args:
        confusion_matrix: The confusion matrix.
        label: The class label to measure the precision of.

    """

    list = 0
    for row in confusion_matrix:
        if row['actual'] == label:
            val = row[label]
        list += row[label]
    prec = val / list
    return prec



def recall(confusion_matrix, label): 
    """Returns the recall for the given label from the confusion matrix.

    Args:
        confusion_matrix: The confusion matrix.
        label: The class label to measure the recall of.

    """

    list = 0
    for row in confusion_matrix:
        if row['actual'] == label:
            val = row[label]
            for x in confusion_matrix.columns():
                if x != 'actual':
                    list += row[x]
    rcl = val / list
    return rcl
