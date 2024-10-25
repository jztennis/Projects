"""
HW-2 Data Table implementation.

NAME: Jared Zaugg
DATE: Fall 2023
CLASS: CPSC 322

"""

import csv
import tabulate


class DataRow:
    """A basic representation of a relational table row. The row maintains
    its corresponding column information.
    """
    
    #constructor
    def __init__(self, columns=[], values=[]):
        """Create a row from a list of column names and data values.
           
        Args:
            columns: A list of column names for the row
            values: A list of the corresponding column values.

        Notes: 
            The column names cannot contain duplicates.
            There must be one value for each column.
        """

        if len(columns) != len(set(columns)): # check
            raise ValueError('duplicate column names')
        if len(columns) != len(values): # check
            raise ValueError('mismatched number of columns and values')
        self.__columns = columns.copy()
        self.__values = values.copy()

    # print
    def __repr__(self):
        """Returns a string representation of the data row (formatted as a
        table with one row).

        Notes: 
            Uses the tabulate library to pretty-print the row.
        """
        return tabulate.tabulate([self.values()], headers=self.columns())

    
    # get column
    def __getitem__(self, column):
        """Returns the value of the given column name.
        
        Args:
            column: The name of the column.
        """

        if column not in self.columns(): # check
            raise IndexError('bad column name')
        return self.values()[self.columns().index(column)]

    # set value
    def __setitem__(self, column, value):
        """Modify the value for a given row column.
        
        Args: 
            column: The column name.
            value: The new value.
        """

        if column not in self.columns(): # check
            raise IndexError('bad column name')
        self.__values[self.columns().index(column)] = value

    # del value in column
    def __delitem__(self, column):
        """Removes the given column and corresponding value from the row.

        Args:
            column: The column name.
        """

        if column not in self.columns(): # check
            raise IndexError('bad column name')
        else:
            copy1 = []
            copy2 = []
            for x in range(0, len(self.columns())):
                if self.columns()[x] != column:
                    copy1.append(self.columns()[x])
                    copy2.append(self.values()[x])
            self.__columns = copy1
            self.__values = copy2

    
    # ==
    def __eq__(self, other):
        """Returns true if this data row and other data row are equal.

        Args:
            other: The other row to compare this row to.

        Notes:
            Checks that the rows have the same columns and values.
        """

        if not isinstance(other, DataRow):
            if self.columns() == [] and other == []:
                return True
            elif (self.columns() != [] and other == []) or (self.columns() == [] and other != []):
                return False
            for x in range(0, len(self.columns())):
                if self.values()[x] != other[x]: # check
                    raise ValueError("not equivalent")
        else:
            for x in range(0, len(self.columns())):
                if self.columns()[x] != other.columns()[x]: # check
                    raise ValueError("not equivalent")
                elif self.values()[x] != other.values()[x]:
                    return False
        return True


    # +
    def __add__(self, other):
        """Combines the current row with another row into a new row.
        
        Args:
            other: The other row being combined with this one.

        Notes:
            The current and other row cannot share column names.
        """

        if not isinstance(other, DataRow):
            raise ValueError('expecting DataRow object') # check
        if len(set(self.columns()).intersection(other.columns())) != 0:
            raise ValueError('overlapping column names') # check
        return DataRow(self.columns() + other.columns(),
                       self.values() + other.values())


    # copy of columns
    def columns(self):
        """Returns a list of the columns of the row."""
        return self.__columns.copy()


    # returns values of selected columns
    def values(self, columns=None):
        """Returns a list of the values for the selected columns in the order
        of the column names given.
           
        Args:
            columns: The column values of the row to return. 

        Notes:
            If no columns given, all column values returned.
        """

        if columns is None:
            return self.__values.copy()
        if not set(columns) <= set(self.columns()): # check
            raise ValueError('duplicate column names')
        return [self[column] for column in columns]


    # new data row for certain columns
    def select(self, columns=None):
        """Returns a new data row for the selected columns in the order of the
        column names given.

        Args:
            columns: The column values of the row to include.
        
        Notes:
            If no columns given, all column values included.
        """

        newColumns = []
        newValues = []
        newDataRow = DataRow()
        if columns == None: # copy of columns
            for x in range(0, len(self.columns())):
                newColumns.append(self.columns()[x])
                newValues.append(self.values()[x])
            newDataRow.__columns = newColumns
            newDataRow.__values = newValues
            return newDataRow
        else: # new data row for selected columns
            if self.columns() == [] and self.values() == []: # check
                raise ValueError("DataRow doesn't exist")
            for y in range(0, len(columns)):
                for x in range(0, len(self.columns())):
                    if self.columns()[x] == columns[y]:
                        newColumns.append(self.columns()[x])
                        newValues.append(self.values()[x])
            if newColumns == [] and newValues == []: # check
                raise ValueError("column doesn't exist")
            newDataRow.__columns = newColumns
            newDataRow.__values = newValues
            return newDataRow

    
    # copy of data row
    def copy(self):
        """Returns a copy of the data row."""
        return self.select()

    

