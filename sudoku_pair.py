from pysat.solvers import Minisat22

def get_pos(g, i, j, k):
    # get the numeber as  ijk
    return 1000*g + 100*i + 10*j + k


def get_subgrid(i, j):
    return [(i-1)//3, (j-1)//3]


def get_clauses(g):
    clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            clauses.append([get_pos(g, i, j, k) for k in range(1, 10)])
            for k1 in range(1, 10):
                for k2 in range(k1+1, 10):
                    clauses.append([-1*get_pos(g, i, j, k1), -1*get_pos(g, i, j, k2)])

    
    row_clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            for i2  in range(1, 10):
                if i != i2:
                    for k in range(1, 10):
                        row_clauses.append([-1*get_pos(g, i, j, k), -1*get_pos(g, i2, j, k)])
    
    row_clauses = list(set([tuple(sorted(i)) for i in row_clauses]))
    row_clauses = [list(i) for i in row_clauses]
    clauses += row_clauses


    col_clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            for j2  in range(1, 10):
                if j != j2:
                    for k in range(1, 10):
                        col_clauses.append([-1*get_pos(g, i, j, k), -1*get_pos(g, i, j2, k)])
            
    col_clauses = list(set([tuple(sorted(i)) for i in col_clauses]))
    col_clauses = [list(i) for i in col_clauses]
    clauses += col_clauses


    subgrid_clauses = []
    
    for i in range(1, 10):
        for j in range(1, 10):
            x, y  = get_subgrid(i, j)
            for p in range(3*x+1, 3*x+4):
                for q in range(3*y+1, 3*y+4):
                    if p != i or q != j:
                        for k in range(1, 10):
                            subgrid_clauses.append([-1*get_pos(g, i, j, k), -1*get_pos(g, p, q, k)])
    
    
    subgrid_clauses = list(set([tuple(sorted(i)) for i in subgrid_clauses]))
    subgrid_clauses = [list(i) for i in subgrid_clauses]
    clauses += subgrid_clauses

    # clauses = list(set(clauses))
    return clauses


def get_inter_clauses(clauses_1, clauses_2):

    clauses = clauses_1 + clauses_2
    for i in range(1, 10):
        for j in range(1, 10):
            for k in range(1, 10):
                clauses.append([-1*get_pos(0, i, j, k), -1*get_pos(1, i, j, k)])

    return clauses            


def validate(solution):


    # row validation
    for i in range(9):
        x = [False]*10
        for j in range(9):
            if not x[solution[i][j]]:
                x[solution[i][j]] = True
            else:
                return False

    
    # column validation
    for i in range(9):
        x = [False]*10
        for j in range(9):
            if not x[solution[j][i]]:
                x[solution[j][i]] = True
            else:
                return False
    

    # sub grid validation
    for i in [0, 1, 2]:
        for j in [0, 1, 2]:
            x = [False]*10
            for p in range(3*i, 3*i+3):
                for q in range(3*j, 3*j+3):
                    if not x[solution[p][q]]:
                        x[solution[p][q]] = True
                    else:
                        return False
    
    return True



clauses_1 = get_clauses(0)
clauses_2 = get_clauses(1)

grid_1  = [[0, 2, 0, 0, 0, 0, 0, 3, 0],
        [0, 0, 0, 6, 0, 1, 0, 0, 0],
        [0, 6, 8, 2, 0, 0, 0, 0, 5],
        [0, 0, 9, 0, 0, 8, 3, 0, 0],
        [0, 4, 6, 0, 0, 0, 7, 5, 0],
        [0, 0, 1, 3, 0, 0, 4, 0, 0],
        [9, 0, 0, 0, 0, 7, 5, 1, 0],
        [0, 0, 0, 1, 0, 4, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 9, 0]]


grid_2  = [[0, 3, 0, 0, 0, 0, 0, 4, 0],
        [0, 0, 0, 7, 0, 2, 0, 0, 0],
        [0, 7, 9, 3, 0, 0, 0, 0, 6],
        [0, 0, 1, 0, 0, 9, 4, 0, 0],
        [0, 5, 7, 0, 0, 0, 8, 6, 0],
        [0, 0, 2, 4, 0, 0, 5, 0, 0],
        [1, 0, 0, 0, 0, 8, 6, 2, 0],
        [0, 0, 0, 2, 0, 5, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 1, 0]]


for i in range(1, 10):
    for j in range(1, 10):
        if grid_1[i-1][j-1] != 0:
            clauses_1.append([get_pos(0, i, j, grid_1[i-1][j-1])])
        if grid_2[i-1][j-1] != 0:
            clauses_2.append([get_pos(1, i, j, grid_2[i-1][j-1])])
        


clauses = get_inter_clauses(clauses_1, clauses_2)
m = Minisat22(bootstrap_with=clauses)
m.solve()

solution_1 = grid_1.copy()
solution_2 = grid_2.copy()

for i in m.get_model():
    if i > 0 and i // 1000 == 0:
        num = i%1000
        x = num//100
        num = num % 100
        y = num//10
        num = num % 10
        solution_1[x-1][y-1] = num
    elif i > 0 and i // 1000 == 1:
        num = i%1000
        x = num//100
        num = num % 100
        y = num//10
        num = num % 10
        solution_2[x-1][y-1] = num


print(validate(solution_1))
print(validate(solution_2))

for k in solution_1:
    print(k)

print('--------------------------------')

for k in solution_2:
    print(k)