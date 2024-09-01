"""Machine learning algorithm implementations.

NAME: <your name here>
DATE: Fall 2023
CLASS: CPSC 322

"""

from data_table import *
from data_util import *
from decision_tree import *

from random import randint
import math


#----------------------------------------------------------------------
# HW-8
#----------------------------------------------------------------------


def random_subset(F, columns):
    """Returns F unique column names from the given list of columns. The
    column names are selected randomly from the given names.

    Args: 
        F: The number of columns to return.
        columns: The columns to select F column names from.

    Notes: If F is greater or equal to the number of names in columns,
       then the columns list is just returned.

    """

    if F >= len(columns):
        return columns
    else:
        count = 0
        temp = []
        while count < F:
            num = randint(0,len(columns)-1)
            if columns[num] not in temp:
                count += 1
                temp.append(columns[num])
        return temp



def tdidt_F(table, label_col, F, columns): 
    """Returns an initial decision tree for the table using information
    gain, selecting a random subset of size F of the columns for
    attribute selection. If fewer than F columns remain, all columns
    are used in attribute selection.

    Args:
        table: The table to build the decision tree from. 
        label_col: The column containing class labels. 
        F: The number of columns to randomly subselect
        columns: The categorical columns. 

    Notes: The resulting tree can contain multiple leaf nodes for a
        particular attribute value, may have attributes without all
        possible attribute values, and in general is not pruned.

    """

    newColumns = random_subset(F, columns)
    return tdidt(table, label_col, newColumns)



def closest_centroid(centroids, row, columns):
    """Given k centroids and a row, finds the centroid that the row is
    closest to.

    Args:
        centroids: The list of rows serving as cluster centroids.
        row: The row to find closest centroid to.
        columns: The numerical columns to calculate distance from. 
    
    Returns: The index of the centroid the row is closest to. 

    Notes: Uses Euclidean distance (without the sqrt) and assumes
        there is at least one centroid.

    """

    dist = 0
    index = 0
    for col in columns:
        dist += abs(centroids[0][col]-row[col])
    if len(centroids) > 1:
        for i in range(len(centroids)):
            newdist = 0
            for col in columns:
                newdist += abs(centroids[i][col]-row[col])
            if newdist < dist:
                dist = newdist
                index = i
    return index



def select_k_random_centroids(table, k):
    """Returns a list of k random rows from the table to serve as initial
    centroids.

    Args: 
        table: The table to select rows from.
        k: The number of rows to select values from.
    
    Returns: k unique rows. 

    Notes: k must be less than or equal to the number of rows in the table. 

    """

    centroids = []
    centroids_check = []
    if k <= table.row_count():
        count = 0
        while count < k:
            num = randint(0,table.row_count()-1)
            if num not in centroids_check:
                count += 1
                centroids.append(table[num])
                centroids_check.append(num)
    return centroids



def k_means(table, centroids, columns): 
    """Returns k clusters from the table using the initial centroids for
    the given numerical columns.

    Args:
        table: The data table to build the clusters from.
        centroids: Initial centroids to use, where k is length of centroids.
        columns: The numerical columns for calculating distances.

    Returns: A list of k clusters, where each cluster is represented
        as a data table.

    Notes: Assumes length of given centroids is number of clusters k to find.

    """

    clusters = []
    for c in centroids:
        clusters.append(DataTable(table.columns()))
    for row in table:
        clusters[closest_centroid(centroids, row, columns)].append(row.values())
    
    newcentroids = []
    for c in clusters:
        row1 = []
        for col in table.columns():
            total = 0
            for row in c:
                total += row[col]
            if total != 0:
                row1.append(total / c.row_count())
            else:
                row1.append(0)
        newcentroids.append(DataRow(table.columns(), row1))
    newclusters = []
    for c in centroids:
        newclusters.append(DataTable(table.columns()))
    for row in table:
        newclusters[closest_centroid(newcentroids, row, columns)].append(row.values())
    return newclusters
            


def tss(clusters, columns):
    """Return the total sum of squares (tss) for each cluster using the
    given numerical columns.

    Args:
        clusters: A list of data tables serving as the clusters
        columns: The list of numerical columns for determining distances.
    
    Returns: A list of tss scores for each cluster. 

    """

    tss_vals = []
    for c in clusters:
        centroid = []
        for col in columns:
            total = 0
            for row in c:
                total += row[col]
            centroid.append(total / c.row_count())
        tss = 0
        for row in c:
            for x in range(len(centroid)):
                tss += abs(row[c.columns()[x]] - centroid[x])
        tss_vals.append(tss)
    return tss_vals



#----------------------------------------------------------------------
# HW-7
#----------------------------------------------------------------------



