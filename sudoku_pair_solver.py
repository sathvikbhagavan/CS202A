from pysat.solvers import Minisat22
import copy
import itertools
import numpy as np
import pandas as pd

class Solver:
    def __init__(self, kdim, grid_1, grid_2, file_name=None):
        self.kdim = kdim
        self.grid_1 = grid_1
        self.grid_2 = grid_2
        self.clauses_1 = []
        self.clauses = []
        self.clauses_2 = []
        self.clauses_ = None
        self.solver = None
        self.solution = None
        self.solution_1 = copy.deepcopy(self.grid_1)
        self.solution_2 = copy.deepcopy(self.grid_2)
        self.file_name = file_name
    
    def encode(self, g, i, j, k):
        return (self.kdim**6)*g + (self.kdim**4)*(i-1) + (self.kdim**2)*(j-1) + k
    
    def decode(self, i):
        i -= 1
        num = i%(self.kdim**6)
        x = num//(self.kdim**4)
        num = num % (self.kdim**4)
        y = num//(self.kdim**2)
        num = num % (self.kdim**2)
        return x, y, num+1

    def get_subgrid(self, i, j):
        return [(i-1)//self.kdim, (j-1)//self.kdim]

    
    def get_individual_clauses(self, g):
        clauses = []

        # Each cell has atleast one number
        individual_clauses_1 = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                individual_clause = []
                for k in range(1, self.kdim**2+1):
                    individual_clause.append(self.encode(g, i, j, k))
                clauses.append(individual_clause)

        
        # Each cell has atmost one number
        individual_clauses_2 = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for k1 in range(1, self.kdim**2+1):
                    for k2 in range(k1+1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k1), -1*self.encode(g, i, j, k2)])
        

        # Each row has every number
        row_clauses = []
        for j in range(1, self.kdim**2+1):
            for i in range(1, self.kdim**2+1):
                for i2 in range(i+1, self.kdim**2+1):
                    for k in range(1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i2, j, k)])
        

        # Each column has every number
        col_clauses = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for j2  in range(j+1, self.kdim**2+1):
                    for k in range(1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i, j2, k)])


        # Subgrids
        subgrid_clauses = []
        for r in range(self.kdim):
            for s in range(self.kdim):
                for k in range(1, self.kdim**2+1):
                    subgrid_clause = []
                    for i in range(1, self.kdim+1):
                        for j in range(1, self.kdim+1):
                            subgrid_clause.append(self.encode(g, self.kdim*r+i, self.kdim*s+j, k))
                    clauses.append(subgrid_clause)
        
        return clauses


    def get_inter_clauses(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for k in range(1, self.kdim**2+1):
                    self.clauses.append([-1*self.encode(0, i, j, k), -1*self.encode(1, i, j, k)])


    
    def get_fixed_clauses(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                if self.grid_1[i-1][j-1] != 0:
                    self.clauses.append([self.encode(0, i, j, self.grid_1[i-1][j-1])])
                if self.grid_2[i-1][j-1] != 0:
                    self.clauses.append([self.encode(1, i, j, self.grid_2[i-1][j-1])])

    def get_clauses(self):

        self.clauses_1 = self.get_individual_clauses(0)
        self.clauses_2 = self.get_individual_clauses(1)
        self.clauses = self.clauses_1 + self.clauses_2
        self.get_inter_clauses()
        self.clauses_= copy.deepcopy(self.clauses)

        self.get_fixed_clauses()
    
    def get_clauses_updated(self):

        self.clauses = copy.deepcopy(self.clauses_)
        self.get_fixed_clauses()
        self.add_solution_clauses()

    def solve(self):
        
        self.solver = Minisat22(use_timer=True, bootstrap_with=self.clauses)
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


    def print_grid(self):

        print('Grid 1: ')
        print('-*-'*self.kdim**2)
        for k in self.grid_1:
            print(k)
        print('-*-'*self.kdim**2)
        print()
        print('Grid 2: ')
        print('-*-'*self.kdim**2)
        for k in self.grid_2:
            print(k)
        print('-*-'*self.kdim**2)
        

    def print_solution(self):
        
        print('Solution of grid 1: ')
        print('-*-'*self.kdim**2)
        for k in self.solution_1:
            print(k)
        print('-*-'*self.kdim**2)
        print()
        print('Solution of grid 2: ')
        print('-*-'*self.kdim**2)
        for k in self.solution_2:
            print(k)
        print('-*-'*self.kdim**2)

    def add_solution_clauses(self):

        sol_clause = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                sol_clause.append(-1*self.encode(0, i, j, self.solution_1[i-1][j-1]))
                sol_clause.append(-1*self.encode(1, i, j, self.solution_2[i-1][j-1]))

        self.clauses.append(sol_clause)

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

    def set_grid(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                self.grid_1[i-1][j-1] = self.solution_1[i-1][j-1]
                self.grid_2[i-1][j-1] = self.solution_2[i-1][j-1]

    def validate(self):

        first = self._validate(0)
        second = self._validate(1)
        p_1 = 'Solution 1 is correct' if first else 'Solution 1 is wrong'
        p_2 = 'Solution 2 is correct' if second else 'Solution 2 is wrong'
        print(p_1)
        print(p_2)
        print('-'*50)

    def print_grid_to_csv(self):

        combined = np.concatenate((np.array(self.grid_1), np.array(self.grid_2)), axis=0)
        pd.DataFrame(combined).to_csv(f'{self.file_name}', header=None, index=None, line_terminator='\n')
    
    def print_solution_to_csv(self):

        combined = np.concatenate((np.array(self.solution_1), np.array(self.solution_2)), axis=0)
        pd.DataFrame(combined).to_csv(f'{self.file_name}', header=None, index=None, line_terminator='\n')


