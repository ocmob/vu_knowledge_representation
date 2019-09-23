import random
import search_tree

DEBUG = False

# -- CLASS DEFINITIONS

class SearchComponent:
    nodes = 0


    def get_metrics(self):
        return self.nodes
#    def rm_literal:
#        pass
#    def rm_clause:
#        pass
#    def undo_rm_literal:
#        pass
#    def undo_rm_clause:
#        pass
#    def init_with_clause(self, clause, clause_id):
#        pass
#    def ready:
#        pass
#    def generate_node:
#        pass


class JWTwoSided(SearchComponent):
    jwscore = {}
    jwscore_sided = {}

    def reset(self):
        self.nodes = 0
        self.jwscore = {}
        self.jwscore_sided = {}

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.jwscore[var] = 0
            self.jwscore_sided[var] = 0
            self.jwscore_sided[-var] = 0

        self.cnf_instance = cnf

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            var = abs(literal)

            self.jwscore[var] += 2**(-len(clause))
            self.jwscore_sided[literal] += 2**(-len(clause))

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            var = abs(literal)

            self.jwscore[var] -= 2**(-len(operand))
            self.jwscore_sided[literal] -= 2**(-len(operand))

    def undo_rm_clause(self, operand, clause_id):
        clause = operand
        for literal in clause:
            var = abs(literal)

            self.jwscore[var] += 2**(-len(clause))
            self.jwscore_sided[literal] += 2**(-len(clause))

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 
        for literal in clause:
            var = abs(literal)
            if literal == operand:
                self.jwscore[var] -= 2**(-len(clause))
                self.jwscore_sided[literal] -= 2**(-len(clause))
            else:
                self.jwscore[var] -= 2**(-len(clause))
                self.jwscore[var] += 2**(-(len(clause)-1))

                self.jwscore_sided[literal] -= 2**(-len(clause))
                self.jwscore_sided[literal] += 2**(-(len(clause)-1))

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        var = abs(operand)
        self.jwscore[var] += 2**(-(len(clause)+1))
        self.jwscore_sided[operand] += 2**(-(len(clause)+1))

        for literal in clause:
            var = abs(literal)
            self.jwscore[var] -= 2**(-len(clause))
            self.jwscore[var] += 2**(-(len(clause)+1))

            self.jwscore_sided[literal] -= 2**(-len(clause))
            self.jwscore_sided[literal] += 2**(-(len(clause)+1))

    def ready(self):
        return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.jwscore.items() if k in keys]
        score_list.sort( key = lambda tup : tup[1], reverse=True )
        if self.jwscore_sided[score_list[0][0]] > self.jwscore_sided[-score_list[0][0]]:
            literal = score_list[0][0]
        else:
            literal = -score_list[0][0]

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)

class LeastConstrainingComponent(SearchComponent):
    lcscore = {}

    def reset(self):
        self.lcscore = {}
        self.nodes = 0

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.lcscore[var] = 0

        self.cnf_instance = cnf

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(operand))
            else:
                self.lcscore[var] += 2**(-len(operand))

    def undo_rm_clause(self, operand, clause_id):
        clause = operand
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 
        for literal in clause:
            var = abs(literal)
            if literal == operand:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                else:
                    self.lcscore[var] += 2**(-len(clause))
            else:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                    self.lcscore[var] += 2**(-(len(clause)-1))
                else:
                    self.lcscore[var] += 2**(-len(clause))
                    self.lcscore[var] -= 2**(-(len(clause)-1))

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        var = abs(operand)
        if operand > 0:
            self.lcscore[var] += 2**(-(len(clause)+1))
        else:
            self.lcscore[var] -= 2**(-(len(clause)+1))

        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(clause))
                self.lcscore[var] += 2**(-(len(clause)+1))
            else:
                self.lcscore[var] += 2**(-len(clause))
                self.lcscore[var] -= 2**(-(len(clause)+1))

    def ready(self):
        return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        score_list.sort( key = lambda tup : abs(tup[1]), reverse=True )
        if score_list[0][1] > 0:
            literal = score_list[0][0]
        else:
            literal = -score_list[0][0]

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)

class MostConstrainingRandMeta(SearchComponent):
    lcscore = {}

    def reset(self):
        self.lcscore = {}
        self.nodes = 0

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.lcscore[var] = 0

        self.cnf_instance = cnf

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(operand))
            else:
                self.lcscore[var] += 2**(-len(operand))

    def undo_rm_clause(self, operand, clause_id):
        clause = operand
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 
        for literal in clause:
            var = abs(literal)
            if literal == operand:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                else:
                    self.lcscore[var] += 2**(-len(clause))
            else:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                    self.lcscore[var] += 2**(-(len(clause)-1))
                else:
                    self.lcscore[var] += 2**(-len(clause))
                    self.lcscore[var] -= 2**(-(len(clause)-1))

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        #breakpoint()

        var = abs(operand)
        if operand > 0:
            self.lcscore[var] += 2**(-(len(clause)+1))
        else:
            self.lcscore[var] -= 2**(-(len(clause)+1))

        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(clause))
                self.lcscore[var] += 2**(-(len(clause)+1))
            else:
                self.lcscore[var] += 2**(-len(clause))
                self.lcscore[var] -= 2**(-(len(clause)+1))

    def ready(self):
        if random.random() > 0.5:
            return False
        else: 
            return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        score_list.sort( key = lambda tup : abs(tup[1]), reverse=False )
        if score_list[0][1] > 0:
            literal = score_list[0][0]
        else:
            literal = -score_list[0][0]

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)

