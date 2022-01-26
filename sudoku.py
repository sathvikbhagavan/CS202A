from pysat.solvers import Minisat22

def get_pos(i, j, k):
    # get the numeber as  ijk
    return 100*i + 10*j + k


def get_subgrid(i, j):
    return [(i-1)//3, (j-1)//3]


def get_clauses():
    clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            clauses.append([get_pos(i, j, k) for k in range(1, 10)])
            for k1 in range(1, 10):
                for k2 in range(k1+1, 10):
                    clauses.append([-1*get_pos(i, j, k1), -1*get_pos(i, j, k2)])

    
    row_clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            for i2  in range(1, 10):
                if i != i2:
                    for k in range(1, 10):
                        row_clauses.append([-1*get_pos(i, j, k), -1*get_pos(i2, j, k)])
    
    row_clauses = list(set([tuple(sorted(i)) for i in row_clauses]))
    row_clauses = [list(i) for i in row_clauses]
    clauses += row_clauses


    col_clauses = []
    for i in range(1, 10):
        for j in range(1, 10):
            for j2  in range(1, 10):
                if j != j2:
                    for k in range(1, 10):
                        col_clauses.append([-1*get_pos(i, j, k), -1*get_pos(i, j2, k)])
            
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
                            subgrid_clauses.append([-1*get_pos(i, j, k), -1*get_pos(p, q, k)])
    
    
    subgrid_clauses = list(set([tuple(sorted(i)) for i in subgrid_clauses]))
    subgrid_clauses = [list(i) for i in subgrid_clauses]
    clauses += subgrid_clauses

    # clauses = list(set(clauses))
    return clauses



clauses = get_clauses()

grid  = [[0, 0, 0, 1, 0, 9, 4, 2, 7],
        [1, 0, 9, 8, 0, 0, 0, 0, 6],
        [0, 0, 7, 0, 5, 0, 1, 0, 8],
        [0, 5, 6, 0, 0, 0, 0, 8, 2],
        [0, 0, 0, 0, 2, 0, 0, 0, 0],
        [9, 4, 0, 0, 0, 0, 6, 1, 0],
        [7, 0, 4, 0, 6, 0, 9, 0, 0],
        [6, 0, 0, 0, 0, 8, 2, 0, 5],
        [2, 9, 5, 3, 0, 1, 0, 0, 0]]


for i in range(1, 10):
    for j in range(1, 10):
        if grid[i-1][j-1] != 0:
            clauses.append([get_pos(i, j, grid[i-1][j-1])])


# print(clauses)
# print(len(clauses))
m = Minisat22(bootstrap_with=clauses)
m.solve()
# print(m.get_model())

solution = grid.copy()

for i in m.get_model():
    # print(i)
    if i > 0:
        num = i
        x = num//100
        num = num % 100
        y = num//10
        num = num % 10
        solution[x-1][y-1] = num

for k in solution:
    print(k)