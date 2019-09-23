import sys

sudoku_file = sys.argv[1]
output_file_prefix = sys.argv[2]

h_sudoku_file = open(sudoku_file, 'r')

sudokus = []

for line in h_sudoku_file:
    line = line.strip('\n')
    current_sudoku = []
    for i, char in enumerate(line):
        if char != '.':
            current_sudoku.append('{}{}{} 0\n'.format(i//9+1,i%9+1,char))
    sudokus.append(current_sudoku)

h_sudoku_file.close()

for i, sudoku in enumerate(sudokus):
    h_output_file = open('{}_{}.txt'.format(output_file_prefix, i), 'w')
    for line in sudoku:
        h_output_file.write(line)
    h_output_file.close()

