"""Data utility functions.

NAME: Jared Zaugg
DATE: Fall 2023
CLASS: CPSC 322

"""

from math import sqrt

from data_table import DataTable, DataRow
import matplotlib.pyplot as plt


#----------------------------------------------------------------------
# HW5
#----------------------------------------------------------------------

def normalize(table, column):
    """Normalize the values in the given column of the table. This
    function modifies the table.

    Args:
        table: The table to normalize.
        column: The column in the table to normalize.

    """

    list = []
    for row in table:
        list.append(row[column])
    for row in table:
        row[column] = (row[column]-min(list)) / (max(list)-min(list))
    



def discretize(table, column, cut_points):
    """Discretize column values according to the given list of n-1
    cut_points to form n ordinal values from 1 to n. This function
    modifies the table.

    Args:
        table: The table to discretize.
        column: The column in the table to discretize.

    """

    for row in table:
        test = False
        for i in range(len(cut_points)):
            if row[column] < cut_points[i]:
                row[column] = i + 1
                test = True
                break
        if test == False:
            row[column] = len(cut_points) + 1
        
        


#----------------------------------------------------------------------
# HW4
#----------------------------------------------------------------------



def column_values(table, column):
    """Returns a list of the values (in order) in the given column.

    Args:
        table: The data table that values are drawn from
        column: The column whose values are returned
    
    """

    list = []
    for row in table:
        list.append(row[column])
    return list



def mean(table, column):
    """Returns the arithmetic mean of the values in the given table
    column.

    Args:
        table: The data table that values are drawn from
        column: The column to compute the mean from

    Notes: 
        Assumes there are no missing values in the column.

    """

    n = 0
    sum = 0
    for row in table:
        n = n + 1
        sum = sum + row[column]
    return sum / n



def variance(table, column):
    """Returns the variance of the values in the given table column.

    Args:
        table: The data table that values are drawn from
        column: The column to compute the variance from

    Notes:
        Assumes there are no missing values in the column.

    """

    m = mean(table,column)
    sum = 0
    n = 0
    for row in table:
        n = n + 1
        var = m - row[column]
        sum = sum + var**2
    return sum / n


def std_dev(table, column):
    """Returns the standard deviation of the values in the given table
    column.

    Args:
        table: The data table that values are drawn from
        column: The colume to compute the standard deviation from

    Notes:
        Assumes there are no missing values in the column.

    """

    return sqrt(variance(table,column))



def covariance(table, x_column, y_column):
    """Returns the covariance of the values in the given table columns.
    
    Args:
        table: The data table that values are drawn from
        x_column: The column with the "x-values"
        y_column: The column with the "y-values"

    Notes:
        Assumes there are no missing values in the columns.        

    """

    xm = mean(table, x_column)
    ym = mean(table, y_column)
    n = 0
    sum = 0
    for row in table:
        n = n + 1
        sum = sum + (row[x_column]-xm)*(row[y_column]-ym)
    return sum / n



def linear_regression(table, x_column, y_column):
    """Returns a pair (slope, intercept) resulting from the ordinary least
    squares linear regression of the values in the given table columns.

    Args:
        table: The data table that values are drawn from
        x_column: The column with the "x values"
        y_column: The column with the "y values"

    """

    cc = correlation_coefficient(table, x_column, y_column)
    xstd = std_dev(table, x_column)
    ystd = std_dev(table, y_column)
    xm = mean(table, x_column)
    ym = mean(table, y_column)

    slope = cc * (ystd/xstd)
    slope = round(slope)
    intercept = ym - (slope * xm)
    intercept = round(intercept)
    
    return slope, intercept



def correlation_coefficient(table, x_column, y_column):
    """Return the correlation coefficient of the table's given x and y
    columns.

    Args:
        table: The data table that value are drawn from
        x_column: The column with the "x values"
        y_column: The column with the "y values"

    Notes:
        Assumes there are no missing values in the columns.        

    """

    cov = covariance(table, x_column, y_column)
    xstd = std_dev(table, x_column)
    ystd = std_dev(table, y_column)
    return cov/(xstd*ystd)


def frequency_of_range(table, column, start, end):
    """Return the number of instances of column values such that each
    instance counted has a column value greater or equal to start and
    less than end. 
    
    Args:
        table: The data table used to get column values from
        column: The column to bin
        start: The starting value of the range
        end: The ending value of the range

    Notes:
        start must be less than end

    """

    n = 0
    for row in table:
        if row[column] >= start and row[column] < end:
            n = n + 1
    return n


