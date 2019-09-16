import sys
import re
import random
import numpy as np
import matplotlib.pyplot as plt

dimacs_file = 'data/sudoku_new.txt'



# -- CONSTANTS

# Enable global debug. Warning: prints a ton of info to the screen
DEBUG = 0

# ClausalNormalForm assign method constants
UNSAT = 0
SAT = 1

# ClausalNormalForm backtrack action type constants
RM_CLAUSE = 0
RM_LITERAL = 1
ASSIGN = 2

# BinaryTreeNode node type constants
HARD_CHOICE = 1
PURE_LITERAL = 2
UNIT_CLAUSE = 3



# -- CLASS DEFINITIONS

#class SearchComponent:
#    def rm_literal:
#    def rm_clause:
#    def undo_rm_literal:
#    def undo_rm_clause:
#    def init_with_clause(self, clause, clause_id):
#    def ready:
#    def generate_node:

class RandomChoiceTracker:
    nodes = 0

    def link_cnf(self, cnf_instance):
        self.cnf_instance = cnf_instance

    def init_with_clause(self, clause, clause_id):
        pass

    def rm_clause(self, operand, clause_id):
        pass

    def rm_literal(self, operand, clause_id):
        pass

    def undo_rm_literal(self, operand, clause_id):
        pass

    def undo_rm_clause(self, operand, clause_id):
        pass

    def get_random_literal(self):
        pass

    def ready(self):
        return True

    def generate_node(self, current_node):
        variable = self.cnf_instance.get_random_var()
        literal = variable if random.random() < 0.5 else -variable
        self.nodes += 1
        return HardChoiceNode(literal, current_node)


class UnitClauseTracker:
    unit_clauses = set()
    nodes = 0

    def link_cnf(self, cnf_instance):
        self.cnf_instance = cnf_instance

    def init_with_clause(self, clause, clause_id):
        if len(clause) == 1:
            self.unit_clauses.add(clause_id)

    def rm_clause(self, operand, clause_id):
        if len(operand) == 1:
            self.unit_clauses.remove(clause_id)

    def rm_literal(self, operand, clause_id):
        if len(self.cnf_instance.get_clause(clause_id)) == 2:
            self.unit_clauses.add(clause_id)

    def undo_rm_literal(self, operand, clause_id):
        if len(self.cnf_instance.get_clause(clause_id)) == 1:
            self.unit_clauses.remove(clause_id)
        elif len(self.cnf_instance.get_clause(clause_id)) == 0:
            self.unit_clauses.add(clause_id)

    def undo_rm_clause(self, operand, clause_id):
        if len(operand) == 1:
            self.unit_clauses.add(clause_id)

    def get_unit_clause_literal(self):
        clause_id = random.sample(self.unit_clauses, 1)[0]
        clause = self.cnf_instance.get_clause(clause_id)
        literal = random.sample(clause, 1)[0]
        return literal

    def ready(self):
        if not self.unit_clauses:
            return False
        else:
            return True

    def generate_node(self, current_node):
        literal = self.get_unit_clause_literal()
        self.nodes += 1
        return UnitClauseNode(literal, current_node)

