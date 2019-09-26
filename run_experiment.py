import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse

# Internal
import search_components
import cnf
from dp import dp

def check_range(arg):
    try:
        value = int(arg)
    except ValueError as err:
       raise argparse.ArgumentTypeError(str(err))

    if value <= 0 or value > 5:
        message = "Expected 0 < value <= 5, got value = {}".format(value)
        raise argparse.ArgumentTypeError(message)

    return value

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-rand', action='store_true',
                    help='Run test set for random heuristic')
group.add_argument('-least', action='store_true',
                    help='Run test set for least constraining heuristic')
group.add_argument('-most', action='store_true',
                    help='Run test set for most constraining heuristic')
group.add_argument('-jw', action='store_true',
                    help='Run test for Jeroslaw-Wang heuristic')

parser.add_argument("ranges", type=check_range,
                    help='Regulate number of cases. Ranges*10 randsat will be run, ranges*40 1000_sudokus will be run, ranges*4 damnhard will be run.')

args = parser.parse_args()

dimacs = []

for i in range(1,10*args.ranges+1):
    dimacs.append( ('randsat_{}'.format(i), ['data/uf75-325/ai/hoos/Shortcuts/UF75.325.100/uf75-0{}.cnf'.format(i)] ))
for i in range(1,40*args.ranges+1):
    dimacs.append( ('1000sudokus_{}'.format(i), ['data/sudoku-rules.txt', 'data/1000sudokus/1000sudokus_{}.txt'.format(i)] ))
for i in range(1,4*args.ranges+1):
    dimacs.append( ('damnhard_{}'.format(i), ['data/sudoku-rules.txt', 'data/damnhard_converted_{}.txt'.format(i)] ))

gen_comp = []

if args.rand:
    filename = 'rand_output.csv'
    iterations = 10
    tup = ( 'rand',
                [
                    (search_components.UnitClauseComponent(), 'uc_nodes'), 
                    (search_components.PureLiteralComponent(), 'pl_nodes'),
                    (search_components.RandomChoiceComponent(), 'splits'),
                ]
        )
    gen_comp.append(tup)
elif args.least:
    filename = 'least_constraning_output.csv'
    iterations = 1
    tup = ( 'least_constraining',
                [
                    (search_components.UnitClauseComponent(), 'uc_nodes'), 
                    (search_components.PureLiteralComponent(), 'pl_nodes'),
                    (search_components.LeastConstrainingComponent(), 'splits'),
                ]
        )
    gen_comp.append(tup)
elif args.most:
    filename = 'most_constraning_output.csv'
    iterations = 1
    tup = ( 'most_constraning',
                [
                    (search_components.UnitClauseComponent(), 'uc_nodes'), 
                    (search_components.PureLiteralComponent(), 'pl_nodes'),
                    (search_components.MostConstrainingComponent(), 'splits'),
                ]
        )
    gen_comp.append(tup)
elif args.jw:
    filename = 'jw_output.csv'
    iterations = 1
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
    'iterations' : iterations,

    # ARRAY OF TUPLES:
    # [0] = NAME OF THE SET
    # [1] = ARRAY OF TUPLES:
    #   [0] = SEARCH COMPONENT
    #   [1] = RETURN METRIC NAME
    'search_components' : gen_comp
}

def run_experiment(run_params, out_filename):

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

    data.to_csv(out_filename)
    print('')
    print('Done with {} cases. Results written to {}'.format(total_cases, out_filename))

run_experiment(experiment_run, filename)
