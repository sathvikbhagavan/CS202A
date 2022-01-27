from pysat.solvers import Minisat22
import copy

class Clauses:
    def __init__(self, kdim, grid_1, grid_2):
        self.kdim = kdim
        self.grid_1 = grid_1
        self.grid_2 = grid_2
        self.clauses_1 = []
        self.clauses = []
        self.clauses_2 = []

    
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
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                clauses.append([self.encode(g, i, j, k) for k in range(1, self.kdim**2+1)])
                for k1 in range(1, self.kdim**2+1):
                    for k2 in range(k1+1, self.kdim**2+1):
                        clauses.append([-1*self.encode(g, i, j, k1), -1*self.encode(g, i, j, k2)])

        
        row_clauses = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for i2  in range(1, self.kdim**2+1):
                    if i != i2:
                        for k in range(1, self.kdim**2+1):
                            row_clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i2, j, k)])
        
        row_clauses = list(set([tuple(sorted(i)) for i in row_clauses]))
        row_clauses = [list(i) for i in row_clauses]
        clauses += row_clauses


        col_clauses = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for j2  in range(1, self.kdim**2+1):
                    if j != j2:
                        for k in range(1, self.kdim**2+1):
                            col_clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, i, j2, k)])
                
        col_clauses = list(set([tuple(sorted(i)) for i in col_clauses]))
        col_clauses = [list(i) for i in col_clauses]
        clauses += col_clauses


        subgrid_clauses = []
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                x, y  = self.get_subgrid(i, j)
                for p in range(self.kdim*x+1, self.kdim*x+self.kdim+1):
                    for q in range(self.kdim*y+1, self.kdim*y+self.kdim+1):
                        if p != i or q != j:
                            for k in range(1, self.kdim**2+1):
                                subgrid_clauses.append([-1*self.encode(g, i, j, k), -1*self.encode(g, p, q, k)])
        
        
        subgrid_clauses = list(set([tuple(sorted(i)) for i in subgrid_clauses]))
        subgrid_clauses = [list(i) for i in subgrid_clauses]
        clauses += subgrid_clauses
        return clauses


    def get_inter_clauses(self):

        self.clauses = self.clauses_1 + self.clauses_2
        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                for k in range(1, self.kdim**2+1):
                    self.clauses.append([-1*self.encode(0, i, j, k), -1*self.encode(1, i, j, k)])


    
    def get_fixed_clauses(self):

        for i in range(1, self.kdim**2+1):
            for j in range(1, self.kdim**2+1):
                if self.grid_1[i-1][j-1] != 0:
                    self.clauses_1.append([self.encode(0, i, j, self.grid_1[i-1][j-1])])
                if self.grid_2[i-1][j-1] != 0:
                    self.clauses_2.append([self.encode(1, i, j, self.grid_2[i-1][j-1])])

    def get_clauses(self):

        self.clauses_1 = self.get_individual_clauses(0)
        self.clauses_2 = self.get_individual_clauses(1)
        self.get_fixed_clauses()
        self.get_inter_clauses()
        return self.clauses



class Solver(Clauses):
    def __init__(self, kdim, grid_1, grid_2):
        super().__init__(kdim, grid_1, grid_2)
        self.get_clauses()
        self.solver = Minisat22(bootstrap_with=self.clauses)
        self.solution = None
        self.solution_1 = copy.deepcopy(self.grid_1)
        self.solution_2 = copy.deepcopy(self.grid_2)

    def solve(self):
        self.solver.solve()
        self.solution = self.solver.get_model()
        for i in self.solution:
            if i > 0 and i <= (self.kdim**6):
                x, y, num = self.decode(i)
                self.solution_1[x][y] = num
            elif i > 0 and i > (self.kdim**6):
                x, y, num = self.decode(i)
                self.solution_2[x][y] = num

    def print_solution(self):
        
        for k in self.solution_1:
            print(k)

        print('--------------------------------')

        for k in self.solution_2:
            print(k)

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

    def validate(self):

        first = self._validate(0)
        second = self._validate(1)

        if first:
            print('First solution is correct')
        else:
            print('First solution is wrong')

        if second:
            print('Second solution is correct')
        else:
            print('Second solution is wrong')