class PureLiteralTracker:
    nodes = 0
    literal_counts = {}
    pure_literals = set()

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            if DEBUG:
                print("Creating new literal entry: {}".format(var))
            self.literal_counts[var] = 0
            self.literal_counts[-var] = 0

        self.cnf_instance = cnf

    def rm_literal(self, operand, clause_id):
        self.remove_value(operand)

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            self.remove_value(literal)

    def undo_rm_literal(self, operand, clause_id):
        self.add_value(operand)

    def undo_rm_clause(self, operand, clause_id):
        for literal in operand:
            self.add_value(literal)

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            self.add_value(literal)

    def add_value(self, literal):
        if DEBUG:
            print("Increasing literal {} counts. Present counts: {}, -counts: {}".format(literal, self.literal_counts[literal], self.literal_counts[-literal]))

        self.literal_counts[literal] += 1

        if (self.literal_counts[-literal] == 0):
            if DEBUG:
                print("Adding to pure literals list : {}".format(literal))
            self.pure_literals.add(literal)
        elif (self.literal_counts[-literal] > 0) & (-literal in self.pure_literals):
            if DEBUG:
                print("Removing from pure literals list : {}".format(-literal))
            self.pure_literals.remove(-literal)


    def remove_value(self, literal):
        if self.literal_counts[literal] == 0:
            print("FATAL ERROR: Tried to remove literal {} with counts 0. Exiting...".format(literal))
            sys.exit()

        if DEBUG:
            print("Decreasing literal {} counts. Present counts: {}, -counts: {}".format(literal, self.literal_counts[literal], self.literal_counts[-literal]))
        self.literal_counts[literal] -= 1

        if (self.literal_counts[-literal] > 0) & (self.literal_counts[literal] == 0):
            if DEBUG:
                print("Adding to pure literals list : {}".format(-literal))
            self.pure_literals.add(-literal)
        elif (self.literal_counts[literal] == 0) & (literal in self.pure_literals):
            if DEBUG:
                print("Removing from pure literals list : {}".format(literal))
            self.pure_literals.remove(literal)

    def get_pure_literal(self):
        if not self.pure_literals:
            return False
        else:
            literal = random.sample(self.pure_literals, 1)[0]
            return literal

    def ready(self):
        if not self.pure_literals:
            return False
        else:
            return True

    def generate_node(self, current_node):
        literal = self.get_pure_literal()
        self.nodes += 1
        return PureLiteralNode(literal, current_node)


# Binary tree node for the Davis-Putnam search
class BinaryTreeNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent


class HardChoiceNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent
        self.type = HARD_CHOICE
        self.true_explored = False
        self.false_explored = False

    def is_explored(self):
        return (self.true_explored & self.false_explored)

    def explore(self):
        if (self.var > 0) & self.true_explored:
            self.var = -self.var
            self.false_explored = True
        elif (self.var < 0) & self.false_explored:
            self.var = -self.var
            self.true_explored = True
        elif (self.var < 0):
            self.false_explored = True
        else:
            self.true_explored = True

        return self.var

class PureLiteralNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent
        self.type = PURE_LITERAL
        self.explored = False

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True
        return self.var

class UnitClauseNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent
        self.type = UNIT_CLAUSE
        self.explored = False

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True
        return self.var



