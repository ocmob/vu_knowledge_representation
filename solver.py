import sys
import re
import random

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

# Binary tree node for the Davis-Putnam search
class BinaryTreeNode:
    def __init__(self, var, parent, node_type=HARD_CHOICE):
        self.var = var
        self.parent = parent
        self.type = node_type
        self.true_explored = False
        self.false_explored = False


# Data structure for keeping and organizing the current status of the problem
class ClausalNormalForm:
    current_cnf = {}
    op_stack = []
    unit_clauses = set()
    pure_literals = set()
    impure_literals = set()
    unassigned_vars = set()

    def __init__(self, input_file):
        h_sat_file = open(input_file, 'r')

        # Go over the DIMACS file
        for clause_id, line in enumerate(h_sat_file):

            # TODO : remove comments from DIMACS
            # TODO : crosscheck no of vars from DIMACS with no of vars read from file

            clause = line.split()

            # Record all the variables
            for var in clause[:-1]:
                var = re.sub('-', '', var)
                if var not in self.unassigned_vars:
                    self.unassigned_vars.add(int(var))

            # Keep clauses as sets for easy add/remove and search
            clause = set([int(x) for x in clause][:-1])

            # Check and record unit clauses
            if len(clause) == 1:
                self.unit_clauses.add(clause_id)

            # Check for tautologies
            for literal in clause:
                if -literal in clause:
                    if DEBUG:
                        print("Removing clause:", clause)
                    break

            # If not a tautology: store the clause
            else:
                self.current_cnf[clause_id] = clause

        # TODO : implement self.chk_pure_literals() efficiently

    # TODO : This is a poor man's version of pure literal checking

    def chk_pure_literals(self):
        self.pure_literals = set()
        self.impure_literals = set()
    
        for clause in self.current_cnf.values():
            for literal in clause:
                if abs(literal) not in self.impure_literals:
                    if -literal in self.pure_literals:
                        self.impure_literals.add(abs(literal))
                    elif literal not in self.pure_literals:
                        self.pure_literals.add(literal)


    def get_unassigned(self):
        return self.unassigned_vars

    # TODO : Unit clause handling could be better, not having to call sth with clause_id
    def get_unit_clauses(self):
        if DEBUG:
            print("Returning unit clause IDs:")
            print(self.unit_clauses)
        return self.unit_clauses

    def get_unit_clause_literal(self, clause_id):
        literal = self.current_cnf[clause_id].pop()
        if DEBUG:
            print("Getting literal from a unit clause")
            print("literal: ",literal)
        self.current_cnf[clause_id].add(literal)
        return literal

    def backtrack(self, no_steps=1):

        # TODO : Raise exception if asked for more steps of backtrack than possible

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

                    self.current_cnf[clause_id] = operand

                    # If was a unit clause restore it into the unit clause list
                    if len(operand) == 1:
                        if DEBUG:
                            print("Was a unit clause")
                        self.unit_clauses.add(clause_id)

                # Restore deleted literals
                elif action == RM_LITERAL:
                    if DEBUG:
                        print("undoing RM_LITERAL:")
                        print("clause_id: {}, operand: {}".format(clause_id, operand))

                    # If it a unit clause now it will stop being one when we restore the literal
                    if len(self.current_cnf[clause_id]) == 1:
                        self.unit_clauses.remove(clause_id)

                    self.current_cnf[clause_id].add(operand)

                # Restore variables to unassigned_vars 
                elif action == ASSIGN:
                    if DEBUG:
                        print("undoing ASSIGN:")
                        print("operand: {}".format(operand))

                    self.unassigned_vars.add(operand)

    def assign(self, assignment):

        status = None

        # TODO : Raise exception if trying to assign variable which is not on the unassigned list

        # Remember all operations for backtracking
        ops_single_step = []

        var = abs(assignment)

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

                if len(self.current_cnf[clause_id]) == 1:
                    self.unit_clauses.remove(clause_id)

                del self.current_cnf[clause_id]

            elif -assignment in clause:
                if DEBUG:
                    print("NOT Assignment found. Removing literal")

                # Remember that we removed this literal
                ops_single_step.append( (RM_LITERAL, clause_id, -assignment) )

                self.current_cnf[clause_id].remove(-assignment)

                # If empty set detected: UNSAT. Exit loop and report back
                if not bool(self.current_cnf[clause_id]):
                    status = UNSAT
                    if DEBUG: 
                        print("UNSAT FOUND")
                    break

                # If new unit clause appeared: record it
                if len(self.current_cnf[clause_id]) == 1:
                    self.unit_clauses.add(clause_id)

        # If the cnf is empty: report SAT!
        if not bool(self.current_cnf):
            status = SAT
        else:
            # TODO : Perhaps can be done easier by merging dicts instead of doing this?
            self.op_stack.append(ops_single_step)

        return status


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



