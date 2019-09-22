import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Internal
import search_components
import cnf

def dp(dimacs_file_set, search_cmp):

    for scmp in search_cmp:
        scmp.reset()

    my_cnf = cnf.ClausalNormalForm(dimacs_file_set, search_cmp)

    backtracks = 0
    success = False

    for search_cmp in my_cnf.search_cmp:
        if search_cmp.ready():
            current_node = search_cmp.generate_node(None)
            break

    while True:
        # Startup
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

            if result == cnf.SAT:
                success = True
                break
            # If assignment yielded UNSAT - backtrack
            elif result == cnf.UNSAT:
                my_cnf.backtrack()
            # Check and create unit clause nodes
            else:
                for search_cmp in my_cnf.search_cmp:
                    if search_cmp.ready():
                        current_node = search_cmp.generate_node(current_node)
                        break

    if success:
        assignment = []
        counter = 0

        while current_node != None:
            assignment.append(current_node.var)
            if current_node.var > 0:
                counter += 1
            current_node = current_node.parent

    answer_dict = {
            'SAT' : success,
            'solution' : assignment,
            'backtracks' : backtracks,
            'cnf' : my_cnf
    }

    return answer_dict

dimacs = []
#dimacs.append( ('medium_sat', ['data/moderate_sat.txt'] ))
#dimacs.append( ('damnhard_0', ['data/sudoku-rules.txt', 'data/damnhard_converted_{}.txt'.format(0)] ))
#for i in range(1,10):
    #dimacs.append( ('randsat_{}'.format(i), ['data/uf75-325/ai/hoos/Shortcuts/UF75.325.100/uf75-0{}.cnf'.format(i)] ))
for i in range(10):
    dimacs.append( ('1000sudokus_{}'.format(i), ['data/sudoku-rules.txt', 'data/1000sudokus/1000sudokus_{}.txt'.format(i)] ))
for i in range(10):
    dimacs.append( ('damnhard_{}'.format(i), ['data/sudoku-rules.txt', 'data/damnhard_converted_{}.txt'.format(i)] ))

experiment_run = {
    # ARRAY OF TUPLES:
    # [0] = NAME OF SET
    # [1] = ARRAY WITH PATHS OF DIMACS FILES 
    'dimacs' : dimacs,

    # NUMBER OF ITERATIONS PER EACH DIMACS SET
    'iterations' : 1,

    # ARRAY OF TUPLES:
    # [0] = NAME OF THE SET
    # [1] = ARRAY OF TUPLES:
    #   [0] = SEARCH COMPONENT
    #   [1] = RETURN METRIC NAME
    'search_components' : [
        ( 'jw_two_sided',
            [
                (search_components.UnitClauseComponent(), 'uc_nodes'), 
                (search_components.PureLiteralComponent(), 'pl_nodes'),
                (search_components.JWTwoSided(), 'split_nodes'),
            ]
        ),
        ( 'most_constraining_dp',
            [
                (search_components.UnitClauseComponent(), 'uc_nodes'), 
                (search_components.PureLiteralComponent(), 'pl_nodes'),
                (search_components.MostConstrainingComponent(), 'split_nodes'),
            ]
        )
    ]
}
#experiment_run = {
#    # ARRAY OF TUPLES:
#    # [0] = NAME OF SET
#    # [1] = ARRAY WITH PATHS OF DIMACS FILES 
#    'dimacs' : dimacs,
#
#    # NUMBER OF ITERATIONS PER EACH DIMACS SET
#    'iterations' : 1,
#
#    # ARRAY OF TUPLES:
#    # [0] = NAME OF THE SET
#    # [1] = ARRAY OF TUPLES:
#    #   [0] = SEARCH COMPONENT
#    #   [1] = RETURN METRIC NAME
#    'search_components' : [
#        ( 'random_choice_dp',
#            [
#                (search_components.UnitClauseComponent(), 'uc_nodes'), 
#                (search_components.PureLiteralComponent(), 'pl_nodes'),
#                (search_components.JWTwoSided(), 'split_nodes'),
#            ]
#        ),
#        ( 'most_constraining_dp',
#            [
#                (search_components.UnitClauseComponent(), 'uc_nodes'), 
#                (search_components.PureLiteralComponent(), 'pl_nodes'),
#                (search_components.MostConstrainingComponent(), 'split_nodes'),
#            ]
#        )
#    ]
#}

def run_experiment(run_params):

    data = pd.DataFrame()

    total_cases = len(run_params['search_components'])*run_params['iterations']*len(run_params['dimacs'])
    counter = 0

    print("Starting experiment.")
    print("Total {} cases will be run.".format(total_cases))

    for scmp_set in run_params['search_components']:
        scmp_set_name = scmp_set[0]
        scmp_cmp = [ tup[0] for tup in scmp_set[1] ]
        scmp_cmp_names = [ tup[1] for tup in scmp_set[1] ]

        for dimacs_set in run_params['dimacs']:
            dimacs_set_name = dimacs_set[0]
            dimacs_set_paths = dimacs_set[1]

            for i in range(run_params['iterations']):
                counter += 1
                print("", end='\r')
                print("Running: scmp_set_name: {}, dimacs_set_name: {}, iteration: {}. Case {} of {} total.".format(
                    scmp_set_name, dimacs_set_name, i, counter, total_cases), end='\r')

                results = dp(dimacs_set_paths, scmp_cmp)

                #TODO : validate here valid
                
                res_dict = {
                        'SAT' : [1 if results['SAT'] else 0],
                        'valid' : [1],
                        'dimacs_set' : [dimacs_set_name],
                        'iteration' : [i],
                        'cmp_set' : [scmp_set_name],
                        'backtracks' : [results['backtracks']]
                        }
                
                for k, name in enumerate(scmp_cmp_names):
                    res_dict[name] = [results['cnf'].search_cmp[k].get_metrics()]

                df = pd.DataFrame(res_dict)
                data = data.append(df, ignore_index = True)

    print()
    print('Done with {} cases. Results written to {}'.format(total_cases, 'DUMMY FILE'))

    return data


data = run_experiment(experiment_run)
print(data)



# Inputs:
#   -A list of dimacs file sets
#       -A codename of each set
#   -no of iterations per dimacs
#   -component sets
#       -codename per component set
#       -and names of fields displaying metrics data from each components
# Outputs:
#   -SAT/UNSAT
#   -Valid/invalid
#   -Codename of DIMACS set
#   -Iteration number
#   -Codename of component set
#   -fields displaying metrics data
# Todo:
#   -Run checker after every run






# TODO IDEA: CHANGE HOW CLAUSES ARE STORED?
#   Linked list type data structure - clause is an object, has parents (all variables participating)