# Data structure for keeping and organizing the current status of the problem
class ClausalNormalForm:

    current_cnf = {}
    literal_counts = {}

    op_stack = []

    pure_literals = set()
    unit_clauses = set()
    unassigned_vars = set()

    def __init__(self, input_file, search_components):
        self.search_components = search_components

        h_sat_file = open(input_file, 'r')

	# First pass: go over DIMACS and create list of clauses
	# https://stackoverflow.com/questions/28890268/parse-dimacs-cnf-file-python
        temp_clause_list = [[]]

        for line in h_sat_file:
            tokens = line.split()
            if len(tokens) != 0 and tokens[0] not in ("p", "c"):
                for tok in tokens:
                    lit = int(tok)
                    if lit == 0:
                        temp_clause_list.append(list())
                        break
                    else:
                        temp_clause_list[-1].append(lit)

                    var = abs(lit)
                    if var not in self.unassigned_vars:
                        self.unassigned_vars.add(var)

        temp_clause_list.pop()

        for search_comp in self.search_components:
            search_comp.link_cnf(self)

        # Go over clauses and do parsing
        for clause_id, clause in enumerate(temp_clause_list):

            # Keep clauses as sets for easy add/remove and search
            clause_id = str(chr(clause_id)) # this is to easier search for info in log
            clause = set([int(x) for x in clause])

            for literal in clause:
                # Check for tautologies
                if -literal in clause:
                    if DEBUG:
                        print("Removing clause:", clause)
                        break
            # If not a tautology: store the clause
            else:
                for search_comp in self.search_components:
                    search_comp.init_with_clause(clause, clause_id)

                self.current_cnf[clause_id] = clause

        h_sat_file.close()

    def get_unassigned(self):
        return self.unassigned_vars

    def backtrack(self, no_steps=1):

        if no_steps > len(self.op_stack):
            print("FATAL ERROR: Tried to backtrack more steps than possible. No_steps: {}. Size of stack: {}. Exiting...".format(no_steps, self.op_stack))
            sys.exit()

        if DEBUG:
            print("Backtrack, no of steps: {}".format(no_steps))

        for i in range(no_steps):
            # Read the last operation sequence from stack
            ops_single_step = self.op_stack.pop()

            # Revert the operation sequence
            for op in ops_single_step:
                action = op[0]
                clause_id = op[1]
                operand = op[2]

                # Restore deleted clauses
                if action == RM_CLAUSE:
                    if DEBUG:
                        print("undoing RM_CLAUSE:")
                        print("clause_id: {}, operand: {}".format(clause_id, operand))

                    for search_comp in self.search_components:
                        search_comp.undo_rm_clause(operand, clause_id)

                    self.current_cnf[clause_id] = operand

                # Restore deleted literals
                elif action == RM_LITERAL:
                    if DEBUG:
                        print("undoing RM_LITERAL:")
                        print("clause_id: {}, operand: {}".format(clause_id, operand))

                    # If it was a unit clause it will stop being one when we restore the literal
                    for search_comp in self.search_components:
                        search_comp.undo_rm_literal(operand, clause_id)

                    self.current_cnf[clause_id].add(operand)

                # Restore variables to unassigned_vars 
                elif action == ASSIGN:
                    if DEBUG:
                        print("undoing ASSIGN:")
                        print("operand: {}".format(operand))

                    self.unassigned_vars.add(operand)

    def assign(self, assignment):

        status = None

        # Remember all operations for backtracking
        # Will keep tuples of the form:
        # [0] : Op code (ASSIGN, RM_CLAUSE, RM_LITERAL)
        # [1] : Clause ID (if applicable, else: None)
        # [2] : Operand
        ops_single_step = []

        var = abs(assignment)

        if var not in self.unassigned_vars:
            print("FATAL ERROR: Tried to assign variable: {} which is not on the unassigned list. Exiting...".format(var))
            sys.exit()

        # Remember that we took this var from unassigned list
        ops_single_step.append( (ASSIGN, None, var) )
        self.unassigned_vars.remove(var)

        if DEBUG:
            print("Assign step. Assignment: {}".format(assignment))

        # Go through the clauses and perform assignment
        for clause_id, clause in list(self.current_cnf.items()):
            if DEBUG:
                print("Clause id: {}, clause: {}".format(clause_id, clause))

            if assignment in clause:
                if DEBUG:
                    print("Assignment found. Removing clause")

                # Remember that we removed this clause
                ops_single_step.append( (RM_CLAUSE, clause_id, clause) )

                for search_comp in self.search_components:
                    search_comp.rm_clause(clause, clause_id)

                del self.current_cnf[clause_id]

            elif -assignment in clause:
                if DEBUG:
                    print("NOT Assignment found. Removing literal")

                # Remember that we removed this literal
                ops_single_step.append( (RM_LITERAL, clause_id, -assignment) )

                for search_comp in self.search_components:
                    search_comp.rm_literal(-assignment, clause_id)

                self.current_cnf[clause_id].remove(-assignment)

                # If empty set detected: UNSAT. Exit loop and report back
                if not bool(self.current_cnf[clause_id]):
                    status = UNSAT
                    if DEBUG: 
                        print("UNSAT FOUND")
                    break

        # If the cnf is empty: report SAT!
        if not bool(self.current_cnf):
            status = SAT
        else:
            self.op_stack.append(ops_single_step)

        return status

    def get_clause(self, clause_id):
        return self.current_cnf[clause_id]

    def print_op_stack(self):
        print(self.op_stack)

    def print_current_cnf(self):
        print(self.current_cnf)

    def print_vars(self):
        print(self.unassigned_vars)

    def print_debug(self):
        print("-------------------------------------------")
        print("OP STACK:")
        self.print_op_stack()
        print("CURRENT CNF:")
        self.print_current_cnf()
        print("VARS:")
        self.print_vars()

    def get_random_var(self):
        variables = self.get_unassigned()
        var = random.sample(variables, 1)[0]
        return var



