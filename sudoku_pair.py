from pysat.solvers import Minisat22
import argparse
import numpy
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument('-k', '--kdim', help='Value of k')
ap.add_argument('-f', '--file', help='CSV file')
args = vars(ap.parse_args())

kdim = int(args['kdim'])
df = pd.read_csv(args['file'], header=None)


def encode(g, i, j, k):
    return (kdim**6)*g + (kdim**4)*(i-1) + (kdim**2)*(j-1) + k

def decode(i):
    i -= 1
    num = i%(kdim**6)
    x = num//(kdim**4)
    num = num % (kdim**4)
    y = num//(kdim**2)
    num = num % (kdim**2)
    return x, y, num+1

def get_subgrid(i, j):
    return [(i-1)//kdim, (j-1)//kdim]


def get_clauses(g):
    clauses = []
    for i in range(1, kdim**2+1):
        for j in range(1, kdim**2+1):
            clauses.append([encode(g, i, j, k) for k in range(1, kdim**2+1)])
            for k1 in range(1, kdim**2+1):
                for k2 in range(k1+1, kdim**2+1):
                    clauses.append([-1*encode(g, i, j, k1), -1*encode(g, i, j, k2)])

    
    row_clauses = []
    for i in range(1, kdim**2+1):
        for j in range(1, kdim**2+1):
            for i2  in range(1, kdim**2+1):
                if i != i2:
                    for k in range(1, kdim**2+1):
                        row_clauses.append([-1*encode(g, i, j, k), -1*encode(g, i2, j, k)])
    
    row_clauses = list(set([tuple(sorted(i)) for i in row_clauses]))
    row_clauses = [list(i) for i in row_clauses]
    clauses += row_clauses


    col_clauses = []
    for i in range(1, kdim**2+1):
        for j in range(1, kdim**2+1):
            for j2  in range(1, kdim**2+1):
                if j != j2:
                    for k in range(1, kdim**2+1):
                        col_clauses.append([-1*encode(g, i, j, k), -1*encode(g, i, j2, k)])
            
    col_clauses = list(set([tuple(sorted(i)) for i in col_clauses]))
    col_clauses = [list(i) for i in col_clauses]
    clauses += col_clauses


    subgrid_clauses = []
    
    for i in range(1, kdim**2+1):
        for j in range(1, kdim**2+1):
            x, y  = get_subgrid(i, j)
            for p in range(kdim*x+1, kdim*x+kdim+1):
                for q in range(kdim*y+1, kdim*y+kdim+1):
                    if p != i or q != j:
                        for k in range(1, kdim**2+1):
                            subgrid_clauses.append([-1*encode(g, i, j, k), -1*encode(g, p, q, k)])
    
    
    subgrid_clauses = list(set([tuple(sorted(i)) for i in subgrid_clauses]))
    subgrid_clauses = [list(i) for i in subgrid_clauses]
    clauses += subgrid_clauses

    return clauses


def get_inter_clauses(clauses_1, clauses_2):

    clauses = clauses_1 + clauses_2
    for i in range(1, kdim**2+1):
        for j in range(1, kdim**2+1):
            for k in range(1, kdim**2+1):
                clauses.append([-1*encode(0, i, j, k), -1*encode(1, i, j, k)])

    return clauses            


def validate(solution):

    # row validation
    for i in range(kdim**2):
        x = [False]*(kdim**2 + 1)
        for j in range(kdim**2):
            if solution[i][j] == 0:
                return False
            elif not x[solution[i][j]]:
                x[solution[i][j]] = True
            else:
                return False

    
    # column validation
    for i in range(kdim**2):
        x = [False]*(kdim**2 + 1)
        for j in range(kdim**2):
            if solution[j][i] == 0:
                return False
            elif not x[solution[j][i]]:
                x[solution[j][i]] = True
            else:
                return False
    

    # sub grid validation
    for i in range(kdim):
        for j in range(kdim):
            x = [False]*(kdim**2 + 1)
            for p in range(kdim*i, kdim*i+kdim):
                for q in range(kdim*j, kdim*j+kdim):
                    if solution[p][q] == 0:
                        return False
                    elif not x[solution[p][q]]:
                        x[solution[p][q]] = True
                    else:
                        return False
    
    return True



clauses_1 = get_clauses(0)
clauses_2 = get_clauses(1)

grid_1 = df.iloc[0:kdim**4, 0].values
grid_1 = grid_1.reshape(kdim**2, kdim**2).tolist()


grid_2 = df.iloc[kdim**4:, 0].values
grid_2 = grid_2.reshape(kdim**2, kdim**2).tolist()


for i in range(1, kdim**2+1):
    for j in range(1, kdim**2+1):
        if grid_1[i-1][j-1] != 0:
            clauses_1.append([encode(0, i, j, grid_1[i-1][j-1])])
        if grid_2[i-1][j-1] != 0:
            clauses_2.append([encode(1, i, j, grid_2[i-1][j-1])])
        


clauses = get_inter_clauses(clauses_1, clauses_2)
m = Minisat22(bootstrap_with=clauses)
m.solve()
sol = m.get_model()

solution_1 = grid_1.copy()
solution_2 = grid_2.copy()


for i in m.get_model():
    if i > 0 and i <= (kdim**6):
        x, y, num = decode(i)
        solution_1[x][y] = num
    elif i > 0 and i > (kdim**6):
        x, y, num = decode(i)
        solution_2[x][y] = num


print(validate(solution_1))
print(validate(solution_2))

for k in solution_1:
    print(k)

print('--------------------------------')

for k in solution_2:
    print(k)