# -- HELPER FUNCTIONS

def get_random_var():
    variables = my_cnf.get_unassigned()
    var = random.sample(variables, 1)[0]
    return var



# -- DPLL

my_cnf = ClausalNormalForm(dimacs_file)

if DEBUG:
    print("Creating parent node")

current_node = None

if my_cnf.get_unit_clauses():
    if DEBUG:
        print("Creating unit clause node")
    # TODO : How do we choose the unit clause to assign? Currently taking first one
    clause_id = list(my_cnf.get_unit_clauses())[0]
    literal = my_cnf.get_unit_clause_literal(clause_id)
    current_node = BinaryTreeNode(literal, None, UNIT_CLAUSE)
else:
    current_node = BinaryTreeNode(get_random_var(), None)

while True:

    if DEBUG:
        print("Current node is:")
        print(current_node.var)
        print(current_node.type)
        print("Truth explored = ", current_node.true_explored)
        print("False explored = ", current_node.false_explored)

    # IF NODE HAS BEEN EXPLORED : BACKTRACK
    if current_node.true_explored & current_node.false_explored:
        if DEBUG:
            print("Backtracking")
        if current_node.parent != None:
            my_cnf.backtrack()
            previous_node = current_node
            current_node = previous_node.parent
            del previous_node
        else:
            print("UNSAT!")
            sys.exit()
    # IF NODE HASN'T BEEN EXPLORED : CONTINUE SEARCH
    else:
        if current_node.type == UNIT_CLAUSE:
            if DEBUG:
                print("Present node is unexplored unit clause node")
            current_node.true_explored = True
            current_node.false_explored = True
        # TODO : Be more clever with choosing whether to assign true or false. Currently always first with true
        elif current_node.type == HARD_CHOICE & (not current_node.true_explored):
            if DEBUG:
                print("Present node is truth-unexplored hard choice node")
            current_node.true_explored = True
            current_node.var = abs(current_node.var)
        elif current_node.type == HARD_CHOICE & (not current_node.false_explored):
            if DEBUG:
                print("Present node is false-unexplored hard choice node")
            current_node.false_explored = True
            current_node.var = -abs(current_node.var)

        result = my_cnf.assign(current_node.var)

        if result == SAT:
            break
        # If assignment yielded UNSAT - backtrack
        elif result == UNSAT:
            my_cnf.backtrack()
        # Check and create unit clause nodes
        elif my_cnf.get_unit_clauses():
            if DEBUG:
                print("Creating unit clause node")
            clause_id = list(my_cnf.get_unit_clauses())[0]
            literal = my_cnf.get_unit_clause_literal(clause_id)
            current_node = BinaryTreeNode(literal, current_node, UNIT_CLAUSE)
        # If no unit clauses - check and create hard choice nodes
        else:
            current_node = BinaryTreeNode(get_random_var(), current_node)
            if DEBUG:
                print("Creating hard choice node")
                print(current_node.var)

# Will get here only if SAT

assignment = []
counter = 0

while current_node != None:
    assignment.append(current_node.var)
    if current_node.var > 0:
        counter += 1
    current_node = current_node.parent

print("SAT. Assignment is:")
print(assignment)
# Poor man's debugging, should be 729 assigned and 81 true for sudoku
print("Number of assigned variables: ", len(assignment))
print("Number of true variables: ", counter)

# TODO IDEA: CHANGE HOW CLAUSES ARE STORED?
#   Linked list type data structure - clause is an object, has parents (all variables participating)


