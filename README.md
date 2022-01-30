# CS202A

There are some prerequisites for running this code.

numpy, pandas, pysat

Our versions:

numpy 1.22.1
pandas 1.4.0
python-sat 0.1.7


Q1. For running the script, there are two command line arguments required:

-k or --kdim: The value of k
-f or --file: The location of the csv file

-o or --output_file: Optional, The location of the csv file to dump the output

Example run will be:

python3 sudoku_pair.py -k 3 -f test/test_1.csv


Q2. For running the script, there are two command line arguments required:

-k or --kdim: The value of k

-o or --output_file: Optional, The location of the csv file to dump the output

Example run will be

python3 generate_solutions.py -k 2 -o solution_1.csv