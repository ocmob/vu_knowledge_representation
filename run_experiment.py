import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Internal
import search_components
import cnf
from dp import dp

# -8 : 8 , step: 0.1

dimacs = []
for i in range(1,1):
    dimacs.append( ('randsat_{}'.format(i), ['data/uf75-325/ai/hoos/Shortcuts/UF75.325.100/uf75-0{}.cnf'.format(i)] ))
for i in range(1,2):
    dimacs.append( ('1000sudokus_{}'.format(i), ['data/sudoku-rules.txt', 'data/1000sudokus/1000sudokus_{}.txt'.format(i)] ))
for i in range(1,2):
    dimacs.append( ('damnhard_{}'.format(i), ['data/sudoku-rules.txt', 'data/damnhard_converted_{}.txt'.format(i)] ))

#hyp_sweep = np.arange(-8, 8, 0.1)
hyp_sweep = np.arange(0, 5, 5)
gen_comp = []

#for hyp_threshold in hyp_sweep:
#    tup = ( hyp_threshold,
#            [
#                (search_components.UnitClauseComponent(), 'uc_nodes'), 
#                (search_components.PureLiteralComponent(), 'pl_nodes'),
#                (search_components.MostConstrainingMeta(hyp_threshold), 'most_constraining_nodes'),
#                (search_components.JWTwoSided(), 'jwnodes'),
#            ]
#    )
#    gen_comp.append(tup)

#for hyp_threshold in hyp_sweep:
#    tup = ( 'rand',
#                [
#                    (search_components.UnitClauseComponent(), 'uc_nodes'), 
#                    (search_components.PureLiteralComponent(), 'pl_nodes'),
#                    (search_components.MostConstrainingRandMeta(), 'most_constraining_nodes'),
#                    (search_components.JWTwoSided(), 'jwnodes'),
#                ]
#        )
#    gen_comp.append(tup)
#
tup = ( 'most_constraning',
            [
                (search_components.UnitClauseComponent(), 'uc_nodes'), 
                (search_components.PureLiteralComponent(), 'pl_nodes'),
                (search_components.MostConstrainingComponent(), 'splits'),
            ]
    )
gen_comp.append(tup)
#tup = ( 'rand',
#            [
#                (search_components.UnitClauseComponent(), 'uc_nodes'), 
#                (search_components.PureLiteralComponent(), 'pl_nodes'),
#                (search_components.RandomChoiceComponent(), 'splits'),
#            ]
#    )
#gen_comp.append(tup)
tup = ( 'JW',
            [
                (search_components.UnitClauseComponent(), 'uc_nodes'), 
                (search_components.PureLiteralComponent(), 'pl_nodes'),
                (search_components.JWTwoSided(), 'splits'),
            ]
    )
gen_comp.append(tup)

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
    'search_components' : gen_comp
    #'search_components' : [
    #    ( 'most_constraining_dp',
    #        [
    #            (search_components.UnitClauseComponent(), 'uc_nodes'), 
    #            (search_components.PureLiteralComponent(), 'pl_nodes'),
    #            (search_components.MostConstrainingMeta(), 'split_nodes'),
    #        ]
    #    ),
    #    #( 'jw_two_sided',
    #    #    [
    #    #        (search_components.UnitClauseComponent(), 'uc_nodes'), 
    #    #        (search_components.PureLiteralComponent(), 'pl_nodes'),
    #    #        (search_components.JWTwoSided(), 'split_nodes'),
    #    #    ]
    #    #),
    #    #( 'random',
    #    #    [
    #    #        (search_components.UnitClauseComponent(), 'uc_nodes'), 
    #    #        (search_components.PureLiteralComponent(), 'pl_nodes'),
    #    #        (search_components.RandomChoiceComponent(), 'split_nodes'),
    #    #    ]
    #    #)
    #]
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
    #lengths = []

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

                #lengths.append((results['cnf'].length_of_clause, dimacs_set_name+scmp_set_name))

                df = pd.DataFrame(res_dict)
                data = data.append(df, ignore_index = True)

    print()
    print('Done with {} cases. Results written to {}'.format(total_cases, 'DUMMY FILE'))

    return data 



data = run_experiment(experiment_run)
print(data)
data.to_csv('output.csv')
