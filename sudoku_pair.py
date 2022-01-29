from sudoku_pair_solver import *
import argparse
import numpy
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument('-k', '--kdim', help='Value of k')
ap.add_argument('-f', '--file', help='CSV file')
args = vars(ap.parse_args())

kdim = int(args['kdim'])
df = pd.read_csv(args['file'], header=None)

grid_1 = df.iloc[0:kdim**2, :].to_numpy()
grid_1 = grid_1.reshape(kdim**2, kdim**2).tolist()


grid_2 = df.iloc[kdim**2:, :].values
grid_2 = grid_2.reshape(kdim**2, kdim**2).tolist()

solver = Solver(kdim, grid_1, grid_2)
solver.get_clauses()
solver.solve()
solver.print_solution()