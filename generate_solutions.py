from pysat.solvers import Minisat22
import argparse
import numpy as np
import copy 
from sudoku_pair_solver import *


ap = argparse.ArgumentParser()
ap.add_argument('-k', '--kdim', help='Value of k')
args = vars(ap.parse_args())

kdim = int(args['kdim'])

grid_1 = np.zeros((kdim**2, kdim**2)).tolist()
grid_2 = np.zeros((kdim**2, kdim**2)).tolist()

solver = Solver(kdim, grid_1, grid_2)
solver.solve()
solver.print_solution()