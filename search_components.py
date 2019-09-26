import random
import search_tree

DEBUG = False

class SearchComponent:
    nodes = 0

    def get_metrics(self):
        return self.nodes

    def reset(self):
        self.nodes = 0

    def link_cnf(self,cnf):
        self.cnf_instance = cnf

    def rm_literal(self):
        raise NotImplementedError('Pure virtual rm_literal method is undefined!')

    def rm_clause(self):
        raise NotImplementedError('Pure virtual rm_clause method is undefined!')

    def undo_rm_literal(self):
        raise NotImplementedError('Pure virtual undo_rm_literal method is undefined!')

    def undo_rm_clause(self):
        raise NotImplementedError('Pure virtual undo_rm_clause method is undefined!')

    def init_with_clause(self, clause, clause_id):
        raise NotImplementedError('Pure virtual init_with_clause method is undefined!')

    def ready(self):
        raise NotImplementedError('Pure virtual ready method is undefined!')

    def generate_node(self):
        raise NotImplementedError('Pure virtual generate_node method is undefined!')


class JWTwoSided(SearchComponent):

    def reset(self):
        self.jwscore = {}
        self.jwscore_sided = {}
        super().reset()

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.jwscore[var] = 0
            self.jwscore_sided[var] = 0
            self.jwscore_sided[-var] = 0
        super().link_cnf(cnf)

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
        var, value = max(score_list, key = lambda tup : tup[1])
        if self.jwscore_sided[var] > self.jwscore_sided[-var]:
            literal = var
        else:
            literal = -var

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class XConstrainingFamily(SearchComponent):
    def reset(self):
        self.lcscore = {}
        super().reset()

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            self.lcscore[var] = 0

        super().link_cnf(cnf)

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
        raise NotImplementedError('Pure virtual ready method is undefined!')

    def generate_node(self, current_node):
        raise NotImplementedError('Pure virtual generate_node method is undefined!')


class LeastConstrainingComponent(XConstrainingFamily):
    def ready(self):
        return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        var, value = max(score_list, key = lambda tup : abs(tup[1]))
        if value > 0:
            literal = var
        else:
            literal = -var

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class MostConstrainingRandMeta(XConstrainingFamily):
    def ready(self):
        if random.random() > 0.5:
            return False
        else: 
            return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        var, value = min(score_list, key = lambda tup : abs(tup[1]))
        if value > 0:
            literal = var
        else:
            literal = -var

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class MostConstrainingMeta(XConstrainingFamily):
    def __init__(self, threshold):
        self.threshold = threshold

    def ready(self):
        keys = self.cnf_instance.get_unassigned()
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        var, value = min(score_list, key = lambda tup : abs(tup[1]))

        if abs(value) > abs(self.threshold):
            return False
        else: 
            return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        var, value = min(score_list, key = lambda tup : abs(tup[1]))
        if value > 0:
            literal = var
        else:
            literal = -var

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class MostConstrainingComponent(XConstrainingFamily):
    def ready(self):
        return True

    def generate_node(self, current_node):
        keys = self.cnf_instance.get_unassigned()
        
        score_list = [(k, v) for k, v in self.lcscore.items() if k in keys]
        var, value = min(score_list, key = lambda tup : abs(tup[1]))
        if value > 0:
            literal = var
        else:
            literal = -var

        self.nodes += 1
        return search_tree.SplitNode(literal, current_node)


class DetTruthFirstComponent(SearchComponent):
    nodes = 0

    def reset(self):
        super().reset()

    def link_cnf(self, cnf_instance):
        super().link_cnf(cnf_instance)

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
        super().reset()

    def link_cnf(self, cnf_instance):
        super().link_cnf(cnf_instance)

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

    def reset(self):
        self.no_clauses = 0
        self.unit_clauses = {}
        super().reset()

    def link_cnf(self, cnf_instance):
        for var in list(cnf_instance.get_unassigned()):
            self.unit_clauses[var] = set()
            self.unit_clauses[-var] = set()

        super().link_cnf(cnf_instance)

    def init_with_clause(self, clause, clause_id):
        if len(clause) == 1:
            self.no_clauses += 1
            self.unit_clauses[ next(iter(clause)) ].add(clause_id)

    def rm_clause(self, operand, clause_id):
        if len(operand) == 1:
            self.no_clauses -= 1
            self.unit_clauses[ next(iter(operand)) ].remove(clause_id)

    def rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id) 

        if len(clause) == 2:
            clause_no_op = clause.copy()
            clause_no_op.remove(operand)
            self.no_clauses += 1
            self.unit_clauses[ next(iter(clause_no_op)) ].add(clause_id)
        elif len(clause) == 1:
            self.no_clauses -= 1
            self.unit_clauses[ operand ].remove(clause_id)

    def undo_rm_literal(self, operand, clause_id):
        clause = self.cnf_instance.get_clause(clause_id)

        if len(clause) == 1:
            self.no_clauses -= 1
            self.unit_clauses[ next(iter(clause)) ].remove(clause_id)
        elif len(clause) == 0:
            self.no_clauses += 1
            self.unit_clauses[ operand ].add(clause_id)

    def undo_rm_clause(self, operand, clause_id):
        if len(operand) == 1:
            self.no_clauses += 1
            self.unit_clauses[ next(iter(operand)) ].add(clause_id)


    def get_unit_clause_literal(self):
        self.literal_counts = list(self.unit_clauses.items())
        literal = max(self.literal_counts, key = lambda tup : len(tup[1]))[0]
        return literal


    def ready(self):
        if self.no_clauses == 0:
            return False
        else:
            return True

    def generate_node(self, current_node):
        literal = self.get_unit_clause_literal()
        self.nodes += 1
        return search_tree.UnitClauseNode(literal, current_node)


class PureLiteralComponent(SearchComponent):
    pure_literals = set()

    def reset(self):
        self.literal_counts = {}
        self.pure_literals = set()
        super().reset()

    def link_cnf(self, cnf):
        for var in list(cnf.get_unassigned()):
            if DEBUG:
                print("Creating new literal entry: {}".format(var))
            self.literal_counts[var] = 0
            self.literal_counts[-var] = 0

        super().link_cnf(cnf)

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