class DataTable:
    """A relational table consisting of rows and columns of data.

    Note that data values loaded from a CSV file are automatically
    converted to numeric values.
    """
    # constructor
    def __init__(self, columns=[]):
        """Create a new data table with the given column names

        Args:
            columns: A list of column names. 

        Notes:
            Requires unique set of column names. 
        """

        if len(columns) != len(set(columns)): # check
            raise ValueError('duplicate column names')
        self.__columns = columns.copy()
        self.__row_data = []


    # print
    def __repr__(self):
        """Return a string representation of the table.
        
        Notes:
            Uses tabulate to pretty print the table.
        """

        table = []
        table.append(self.columns())
        for row in self.__row_data:
            table.append(row.values())
        return tabulate.tabulate(table, headers = 'firstrow')

    
    # returns a specified row
    def __getitem__(self, row_index):
        """Returns the row at row_index of the data table.
        
        Notes:
            Makes data tables iterable over their rows.
        """
        return self.__row_data[row_index]


    # del specified row
    def __delitem__(self, row_index):
        """Deletes the row at row_index of the data table.
        """

        if len(self.__row_data) <= row_index: # check
            raise IndexError("that row doesn't exist")
        newData = []
        for x in range(0, len(self.__row_data)):
            if x != row_index:
                newData.append(self.__row_data[x])
        self.__row_data = newData


    # load rows from a file
    def load(self, filename, delimiter=','):
        """Add rows from given filename with the given column delimiter.

        Args:
            filename: The name of the file to load data from
            delimeter: The column delimiter to use

        Notes:
            Assumes that the header is not part of the given csv file.
            Converts string values to numeric data as appropriate.
            All file rows must have all columns.
        """

        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            num_cols = len(self.columns())
            for row in reader:
                row_cols = len(row)                
                if num_cols != row_cols: # check
                    raise ValueError(f'expecting {num_cols}, found {row_cols}')
                converted_row = []
                for value in row:
                    converted_row.append(DataTable.convert_numeric(value.strip()))
                self.__row_data.append(DataRow(self.columns(), converted_row))


    # save table to file            
    def save(self, filename, delimiter=','):
        """Saves the current table to the given file.
        
        Args:
            filename: The name of the file to write to.
            delimiter: The column delimiter to use. 

        Notes:
            File is overwritten if already exists. 
            Table header not included in file output.
        """

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter, quotechar='"',
                                quoting=csv.QUOTE_NONNUMERIC)
            for row in self.__row_data:
                writer.writerow(row.values())


    # return num. of columns
    def column_count(self):
        """Returns the number of columns in the data table."""
        return len(self.__columns)


    # return # of rows
    def row_count(self):
        """Returns the number of rows in the data table."""
        return len(self.__row_data)


    # copy of columns
    def columns(self):
        """Returns a list of the column names of the data table."""
        return self.__columns.copy()


    # add row to table
    def append(self, row_values):
        """Adds a new row to the end of the current table. 

        Args:
            row_data: The row to add as a list of values.
        
        Notes:
            The row must have one value per column. 
        """

        newRow = DataRow(self.columns(), row_values)
        self.__row_data.append(newRow)



    # new table w/specified rows
    def rows(self, row_indexes):
        """Returns a new data table with the given list of row indexes. 

        Args:
            row_indexes: A list of row indexes to copy into new table.
        
        Notes: 
            New data table has the same column names as current table.
        """

        for x in range(len(row_indexes)):
            if len(self.__row_data) <= row_indexes[x]: # check
                raise IndexError("row index doesn't exist")
        newDataTable = DataTable(self.columns())
        for y in range(len(row_indexes)):
            for x in range(len(self.__row_data)):
                if x == row_indexes[y]:
                    newDataRow = DataRow(self.columns(), self.__row_data[x].values())
                    newDataTable.__row_data.append(newDataRow)
        return newDataTable
        


    # copy of table
    def copy(self):
        """Returns a copy of the current table."""
        table = DataTable(self.columns())
        for row in self:
            table.append(row.values())
        return table
    

    # updates a value in the table
    def update(self, row_index, column, new_value):
        """Changes a column value in a specific row of the current table.

        Args:
            row_index: The index of the row to update.
            column: The name of the column whose value is being updated.
            new_value: The row's new value of the column.

        Notes:
            The row index and column name must be valid. 
        """

        self.__row_data[row_index][column] = new_value


    # combines 2 tables
    @staticmethod
    def combine(table1, table2, columns=[], non_matches=False):
        """Returns a new data table holding the result of combining table 1 and 2.

        Args:
            table1: First data table to be combined.
            table2: Second data table to be combined.
            columns: List of column names to combine on.
            nonmatches: Include non matches in answer.

        Notes:
            If columns to combine on are empty, performs all combinations.
            Column names to combine are must be in both tables.
            Duplicate column names removed from table2 portion of result.
        """

        if len(columns) != len(set(columns)): # check
            raise IndexError('repeat column names')
        for a in columns:
            if a not in table1.columns() or a not in table2.columns(): # check
                raise IndexError('column to combine is not in one of the tables')
            
        # initialize
        newDataTable = DataTable()
        newColumns = []

        # get new table's columns
        for x in range(len(table1.columns())):
            newColumns.append(table1.columns()[x])
        for y in range(len(table2.columns())):
            if table2.columns()[y] not in newColumns:
                newColumns.append(table2.columns()[y])
        newDataTable.__columns = newColumns

        # get new table's values
        for r1 in table1:
            n = 1
            if non_matches == False: # only matches
                for r2 in table2:
                    matching = all(r1[column] == r2[column] for column in columns)
                    if matching == True:
                        new_row = [r1[column] if column in table1.columns() else r2[column] for column in newColumns]
                        newDataTable.__row_data.append(DataRow(newColumns, new_row))
                    n = n + 1
            else: # if match, combine. if not match, ''
                test = False
                for r2 in table2:
                    matching = all(r1[column] == r2[column] for column in columns)

                    # matches
                    if matching == True:
                        test = True
                        new_row = [r1[column] if column in table1.columns() else r2[column] for column in newColumns]
                        newDataTable.__row_data.append(DataRow(newColumns, new_row))

                # no match adds from table1
                if test == False:
                    new_row = []
                    for column in newColumns:
                        if column in table1.columns():
                            new_row = new_row + [r1[column]]
                        else:
                            new_row = new_row + ['']
                    newDataTable.__row_data.append(DataRow(newColumns, new_row))

        # missed values in table2
        if non_matches == True:
            for r2 in table2:
                test = False
                n = 1
                for r1 in table1:
                    matching = all(r1[column] == r2[column] for column in columns)

                    # if match, log that this table2 row has a match
                    if matching == True:
                        test = True

                    # if no match and it's compared all the rows in table1, add the table2 row
                    elif n == len(table1.__row_data) and test == False:
                        new_row = []
                        for column in newColumns:
                            if column in table2.columns():
                                new_row = new_row + [r2[column]]
                            else:
                                new_row = new_row + ['']
                        newDataTable.__row_data.append(DataRow(newColumns, new_row))
                    n = n + 1
        return newDataTable


    # converts to int (e.g. '4' to 4)
    @staticmethod
    def convert_numeric(value):
        """Returns a version of value as its corresponding numeric (int or
        float) type as appropriate.

        Args:
            value: The string value to convert

        Notes:
            If value is not a string, the value is returned.
            If value cannot be converted to int or float, it is returned.
         """
        
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return str(value)
            

            
    def drop(self, columns):
        """Removes the given columns from the current table.

        Args:
            column: the name of the columns to drop
        """
        
        subDataTable = DataTable()
        newColumns = []
        for col in self.columns():
            if col not in columns:
                newColumns.append(col)
        subDataTable.__columns = newColumns
        for row in self:
            newValues = []
            for col in newColumns:
                newValues.append(row[col])
            newrow = DataRow(newColumns, newValues)
            subDataTable.__row_data.append(newrow)
        self.__columns = subDataTable.__columns
        self.__row_data = subDataTable.__row_data