# -- DPLL

NO_TESTS = 4
PRINTS = True

a_backtracks = np.zeros((NO_TESTS, 1))
a_explored_nodes = np.zeros((NO_TESTS, 1))
a_hard_choice_nodes = np.zeros((NO_TESTS, 1))
a_unit_clause_nodes = np.zeros((NO_TESTS, 1))
a_pure_literal_nodes = np.zeros((NO_TESTS, 1))

for test in range(NO_TESTS):
    print("Running test, ", test, end='\r')

    search_components = [UnitClauseTracker(), PureLiteralTracker(), RandomChoiceTracker()]
    my_cnf = ClausalNormalForm(dimacs_file, search_components)

    backtracks = 0
    explored_nodes = 0

    # Gen parent node

    for search_cmp in my_cnf.search_components:
        if search_cmp.ready():
            current_node = search_cmp.generate_node(None)
            break

    while True:
        # Startup
        if current_node.is_explored():
            if DEBUG:
                print("Backtracking")
            if current_node.parent != None:
                backtracks += 1
                my_cnf.backtrack()
                previous_node = current_node
                current_node = previous_node.parent
                del previous_node
            else:
                print("UNSAT!")
                sys.exit()
        else:
            result = my_cnf.assign(current_node.explore())

            if result == SAT:
                break
            # If assignment yielded UNSAT - backtrack
            elif result == UNSAT:
                my_cnf.backtrack()
            # Check and create unit clause nodes
            else:
                for search_cmp in my_cnf.search_components:
                    if search_cmp.ready():
                        current_node = search_cmp.generate_node(current_node)
                        break

            explored_nodes += 1

    # Will get here only if SAT

    assignment = []
    counter = 0

    while current_node != None:
        assignment.append(current_node.var)
        if current_node.var > 0:
            counter += 1
        current_node = current_node.parent

    a_backtracks[test] = backtracks
    a_explored_nodes[test] = explored_nodes
    a_hard_choice_nodes[test] = my_cnf.search_components[0].nodes
    a_unit_clause_nodes[test] = my_cnf.search_components[1].nodes
    a_pure_literal_nodes[test] = my_cnf.search_components[2].nodes

    if PRINTS:

        print("SAT. Assignment is:")
        print(assignment)
        # Poor man's debugging, should be 729 assigned and 81 true for sudoku
        print("Number of assigned variables: ", len(assignment))
        print("Number of true variables: ", counter)
        print("Number of backtracks: ", backtracks)
        print("Number of explored nodes: ", explored_nodes)
        print("Number of unit clause nodes: ", my_cnf.search_components[0].nodes)
        print("Number of pure literal nodes: ", my_cnf.search_components[1].nodes)
        print("Number of hard choice nodes: ", my_cnf.search_components[2].nodes)

   # h_out_file = open('./output.out', 'w')
   # for var in assignment:
   #     h_out_file.write('{} {}\n'.format(var, '0'))
   # h_out_file.close()

print()
print("STD: ", np.std(a_backtracks))
print("MEAN: ", np.mean(a_backtracks))



# TODO IDEA: CHANGE HOW CLAUSES ARE STORED?
#   Linked list type data structure - clause is an object, has parents (all variables participating)


