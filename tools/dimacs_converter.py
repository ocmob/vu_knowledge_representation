

sudoku_file = open('1000 sudokus.txt')
#read all the lines and remove last empty line
sudokus = sudoku_file.read().split('\n')[:-1]
new_file = open("new_file.txt","w+")
# print(sudokus)

#make a list of lists in which each individual list contains 1 sudoku
def list_of_lists_maker(lst):
    lst_of_lst = []
    for i in lst:
        spl = i.split(',')
        lst_of_lst.append(spl)
    return lst_of_lst

lst_of_lists = (list_of_lists_maker(sudokus))

def everything(lst_of_lists):
    for individual_sudoku in lst_of_lists:
        for elements in individual_sudoku:
            #9x9 sudokus
            dict_of_sudokus = {}
            if len(elements) == 81:
                thingy = ([elements[i:i+9] for i in range(0, len(elements), 9)])
                new_file.write('\n')
                for row in thingy:
                    rownumber = int(thingy.index(row)) + 1
                    for char in row:
                        column_number = row.index(char) + 1
                        if char != '.':
                            char = str(rownumber) + str(column_number) + char + ' 0'
                            new_file.write(char + '\n')

            # 4x4 sudokus
            elif len(elements) == 16:
                thingy = ([elements[i:i+4] for i in range(0, len(elements), 4)])
                new_file.write('\n')
                for row in thingy:
                    rownumber = int(thingy.index(row)) + 1
                    for char in row:
                        column_number = row.index(char) + 1
                        if char != '.':
                            char = str(rownumber) + str(column_number) + char + ' 0'
                            new_file.write(char + '\n')

            # 16x16 sudokus
            elif len(elements) == 256:
                thingy = ([elements[i:i+16] for i in range(0, len(elements), 16)])
                new_file.write('\n')
                for row in thingy:
                    rownumber = int(thingy.index(row)) + 1
                    for char in row:
                        column_number = row.index(char) + 1
                        if char != '.':
                            char = str(rownumber) + str(column_number) + char + ' 0'
                            new_file.write(char + '\n')


def dimacs_maker():
    everything(lst_of_lists)
    return

dimacs_maker()


"""
168 0
175 0
225 0
231 0
318 0
419 0
444 0
465 0
493 0
689 0
692 0
727 0
732 0
828 0
886 0
956 0
961 0
973 0
"""