def same_class(table, label_col):
    """Returns true if all of the instances in the table have the same
    labels and false otherwise.

    Args: 
        table: The table with instances to check. 
        label_col: The column with class labels.

    """

    test = []
    for r in table:
        if test == []:
            test.append(r[label_col])
        elif r[label_col] not in test:
            return False
    return True



def build_leaves(table, label_col):
    """Builds a list of leaves out of the current table instances.
    
    Args: 
        table: The table to build the leaves out of.
        label_col: The column to use as class labels

    Returns: A list of LeafNode objects, one per label value in the
        table.

    """

    nodes = []
    count = 0
    if table.row_count() != 0:
        for r in table:
            test = False
            if nodes != []:
                for n in nodes:
                    if n.label == r[label_col]:
                        n.count += 1
                        count += 1
                        test = True
                if not test:
                    nodes.append(LeafNode(r[label_col],1,1))
                    count += 1
            else:
                nodes.append(LeafNode(r[label_col],1,1))
                count += 1
    else:
        return []
    for n in nodes:
        n.total = count
    return nodes



def calc_e_new(table, label_col, columns):
    """Returns entropy values for the given table, label column, and
    feature columns (assumed to be categorical). 

    Args:
        table: The table to compute entropy from
        label_col: The label column.
        columns: The categorical columns to use to compute entropy from.

    Returns: A dictionary, e.g., {e1:['a1', 'a2', ...], ...}, where
        each key is an entropy value and each corresponding key-value
        is a list of attributes having the corresponding entropy value. 

    Notes: This function assumes all columns are categorical.

    """

    if table.row_count() == 0:
        dict = {0: columns}
        return dict
    ents = {}
    for col in columns:
        distvals = distinct_values(table, col)
        temp1 = []
        for val in distvals:
            list1 = {}
            count = 0
            for row in table:
                if row[col] == val:
                    if row[label_col] not in list(list1.keys()):
                        list1[row[label_col]] = 1
                        count += 1
                    else:
                        list1[row[label_col]] += 1
                        count += 1
            endval = []
            for keys, vals, in list1.items():
                temp = vals/count
                log = math.log2(temp)
                endval.append(temp*log)
            temp1.append(((-1)*sum(endval))*(count/table.row_count()))
        temp2 = sum(temp1)
        if temp2 in list(ents.keys()):
            ents[temp2] = ents[temp2] + [col]
        else:
            ents[temp2] = [col]
    return ents



def tdidt(table, label_col, columns): 
    """Returns an initial decision tree for the table using information
    gain.

    Args:
        table: The table to build the decision tree from. 
        label_col: The column containing class labels. 
        columns: The categorical columns. 

    Notes: The resulting tree can contain multiple leaf nodes for a
        particular attribute value, may have attributes without all
        possible attribute values, and in general is not pruned.

    """
    if table.row_count() == 0:
        return None
    elif columns == []:
        leaves = build_leaves(table, label_col)
        return leaves
    elif same_class(table, label_col):
        leaves = build_leaves(table, label_col)
        return leaves
    elif not same_class(table, label_col):
        eNew = calc_e_new(table, label_col, columns)
        cols = sorted(list(eNew.keys()))
        tree = AttributeNode(eNew[cols[0]][0], {})
        for key in cols:
            for col in eNew[key]:
                dist = distinct_values(table, col)
                if len(dist) == 1:
                    leaves = build_leaves(table, label_col)
                    return leaves
                else:                
                    for d in dist:
                        newtable = DataTable(table.columns())
                        newtable1 = DataTable(table.columns())
                        for row in table:
                            if row[col] == d:
                                newtable.append(row.values())
                            else:
                                newtable1.append(row.values())
                        table = newtable1
                        tree.values[d] = tdidt(newtable, label_col, columns)
        return tree



def summarize_instances(dt_root):
    """Return a summary by class label of the leaf nodes within the given
    decision tree.

    Args: 
        dt_root: The subtree root whose (descendant) leaf nodes are summarized. 

    Returns: A dictionary {label1: count, label2: count, ...} of class
        labels and their corresponding number of instances under the
        given subtree root.

    """

    final = {}
    if type(dt_root) == AttributeNode:
        for key in dt_root.values.keys():
            vals = summarize_instances(dt_root.values[key]) # dictionary
            for key, val in vals.items():
                if key not in final.keys():
                    final[key] = val
                else:
                    final[key] += val
        return final
    else:
        if type(dt_root) == list:
            temp = {}
            for leaf in dt_root:
                vals = summarize_instances(leaf) # dictionary
                for key, val in vals.items():
                    if key not in temp.keys():
                        temp[key] = val
                    else:
                        temp[key] += val
            return temp
        else:
            return {dt_root.label: dt_root.count}