class MostConstrainingMeta(SearchComponent):
    lcscore = {}

    def __init__(self, threshold):
        self.threshold = threshold

    def reset(self):
        self.lcscore = {}
        self.nodes = 0

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.lcscore[var] = 0

        self.cnf_instance = cnf

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(operand))
            else:
                self.lcscore[var] += 2**(-len(operand))

    def undo_rm_clause(self, operand, clause_id):
        clause = operand
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 
        for literal in clause:
            var = abs(literal)
            if literal == operand:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                else:
                    self.lcscore[var] += 2**(-len(clause))
            else:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                    self.lcscore[var] += 2**(-(len(clause)-1))
                else:
                    self.lcscore[var] += 2**(-len(clause))
                    self.lcscore[var] -= 2**(-(len(clause)-1))

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        #breakpoint()

        var = abs(operand)
        if operand > 0:
            self.lcscore[var] += 2**(-(len(clause)+1))
        else:
            self.lcscore[var] -= 2**(-(len(clause)+1))

        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(clause))
                self.lcscore[var] += 2**(-(len(clause)+1))
            else:
                self.lcscore[var] += 2**(-len(clause))
                self.lcscore[var] -= 2**(-(len(clause)+1))

    def ready(self):
        keys = self.cnf_instance.get_unassigned()
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        score_list.sort( key = lambda tup : abs(tup[1]), reverse=False )

        if abs(score_list[0][1]) > abs(self.threshold):
            return False
        else: 
            return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        score_list.sort( key = lambda tup : abs(tup[1]), reverse=False )
        if score_list[0][1] > 0:
            literal = score_list[0][0]
        else:
            literal = -score_list[0][0]

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)

class MostConstrainingComponent(SearchComponent):
    lcscore = {}

    def reset(self):
        self.lcscore = {}
        self.nodes = 0

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.lcscore[var] = 0

        self.cnf_instance = cnf

    def init_with_clause(self, clause, clause_id):
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_clause(self, operand, clause_id):
        for literal in operand:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(operand))
            else:
                self.lcscore[var] += 2**(-len(operand))

    def undo_rm_clause(self, operand, clause_id):
        clause = operand
        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] += 2**(-len(clause))
            else:
                self.lcscore[var] -= 2**(-len(clause))

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 
        for literal in clause:
            var = abs(literal)
            if literal == operand:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                else:
                    self.lcscore[var] += 2**(-len(clause))
            else:
                if literal > 0:
                    self.lcscore[var] -= 2**(-len(clause))
                    self.lcscore[var] += 2**(-(len(clause)-1))
                else:
                    self.lcscore[var] += 2**(-len(clause))
                    self.lcscore[var] -= 2**(-(len(clause)-1))

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        #breakpoint()

        var = abs(operand)
        if operand > 0:
            self.lcscore[var] += 2**(-(len(clause)+1))
        else:
            self.lcscore[var] -= 2**(-(len(clause)+1))

        for literal in clause:
            var = abs(literal)
            if literal > 0:
                self.lcscore[var] -= 2**(-len(clause))
                self.lcscore[var] += 2**(-(len(clause)+1))
            else:
                self.lcscore[var] += 2**(-len(clause))
                self.lcscore[var] -= 2**(-(len(clause)+1))

    def ready(self):
        return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        score_list.sort( key = lambda tup : abs(tup[1]), reverse=False )
        if score_list[0][1] > 0:
            literal = score_list[0][0]
        else:
            literal = -score_list[0][0]

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class TruthFirstComponent(SearchComponent):
    nodes = 0

    def reset(self):
        self.nodes = 0

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

    def ready(self):
        return True

    def generate_node(self, current_node):
        unassigned_vars = list(self.cnf_instance.get_unassigned())
        unassigned_vars.sort()
        variable = unassigned_vars.pop()
        self.nodes += 1
        return search_tree.SplitNode(variable, current_node)


class RandomChoiceComponent(SearchComponent):
    nodes = 0

    def reset(self):
        self.nodes = 0
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

    def ready(self):
        return True

    def generate_node(self, current_node):
        variable = self.cnf_instance.get_random_var()
        literal = variable if random.random() < 0.5 else -variable
        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class UnitClauseComponent(SearchComponent):
    unit_clauses = set()
    nodes = 0
    def reset(self):
        self.unit_clauses = set()
        self.nodes = 0

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
        return search_tree.UnitClauseNode(literal, current_node)

class PureLiteralComponent(SearchComponent):
    nodes = 0
    literal_counts = {}
    pure_literals = set()

    def reset(self):
        self.literal_counts = {}
        self.pure_literals = set()
        self.nodes = 0

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
        return search_tree.PureLiteralNode(literal, current_node)
