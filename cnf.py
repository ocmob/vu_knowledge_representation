import re
import random
from enum import Enum

DEBUG = False

# ClausalNormalForm action type enum
class Action(Enum):
    RM_CLAUSE = 0
    RM_LITERAL = 1
    ASSIGN = 2

# Data structure for keeping and organizing the current status of the problem
class ClausalNormalForm:

    def __init__(self, dimacs_files, search_cmp):
        self.search_cmp = search_cmp

        # First pass: go over DIMACS and create list of clauses. Using modified code from:
	# https://stackoverflow.com/questions/28890268/parse-dimacs-cnf-file-python
        temp_clause_list = [[]]

        self.unassigned_vars = set()
        self.current_cnf = {}
        self.op_stack = []

        for dimacs_file in dimacs_files:
            h_sat_file = open(dimacs_file, 'r')

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

        for search_cmp in self.search_cmp:
            search_cmp.link_cnf(self)

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
                for search_comp in self.search_cmp:
                    search_comp.init_with_clause(clause, clause_id)

                self.current_cnf[clause_id] = clause

        h_sat_file.close()


    def get_unassigned(self):
        return self.unassigned_vars


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
        ops_single_step.append( (Action.ASSIGN, None, var) )
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
                ops_single_step.append( (Action.RM_CLAUSE, clause_id, clause) )

                for search_comp in self.search_cmp:
                    search_comp.rm_clause(clause, clause_id)

                del self.current_cnf[clause_id]

            elif -assignment in clause:
                if DEBUG:
                    print("NOT Assignment found. Removing literal")

                # Remember that we removed this literal
                ops_single_step.append( (Action.RM_LITERAL, clause_id, -assignment) )

                for search_comp in self.search_cmp:
                    search_comp.rm_literal(-assignment, clause_id)

                self.current_cnf[clause_id].remove(-assignment)

                # If empty set detected: UNSAT. Exit loop and report back
                if not bool(self.current_cnf[clause_id]):
                    status = False
                    if DEBUG: 
                        print("UNSAT FOUND")
                    break

        # If the cnf is empty: report SAT!
        if not self.current_cnf:
            status = True
        else:
            self.op_stack.append(ops_single_step)

        return status


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
                if action == Action.RM_CLAUSE:
                    if DEBUG:
                        print("undoing RM_CLAUSE:")
                        print("clause_id: {}, operand: {}".format(clause_id, operand))

                    for search_comp in self.search_cmp:
                        search_comp.undo_rm_clause(operand, clause_id)

                    self.current_cnf[clause_id] = operand

                # Restore deleted literals
                elif action == Action.RM_LITERAL:
                    if DEBUG:
                        print("undoing RM_LITERAL:")
                        print("clause_id: {}, operand: {}".format(clause_id, operand))
                        print("clause: {}".format(self.get_clause(clause_id)))

                    for search_comp in self.search_cmp:
                        search_comp.undo_rm_literal(operand, clause_id)

                    self.current_cnf[clause_id].add(operand)

                # Restore variables to unassigned_vars 
                elif action == Action.ASSIGN:
                    if DEBUG:
                        print("undoing ASSIGN:")
                        print("operand: {}".format(operand))

                    self.unassigned_vars.add(operand)

    def get_clause(self, clause_id):
        return self.current_cnf[clause_id]

    def get_random_var(self):
        variables = self.get_unassigned()
        var = random.sample(variables, 1)[0]
        return var
