DEBUG = False

class SearchTreeNode:
    def __init__(self, var, parent):
        self.var = var
        self.parent = parent

    def is_explored(self):
        raise NotImplementedError('Pure virtual is_explored method is undefined!')

    def explore(self):
        raise NotImplementedError('Pure virtual explore method is undefined!')


class SplitNode(SearchTreeNode):
    def __init__(self, var, parent):
        self.true_explored = False
        self.false_explored = False
        super().__init__(var, parent)

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

        return self.var

class PureLiteralNode(SearchTreeNode):
    def __init__(self, var, parent):
        self.explored = False
        super().__init__(var, parent)

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True
        return self.var

class UnitClauseNode(SearchTreeNode):
    def __init__(self, var, parent):
        self.explored = False
        super().__init__(var, parent)

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True
        return self.var
