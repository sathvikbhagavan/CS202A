import argparse
import numpy as np
import time
from sudoku_pair_solver import *

start_time = time.time()
ap = argparse.ArgumentParser()
ap.add_argument('-k', '--kdim', help='Value of k')
args = vars(ap.parse_args())

kdim = int(args['kdim'])

grid_1 = np.zeros((kdim**2, kdim**2)).tolist()
grid_2 = np.zeros((kdim**2, kdim**2)).tolist()

solver = Solver(kdim, grid_1, grid_2)

solver.solve()
solver.print_solution()
solver.validate()
end_time = time.time()
print(end_time-start_time)