def histogram(table, column, nbins, xlabel, ylabel, title, filename=None):
    """Create an equal-width histogram of the given table column and number of bins.
    
    Args:
        table: The data table to use
        column: The column to obtain the value distribution
        nbins: The number of equal-width bins to use
        xlabel: The label of the x-axis
        ylabel: The label of the y-axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """
    
    list = []
    for row in table:
        list = list + [row[column]]
    plt.figure()
    plt.hist(list, nbins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()
    

def scatter_plot_with_best_fit(table, xcolumn, ycolumn, xlabel, ylabel, title, filename=None):
    """Create a scatter plot from given values that includes the "best fit" line.
    
    Args:
        table: The data table to use
        xcolumn: The column for x-values
        ycolumn: The column for y-values
        xlabel: The label of the x-axis
        ylabel: The label of the y-axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    xvalues = []
    yvalues = []
    for row in table:
        xvalues = xvalues + [row[xcolumn]]
        yvalues = yvalues + [row[ycolumn]]
    slope, intercept = linear_regression(table, xcolumn, ycolumn)
    max1 = max(xvalues)
    min1 = min(xvalues)
    y1 = slope*max1 + intercept
    y2 = slope*min1 + intercept
        
    plt.figure()
    plt.scatter(xvalues, yvalues)
    plt.plot([min1,max1], [y2,y1], linestyle = '-', color = 'r')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()
    


#----------------------------------------------------------------------
# HW3
#----------------------------------------------------------------------



def distinct_values(table, column):
    """Return the unique values in the given column of the table.
    
    Args:
        table: The data table used to get column values from.
        column: The column of the table to get values from.

    Notes:
        Returns a list of unique values
    """

    list = []
    for r in table:
        if r[column] != None and r[column] not in list:
            list.append(r[column])
    return list



def remove_missing(table, columns):
    """Return a new data table with rows from the given one without
    missing values.

    Args:
        table: The data table used to create the new table.
        columns: The column names to check for missing values.

    Returns:
        A new data table.

    Notes: 
        Columns must be valid.

    """

    newtable = DataTable(columns=table.columns())
    for r in table:
        has_missing_value = False
        for col in columns:
            if r[col] == '':
                has_missing_value = True
                break
        if has_missing_value == False:
            newtable.append(r.values())
    return newtable



def duplicate_instances(table):
    """Returns a table containing duplicate instances from original table.
    
    Args:
        table: The original data table to check for duplicate instances.

    """

    newtable = DataTable(table.columns())
    if table == None:
        return newtable
    test = []
    for row in table:
        newrows = row.values()
        if newrows in test:
            count = 0
            for x in test:
                if newrows == x:
                    count = count + 1
            if count == 1:
                newtable.append(newrows)
            test = test + [newrows]
        else:
            test = test + [newrows]
    return newtable



def remove_duplicates(table):
    """Remove duplicate instances from the given table.
    
    Args:
        table: The data table to remove duplicate rows from

    """

    newtable = DataTable(table.columns())
    if table == None:
        return newtable
    test = []
    for row in table:
        newrows = []
        for x in row.values():
            newrows.append(x)
        if newrows not in test:
            newtable.append(newrows)
            test = test + [newrows]
    return newtable



def partition(table, columns):
    """Partition the given table into a list containing one table per
    corresponding values in the grouping columns.
    
    Args:
        table: the table to partition
        columns: the columns to partition the table on
    """

    newlist = []
    if columns == None:
        return [table]
    else:
        if table.row_count() == 0:
            return newlist
        key = []
        for row in table:
            trow = []
            for col in columns:
                trow.append(row[col])
            if trow not in key:
                key.append(trow)
        for x in range(len(key)):
            newtable = DataTable(columns)
            for row in table:
                nrow = []
                for col in columns:
                    nrow.append(row[col])
                if key[x] == nrow:
                    newtable.append(nrow)
            newlist.append(newtable)
        return newlist




def summary_stat(table, column, function):
    """Return the result of applying the given function to a list of
    non-empty column values in the given table.

    Args:
        table: the table to compute summary stats over
        column: the column in the table to compute the statistic
        function: the function to compute the summary statistic

    Notes: 
        The given function must take a list of values, return a single
        value, and ignore empty values (denoted by the empty string)

    """

    values = []
    for row in table:
        if row[column] != '':
            values.append(row[column])
    val = function(values)
    return val



def replace_missing(table, column, partition_columns, function): 
    """Replace missing values in a given table's column using the provided
     function over similar instances, where similar instances are
     those with the same values for the given partition columns.

    Args:
        table: the table to replace missing values for
        column: the column whose missing values are to be replaced
        partition_columns: for finding similar values
        function: function that selects value to use for missing value

    Notes: 
        Assumes there is at least one instance with a non-empty value
        in each partition

    """

    key = []
    for row in table:
        if row[column] == '':
            list = []
            for col in partition_columns:
                list.append(row[col])
            if list not in key:
                key.append(list)

    statvals = []
    for x in range(len(key)):
        values = []
        for row in table:
            if row[column] != '':
                test = []
                for col in partition_columns:
                    test.append(row[col])
                if test == key[x]:
                    values.append(row[column])
        stat = function(values)
        if stat != None:
            stat = int(stat)
            stat.__trunc__
        statvals.append(stat)
            
    newtable = DataTable(table.columns())
    for row in table:
        list = []
        if row[column] != '':
            for col in table.columns():
                list.append(row[col])
            newtable.append(list)
        else:
            test = []
            for col in partition_columns:
                test.append(row[col])
            for x in range(len(key)):
                if test == key[x]:
                    for col in table.columns():
                        if col == column:
                            list.append(statvals[x])
                        else:
                            list.append(row[col])
            newtable.append(list)
    return newtable



def summary_stat_by_column(table, partition_column, stat_column, function):
    """Returns for each partition column value the result of the statistic
    function over the given statistics column.

    Args:
        table: the table for computing the result
        partition_column: the column used to create groups from
        stat_column: the column to compute the statistic over
        function: the statistic function to apply to the stat column

    Notes:
        Returns a list of the groups and a list of the corresponding
        statistic for that group.

    """

    pcolumn = []
    test = []
    scolumn = []
    n = 0
    for row in table:
        if len(pcolumn) == len(scolumn) and n == 1:
            pcolumn = []
            scolumn = []
        pcolumn.append(row[partition_column])
        test.append(row[stat_column])
        x = function(test)
        scolumn.append(x)
        n = n + 1
    return pcolumn, scolumn
        




def frequencies(table, partition_column):
    """Returns for each partition column value the number of instances
    having that value.

    Args:
        table: the table for computing the result
        partition_column: the column used to create groups

    Notes:

        Returns a list of the groups and a list of the corresponding
        instance count for that group.

    """

    univals = []
    freqvals = []
    for row in table:
        if row[partition_column] in univals:
            for x in range(len(univals)):
                if univals[x] == row[partition_column]:
                    freqvals[x] = freqvals[x] + 1
        else:
            univals.append(row[partition_column])
            freqvals.append(1)
    return univals, freqvals



def dot_chart(xvalues, xlabel, title, filename=None):
    """Create a dot chart from given values.
    
    Args:
        xvalues: The values to display
        xlabel: The label of the x axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    # reset figure
    plt.figure()
    # dummy y values
    yvalues = [1] * len(xvalues)
    # create an x-axis grid
    plt.grid(axis='x', color='0.85', zorder=0)
    # create the dot chart (with pcts)
    plt.plot(xvalues, yvalues, 'b.', alpha=0.2, markersize=16, zorder=3)
    # get rid of the y axis
    plt.gca().get_yaxis().set_visible(False)
    # assign the axis labels and title
    plt.xlabel(xlabel)
    plt.title(title)
    # save as file or just show
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    # close the plot
    plt.close()



def pie_chart(values, labels, title, filename=None):
    """Create a pie chart from given values.
    
    Args:
        values: The values to display
        labels: The label to use for each value
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    plt.figure()
    plt.pie(values, labels = labels,)
    plt.legend(title = title)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()



def bar_chart(bar_values, bar_names, xlabel, ylabel, title, filename=None):
    """Create a bar chart from given values.
    
    Args:
        bar_values: The values used for each bar
        bar_labels: The label for each bar value
        xlabel: The label of the x-axis
        ylabel: The label of the y-axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    plt.figure()
    plt.bar(bar_names, bar_values)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()



def scatter_plot(xvalues, yvalues, xlabel, ylabel, title, filename=None):
    """Create a scatter plot from given values.
    
    Args:
        xvalues: The x values to plot
        yvalues: The y values to plot
        xlabel: The label of the x-axis
        ylabel: The label of the y-axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    plt.figure()
    plt.scatter(xvalues, yvalues)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()



def box_plot(distributions, labels, xlabel, ylabel, title, filename=None):
    """Create a box and whisker plot from given values.
    
    Args:
        distributions: The distribution for each box
        labels: The label of each corresponding box
        xlabel: The label of the x-axis
        ylabel: The label of the y-axis
        title: The title of the chart
        filename: Filename to save chart to (in SVG format)

    Notes:
        If filename is given, chart is saved and not displayed.

    """

    plt.figure()
    plt.boxplot(distributions)
    ax = plt.subplot()
    ax.set_xticklabels(labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if filename:
        plt.savefig(filename, format='svg')
    else:
        plt.show()
    plt.close()