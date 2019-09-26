# Internal
import search_components
import cnf

def dp(dimacs_file_set, search_cmp):

    for scmp in search_cmp:
        scmp.reset()

    my_cnf = cnf.ClausalNormalForm(dimacs_file_set, search_cmp)

    backtracks = 0
    success = False

    # Generate parent node
    for search_cmp in my_cnf.search_cmp:
        if search_cmp.ready():
            current_node = search_cmp.generate_node(None)
            break

    while True:
        if current_node.is_explored():
            if current_node.parent != None:
                backtracks += 1
                my_cnf.backtrack()
                previous_node = current_node
                current_node = previous_node.parent
                del previous_node
            else:
                break
        else:
            result = my_cnf.assign(current_node.explore())

            # SAT
            if result == True:
                success = True
                break
            # UNSAT
            elif result == False:
                my_cnf.backtrack()
            # Succesful assignment
            else:
                for search_cmp in my_cnf.search_cmp:
                    if search_cmp.ready():
                        current_node = search_cmp.generate_node(current_node)
                        break

    # Backtrack through all nodes to get the assignment
    assignment = []
    if success:
        while current_node != None:
            assignment.append(current_node.var)
            current_node = current_node.parent

    answer_dict = {
            'SAT' : success,
            'solution' : assignment,
            'backtracks' : backtracks,
            'cnf' : my_cnf
    }

    return answer_dict
