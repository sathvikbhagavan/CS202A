from pysat.solvers import Minisat22
import copy
import numpy as np
import pandas as pd

class Solver:
    """
    This is a class used for solving sudoku pair using sat solver(Minisat22)

    Attributes:
        k (int) - size of the subgrid in the sudoku
        grid_1 (list of list) - first sudoku
        grid_2 (list of list) - second sudoku
        clauses_1 (list of list) - clauses for the first sudoku
        clauses_2 (list of list) - clauses for the second sudoku
        clauses (list of list) - clauses for the sudoku pair
        solver (Minisat object) - sat solver used for solving the sudoku pair
        solution (list) - solution returned by the sat solver
        solution_1 (list of list) - solution of first sudoku which can used for printing on screen 
                                    or write to a csv file 
        solution_2 (list of list) - solution of second sudoku which can used for printing on screen 
                                    or write to a csv file
        filename (str) - name of the csv file for writing the solution
    """

    def __init__(self, kdim, grid_1, grid_2, file_name=None):
        self.kdim = kdim
        self.grid_1 = grid_1
        self.grid_2 = grid_2
        self.clauses_1 = []
        self.clauses = []
        self.clauses_2 = []
        self.solver = None
        self.solution = None
        self.solution_1 = copy.deepcopy(self.grid_1)
        self.solution_2 = copy.deepcopy(self.grid_2)
        self.file_name = file_name
    

    # Encoding the position in the sudoku to a number
    def encode(self, g, i, j, k):
        return (self.kdim**6)*g + (self.kdim**4)*(i-1) + (self.kdim**2)*(j-1) + k
    

    # Decoding the position in the sudoku to a number
    def decode(self, i):
        i -= 1
        num = i%(self.kdim**6)
        x = num//(self.kdim**4)
        num = num % (self.kdim**4)
        y = num//(self.kdim**2)
        num = num % (self.kdim**2)
        return x, y, num+1


    # Method to get the subgrid a cell belongs to
    def get_subgrid(self, i, j):
        return [(i-1)//self.kdim, (j-1)//self.kdim]

    
    # Get clauses for one sudoku
    def get_individual_clauses(self, g):
        clauses = []

        # Each cell has atleast one number
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                individual_clause = []
                for k in range(1, self.kdim**2+1):
                    individual_clause.append(self.encode(g, i, j, k))
                clauses.append(individual_clause)

        
        # Each cell has atmost one number
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for k1 in range(1, self.kdim**2+1):
                    for k2 in range(k1+1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k1), -1*self.encode(g, i, j, k2)])
        

        # Each row has every number
        for j in range(1, self.kdim**2+1):
            for i in range(1, self.kdim**2+1):
                for i2 in range(i+1, self.kdim**2+1):
                    for k in range(1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i2, j, k)])
        
        
        # Each column has every number
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for j2  in range(j+1, self.kdim**2+1):
                    for k in range(1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i, j2, k)])

        # Subgrids
        for r in range(self.kdim):
            for s in range(self.kdim):
                for k in range(1, self.kdim**2+1):
                    subgrid_clause = []
                    for i in range(1, self.kdim+1):
                        for j in range(1, self.kdim+1):
                            subgrid_clause.append(self.encode(g, self.kdim*r+i, self.kdim*s+j, k))
                    clauses.append(subgrid_clause)
        
        return clauses


    # Clauses for the constraints between two sudokus
    def get_inter_clauses(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for k in range(1, self.kdim**2+1):
                    self.clauses.append([-1*self.encode(0, i, j, k), -1*self.encode(1, i, j, k)])


    # Clauses for numbers fixed in the sudoku
    def get_fixed_clauses(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                if self.grid_1[i-1][j-1] != 0:
                    self.clauses.append([self.encode(0, i, j, self.grid_1[i-1][j-1])])
                if self.grid_2[i-1][j-1] != 0:
                    self.clauses.append([self.encode(1, i, j, self.grid_2[i-1][j-1])])


    # Method to collect all clauses
    def get_clauses(self):

        self.clauses_1 = self.get_individual_clauses(0)
        self.clauses_2 = self.get_individual_clauses(1)
        self.clauses = self.clauses_1 + self.clauses_2
        self.get_inter_clauses()
        self.get_fixed_clauses()
    

    # Method to update clauses (required for generation)
    def get_clauses_updated(self, pos_x_1, pos_y_1, prev_1, pos_x_2, pos_y_2, prev_2):
        
        self.clauses.remove([self.encode(0, pos_x_1, pos_y_1, prev_1)])
        self.clauses.remove([self.encode(1, pos_x_2, pos_y_2, prev_2)])


    # Method to solve the sudoku pair
    def solve(self):
        
        with Minisat22(bootstrap_with=self.clauses) as self.solver:
            self.solver.solve()
            self.solution = self.solver.get_model()
            if self.solution is None:
                return False
            for i in self.solution:
                if i > 0 and i <= (self.kdim**6):
                    x, y, num = self.decode(i)
                    self.solution_1[x][y] = num
                elif i > 0 and i > (self.kdim**6):
                    x, y, num = self.decode(i)
                    self.solution_2[x][y] = num
            return True


    # Method to print input grid of sudoku pair
    def print_grid(self):

        print('Grid 1: ')
        print('-'*4*self.kdim**2)
        for k in self.grid_1:
            for j in k:
                if j < 10:
                    print(f' {j} ', end=' ')
                else:
                    print(f' {j}', end=' ')
            print()
        print('-'*4*self.kdim**2)
        print()
        print('Grid 2: ')
        print('-'*4*self.kdim**2)
        for k in self.grid_2:
            for j in k:
                if j < 10:
                    print(f' {j} ', end=' ')
                else:
                    print(f' {j}', end=' ')
            print()
        print('-'*4*self.kdim**2)
        
    
    # Method to print solution of sudoku pair
    def print_solution(self):
        
        print('Solution of grid 1: ')
        print('-'*4*self.kdim**2)
        for k in self.solution_1:
            for j in k:
                if j < 10:
                    print(f' {j} ', end=' ')
                else:
                    print(f' {j}', end=' ')
            print()
        print('-'*4*self.kdim**2)
        print()
        print('Solution of grid 2: ')
        print('-'*4*self.kdim**2)
        for k in self.solution_2:
            for j in k:
                if j < 10:
                    print(f' {j} ', end=' ')
                else:
                    print(f' {j}', end=' ')
            print()
        print('-'*4*self.kdim**2)

    
    # Method to add solution clauses for checking non unique solution
    def add_solution_clauses(self):

        sol_clause = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                sol_clause.append(-1*self.encode(0, i, j, self.solution_1[i-1][j-1]))
                sol_clause.append(-1*self.encode(1, i, j, self.solution_2[i-1][j-1]))

        self.clauses.append(sol_clause)

    
    # Method to check whether the solution is correct or not
    def _validate(self, i):

        solution = self.solution_1 if i == 0 else self.solution_2
        
        for i in range(self.kdim**2):
            x = [False]*(self.kdim**2 + 1)
            for j in range(self.kdim**2):
                if solution[i][j] == 0:
                    return False
                elif not x[solution[i][j]]:
                    x[solution[i][j]] = True
                else:
                    return False

        for i in range(self.kdim**2):
            x = [False]*(self.kdim**2 + 1)
            for j in range(self.kdim**2):
                if solution[j][i] == 0:
                    return False
                elif not x[solution[j][i]]:
                    x[solution[j][i]] = True
                else:
                    return False
        
        for i in range(self.kdim):
            for j in range(self.kdim):
                x = [False]*(self.kdim**2 + 1)
                for p in range(self.kdim*i, self.kdim*i+self.kdim):
                    for q in range(self.kdim*j, self.kdim*j+self.kdim):
                        if solution[p][q] == 0:
                            return False
                        elif not x[solution[p][q]]:
                            x[solution[p][q]] = True
                        else:
                            return False
        
        return True


    def _cross_validate(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                if self.solution_1[i-1][j-1] == self.solution_2[i-1][j-1]:
                    return False
        
        return True
                

    # Method to copy solution into grid (required for generation)
    def set_grid(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                self.grid_1[i-1][j-1] = self.solution_1[i-1][j-1]
                self.grid_2[i-1][j-1] = self.solution_2[i-1][j-1]


    # Method to invoke _validate for both sudokus in the sudoku pair
    def validate(self):

        first = self._validate(0)
        second = self._validate(1)
        cross = self._cross_validate()
        if not cross:
            print('Solutions are wrong!')
        else:
            if first and second:
                print('Solutions are correct!')
            else:
                print('Solutions are wrong!')
        print('-'*4*self.kdim**2)


    # Method to write grids into csv file
    def print_grid_to_csv(self):

        combined = np.concatenate((np.array(self.grid_1), np.array(self.grid_2)), axis=0)
        pd.DataFrame(combined).to_csv(f'{self.file_name}', header=None, index=None, line_terminator='\n')
    

    # Method to write solutions into csv file
    def print_solution_to_csv(self):

        combined = np.concatenate((np.array(self.solution_1), np.array(self.solution_2)), axis=0)
        pd.DataFrame(combined).to_csv(f'{self.file_name}', header=None, index=None, line_terminator='\n')