def resolve_leaf_nodes(dt_root):
    """Modifies the given decision tree by combining attribute values with
    multiple leaf nodes into attribute values with a single leaf node
    (selecting the label with the highest overall count).

    Args:
        dt_root: The root of the decision tree to modify.

    Notes: If an attribute value contains two or more leaf nodes with
        the same count, the first leaf node is used.

    """

    if type(dt_root) == AttributeNode:
        final = AttributeNode(dt_root.name, values={})
        for key in dt_root.values.keys():
            vals = resolve_leaf_nodes(dt_root.values[key])
            if type(vals) == LeafNode:
                final.values[key] = [vals]
            else:
                final.values[key] = vals
        return final
    else:
        if type(dt_root) == list:
            list1 = LeafNode('a',0,0)
            for leaf in dt_root:
                if leaf.count > list1.count:
                    list1 = leaf
            return list1
        else:
            return dt_root



def resolve_attribute_values(dt_root, table):
    """Return a modified decision tree by replacing attribute nodes
    having missing attribute values with the corresponding summarized
    descendent leaf nodes.
    
    Args:
        dt_root: The root of the decision tree to modify.
        table: The data table the tree was built from. 

    Notes: The table is only used to obtain the set of unique values
        for attributes represented in the decision tree.

    """

    if table.row_count() == 0:
        return dt_root
    temp = AttributeNode(dt_root.name, {})
    for key in dt_root.values.keys():
        if type(dt_root.values[key]) == AttributeNode:
            vals = resolve_attribute_values(dt_root.values[key], table)
            temp.values[key] = vals
        elif type(dt_root.values[key]) == list:
            temp.values[key] = dt_root.values[key]
    if len(distinct_values(table, dt_root.name)) != len(list(temp.values.keys())):
        if len(list(temp.values.keys())) == 1:
            return temp.values[list(temp.values.keys())[0]]
        else:
            list1 = []
            total = 0
            for key in temp.values.keys():
                if type(temp.values[key]) == list: 
                    list1.append(temp.values[key][0])
                    total += temp.values[key][0].total
            for t in list1:
                t.total = total
            return list1
    elif len(distinct_values(table, dt_root.name)) == len(list(temp.values.keys())):
        return temp
    else:
        return temp.values



def tdidt_predict(dt_root, instance): 
    """Returns the class for the given instance given the decision tree. 

    Args:
        dt_root: The root node of the decision tree. 
        instance: The instance to classify. 

    Returns: A pair consisting of the predicted label and the
       corresponding percent value of the leaf node.

    """

    if type(dt_root) == LeafNode:
        return dt_root.label, dt_root.percent()
    if type(dt_root) == AttributeNode:
        for key in dt_root.values.keys():
            if instance[dt_root.name] == key:
                return tdidt_predict(dt_root.values[key], instance)
    if type(dt_root) == list:
        return dt_root[0].label, dt_root[0].percent()



#----------------------------------------------------------------------
# HW-6
#----------------------------------------------------------------------

def naive_bayes(table, instance, label_col, continuous_cols, categorical_cols=[]):
    """Returns the labels with the highest probabibility for the instance
    given table of instances using the naive bayes algorithm.

    Args:
       table: A data table of instances to use for estimating most probably labels.
       instance: The instance to classify.
       continuous_cols: The continuous columns to use in the estimation.
       categorical_cols: The categorical columns to use in the estimation. 

    Returns: A pair (labels, prob) consisting of a list of the labels
        with the highest probability and the corresponding highest
        probability.

    """

    labels = []
    lab_counts = []
    for row in table:
        if row[label_col] not in labels:
            labels.append(row[label_col])
            lab_counts.append(1)
        else:
            for x in range(len(labels)):
                if row[label_col] == labels[x]:
                    lab_counts[x] += 1

    cond_prob_cat = []
    cond_prob_cont = []
    for label in labels:
        pos_cat_col = [[0, 0] for col in categorical_cols]
        pos_cont_col = [[0, 0] for col in continuous_cols]
        newtable = DataTable(table.columns())
        for row in table:
            if row[label_col] == label:
                newtable.append(row.values())
                if categorical_cols != []:
                    for x in range(len(categorical_cols)):
                        if row[categorical_cols[x]] == instance[categorical_cols[x]]:
                            pos_cat_col[x][0] += 1
                            pos_cat_col[x][1] += 1
                        else:
                            pos_cat_col[x][1] += 1 
                if continuous_cols != []:
                    for x in range(len(continuous_cols)):
                        pos_cont_col[x][0] += row[continuous_cols[x]]
                        pos_cont_col[x][1] += 1

        if categorical_cols != []:
            newlist = []
            for x in range(len(pos_cat_col)):
                newlist.append(pos_cat_col[x][0] / pos_cat_col[x][1])
            res_cat = newlist[0]
            for x in range(len(newlist)-1):
                res_cat = res_cat * newlist[x+1]
            cond_prob_cat.append(res_cat)
            
        if continuous_cols != []:
            newlist = []
            for x in range(len(pos_cont_col)):
                mean = pos_cont_col[x][0] / pos_cont_col[x][1]
                newlist.append(gaussian_density(instance[continuous_cols[x]], mean, std_dev(newtable, continuous_cols[x])))
            res_cont = newlist[0]
            for x in range(len(newlist)-1):
                res_cont = res_cont * newlist[x+1]
            cond_prob_cont.append(res_cont)
            
    prob_labels = [count / table.row_count() for count in lab_counts]

    final_prob = 0
    final_labels = []
    for x in range(len(labels)):
        if categorical_cols != [] and continuous_cols == []:
            if cond_prob_cat[x] * prob_labels[x] > final_prob:
                final_prob = cond_prob_cat[x] * prob_labels[x]
                final_labels = [labels[x]]
            elif cond_prob_cat[x] * prob_labels[x] == final_prob:
                final_labels.append(labels[x])
        elif continuous_cols != [] and categorical_cols == []:
            if cond_prob_cont[x] * prob_labels[x] > final_prob:
                final_prob = cond_prob_cont[x] * prob_labels[x]
                final_labels = [labels[x]]
            elif cond_prob_cont[x] * prob_labels[x] == final_prob:
                final_labels.append(labels[x])

    return final_labels, final_prob
    
    



