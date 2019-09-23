DEBUG = False

# BinaryTreeNode node type constants
SPLIT = 1
PURE_LITERAL = 2
UNIT_CLAUSE = 3

# Binary tree node for the Davis-Putnam search
class BinaryTreeNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent


class SplitNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent
        self.type = SPLIT
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

        if DEBUG:
            print()
            print('Evaluating: ', self.var)
            #print('False: ', self.false_explored)
            #print('True: ', self.true_explored)

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
