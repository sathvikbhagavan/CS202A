from sudoku_pair_solver import *
import argparse
import numpy
import pandas as pd
import time

start_time = time.time()
ap = argparse.ArgumentParser()
ap.add_argument('-k', '--kdim', required=True, help='Value of k')
ap.add_argument('-f', '--file', required=True, help='CSV file')
ap.add_argument('-o', '--output_file', required=False, help='Name of the csv file to dump the results' )
args = vars(ap.parse_args())

kdim = int(args['kdim'])
df = pd.read_csv(args['file'], header=None)
file_name = args['output_file']

grid_1 = df.iloc[0:kdim**2, :].to_numpy()
grid_1 = grid_1.reshape(kdim**2, kdim**2).tolist()


grid_2 = df.iloc[kdim**2:, :].values
grid_2 = grid_2.reshape(kdim**2, kdim**2).tolist()

solver = Solver(kdim, grid_1, grid_2, file_name)
solver.get_clauses()
is_sol = solver.solve()
if not is_sol:
    print(None)
else:
    solver.print_solution()
    if file_name is not None:
        solver.print_solution_to_csv()
    solver.validate()
end_time = time.time()
print(f'Time taken: {end_time-start_time}')