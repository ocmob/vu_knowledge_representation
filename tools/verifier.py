import itertools
import numpy as np
import sys

sudoku = np.zeros((9,9), dtype='int32')

filename = sys.argv[1]

def sudoku_ok(line):
    return (len(line) == 9 and sum(line) == sum(set(line)))

def check_sudoku(grid):
    bad_rows = [row for row in grid if not sudoku_ok(row)]
    grid = list(zip(*grid))
    bad_cols = [col for col in grid if not sudoku_ok(col)]
    squares = []
    for i in range(0,9, 3):
        for j in range(0,9, 3):
          square = list(itertools.chain(row[j:j+3] for row in grid[i:i+3]))
          squares.append(square)
    bad_squares = [square for square in squares if not sudoku_ok(list(itertools.chain(*square)))]
    return not (bad_rows or bad_cols or bad_squares)

neg_counter = 0
pos_counter = 0

with open(filename) as f:
    for line in f:
        if(int(line.split()[0]) > 0):
            row = int(line[0])
            col = int(line[1])
            value = int(line[2])
            sudoku[row-1][col-1] = value
            pos_counter += 1
        else:
            neg_counter += 1
    if(check_sudoku(sudoku)): print("Success! This is a valid sudoku.")
    else: print("Failed. This is not a valid sudoku.")
    print(check_sudoku(sudoku))

print(sudoku)
print('Number of true assignments: {}'.format(pos_counter))
print('Number of false assignments: {}'.format(neg_counter))
print('Total number of assignments: {}'.format(neg_counter+pos_counter))