def gaussian_density(x, mean, sdev):
    """Return the probability of an x value given the mean and standard
    deviation assuming a normal distribution.

    Args:
        x: The value to estimate the probability of.
        mean: The mean of the distribution.
        sdev: The standard deviation of the distribution.

    """
    
    var = sdev**2
    deno = (2*math.pi*var)**(1/2)
    num = math.exp(-(x-mean)**2 / (2*var))
    return num/deno


#----------------------------------------------------------------------
# HW-5
#----------------------------------------------------------------------

def knn(table, instance, k, numerical_columns, nominal_columns=[]):
    """Returns the k closest distance values and corresponding table
    instances forming the nearest neighbors of the given instance. 

    Args:
        table: The data table whose instances form the nearest neighbors.
        instance: The instance to find neighbors for in the table.
        k: The number of closest distances to return.
        numerical_columns: The numerical columns to use for comparison.
        nominal_columns: The nominal columns to use for comparison (if any).

    Returns: A dictionary with k key-value pairs, where the keys are
        the distances and the values are the corresponding rows.

    Notes: 
        The numerical and nominal columns must be disjoint. 
        The numerical and nominal columns must be valid for the table.
        The resulting score is a combined distance without the final
        square root applied.

    """
    
    dic = {}
    for row in table:
        dist = 0
        for column in numerical_columns:
            dist += (row[column] - instance[column]) ** 2
        if nominal_columns != []:
            for column in nominal_columns:
                if row[column] != instance[column]:
                    dist += 1
        if dist in dic:
            dic[dist].append(row)
        else:
            dic[dist] = [row]
    sorted_dic = sorted(dic.items())[:k]
    return dict(sorted_dic)



def majority_vote(instances, scores, labeled_column):
    """Returns the labels in the given instances that occur the most.

    Args:
        instances: A list of instance rows.
        labeled_column: The column holding the class labels.

    Returns: A list of the labels that occur the most in the given
    instances.

    """

    list = []
    count = []
    for x in range(len(instances)):
        if instances[x][labeled_column] in list:
            for y in range(len(list)):
                if instances[x][labeled_column] == list[y]:
                    count[y] += 1
        else:
            list.append(instances[x][labeled_column])
            count.append(1)
    final = []
    max_count = max(count)
    for x in range(len(list)):
        if count[x] == max_count:
            final.append(list[x])
    return final



def weighted_vote(instances, scores, labeled_column):
    """Returns the labels in the given instances with the largest total
    sum of corresponding scores.

    Args:
        instances: The list of instance rows.
        scores: The corresponding scores for each instance.
        labeled_column: The column with class labels.

    """

    list = []
    count = []
    for x in range(len(instances)):
        if instances[x][labeled_column] in list:
            for y in range(len(list)):
                if instances[x][labeled_column] == list[y]:
                    count[y] += scores[x]
        else:
            list.append(instances[x][labeled_column])
            count.append(scores[x])
    final = []
    max_count = max(count)
    for x in range(len(list)):
        if count[x] == max_count:
            final.append(list[x])
    return final