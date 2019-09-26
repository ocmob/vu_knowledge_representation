import argparse
import search_components
import time
from dp import dp

parser = argparse.ArgumentParser()

parser.add_argument("input_file",
                    help='Input file in DIMACS format')

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-S1', action='store_true',
                    help='Run DP with a random heuristic')
group.add_argument('-S2', action='store_true',
                    help='Run DP with a two-sided JW heuristic')
group.add_argument('-S3', action='store_true',
                    help='Run DP with a most constraining heuristic')

args = parser.parse_args()

if args.S1:
    srcmp = [
        search_components.UnitClauseComponent(),
        search_components.PureLiteralComponent(),
        search_components.RandomChoiceComponent() ]
    print('Starting DP with a random heuristic...')
elif args.S2:
    srcmp = [
        search_components.UnitClauseComponent(),
        search_components.PureLiteralComponent(),
        search_components.JWTwoSided() ]
    print('Starting DP with a two-sided JW heuristic...')
else:
    srcmp = [
        search_components.UnitClauseComponent(),
        search_components.PureLiteralComponent(),
        search_components.MostConstrainingComponent() ]
    print('Starting DP with a most constraining heuristic...')

print('Input DIMACS file: ', args.input_file)

start = time.time()
answer = dp([args.input_file], srcmp)
end = time.time()

splits = srcmp[2].get_metrics()
backtracks = answer['backtracks']

print('Done. {:.3f}s elapsed. {} backtracks, {} splits.'.format(
    end-start, backtracks, splits))

output_file = args.input_file + '.out'

if answer['SAT']:
    print('Result is: SAT. Writing output to', output_file)

    h_output_file = open(output_file, 'w')
    for var in answer['solution']:
        h_output_file.write(str(var) + ' 0\n')
    h_output_file.close()
else:
    print('Result is: UNSAT. No output will be written.')
