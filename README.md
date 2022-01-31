# CS202A Assignment 1

Prerequisite modules for running the code:  numpy, pandas, python-sat

## Our versions:

numpy 1.22.1

pandas 1.4.0

python-sat 0.1.7


## Q1 Sudoku Pair Solver

### For running the script, there are two command line arguments required:

-k or --kdim: The value of k


-f or --file: The location of the csv file


-o or --output_file: Optional, The location of the csv file to dump the output

### Example run will be:

python3 solve_sudoku_pair.py -k 2 -f tests/test_2_1.csv


## Q2 Sudoku Pair Generator

### For running the script, there are two command line arguments required:

-k or --kdim: The value of k

-o or --output_file: The location of the csv file to dump the output

### Example run will be

python3 generate_sudoku_pair.py -k 2 -o tests/test_2_1.csv

## Test cases for Q1

Naming scheme is: test_{k}_{test case number}.csv
