import numpy as np
import copy
from line_profiler import LineProfiler


class Tree(object):
    def __init__(self, data):
        self.parent = None
        self.children = list()
        self.data = data

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def add_children(self, nodes):
        for node in nodes:
            self.add_child(node)

    def get_lineage(self):
        lineage = list()
        lineage.append(self)
        if self.parent != None:
            lineage = lineage + self.parent.get_lineage()
        return lineage


def make_board(N, boundary, colored):
    board = np.zeros([N * 2 + 1, N * 2 + 1], dtype=int)
    if colored:
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                if (i % 2 == 1) and (j % 2 == 1):
                    board[(i, j)] = 2
                if (i % 2 == 0) ^ (j % 2 == 0):
                    board[(i, j)] = 1
    if boundary:
        for i in range(board.shape[0]):
            board[(i, 0)] = 1
            board[(i, board.shape[1] - 1)] = 1
        for j in range(board.shape[1]):
            board[(0, j)] = 1
            board[(board.shape[0] - 1, j)] = 1
    for i in range(0, board.shape[0], 2):
        for j in range(0, board.shape[1], 2):
            board[(i, j)] = 0
    return board


def columnize_tree(tree):
    columns = _columnize_tree(tree)
    for i in range(len(columns)):
        columns[i].reverse
    columns = [[node.data for node in c] for c in columns]
    return columns


def _columnize_tree(tree):
    columns = list()
    if len(tree.children) != 0:
        for child in tree.children:
            columns = columns + _columnize_tree(child)
    else:
        columns = columns + [tree.get_lineage()]
    return columns


# def get_all_moves(board):
#     moves = list()
#     for i in range(board.shape[0]):
#         for j in range(board.shape[1]):
#             if (i % 2 == 0) ^ (j % 2 == 0):
#                 moves.append((i, j))
#     return moves


def get_cells_near_move(board, move):
    cells = list()
    if move[0] % 2 == 0:  # vertical line
        if move[0] != 0:
            cells.append((move[0] - 1, move[1]))
        if move[0] != board.shape[0] - 1:
            cells.append((move[0] + 1, move[1]))
    else:  # horizontal line
        if move[1] != 0:
            cells.append((move[0], move[1] - 1))
        if move[1] != board.shape[1] - 1:
            cells.append((move[0], move[1] + 1))
    return cells


def move_squares(board, move):
    board[move] = 1  # make the move
    cells = get_cells_near_move(board, move)
    any_squares = any([get_cell_value(board, cell) == 4 for cell in cells])
    board[move] = 0
    return any_squares


def get_available_moves(board):
    root = Tree(None)
    micro_append_next_valid_moves(board, root)
    moves = columnize_tree(root)
    return moves


def get_cell_value(board, cell):
    return sum([int(board[boundary] == 1) for boundary in get_cell_boundaries(cell)])


def micro_append_next_valid_moves(board, parent_move):
    moves = get_valid_moves(board)
    for move in moves:
        child = Tree(move)
        if move_squares(board, move):
            micro_append_next_valid_moves(simulate_move(board, move), child)
        parent_move.add_child(child)


def macro_append_next_valid_moves(parent_state):
    moves = get_available_moves(parent_state.data['board'])
    for move in moves:
        new_board = simulate_moves(parent_state.data['board'], move)
        parent_state.add_child(Tree({'board': new_board, 'move': move}))


def get_valid_moves(board):
    moves = list()
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if (i % 2 == 0) ^ (j % 2 == 0):
                if board[(i, j)] != 1:
                    moves.append((i, j))
    return moves


def get_free_cells(board):
    cells = list()
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if (i % 2 == 1) and (j % 2 == 1):
                if board[(i, j)] == 0:
                    cells.append((i, j))
    return cells


def make_colored_board(N):
    board = np.zeros([N * 2 + 1, N * 2 + 1], dtype=int)
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if (i % 2 == 1) and (j % 2 == 1):
                board[(i, j)] = 2
            if (i % 2 == 0) ^ (j % 2 == 0):
                board[(i, j)] = 1
    return board


def simulate_move(board, move):
    if move == None:
        return copy.copy(board)
    else:
        new_board = copy.copy(board)
        new_board[move] = 1
        return new_board


def simulate_moves(board, moves):
    new_board = copy.copy(board)
    for move in moves:
        if move != None:
            new_board[move] = 1
    return new_board


def get_cell_boundaries(cell):
    return [(cell[0], cell[1] - 1), (cell[0], cell[1] + 1), (cell[0] - 1, cell[1]), (cell[0] + 1, cell[1])]


def build_search_tree(parent_state, depth):
    macro_append_next_valid_moves(parent_state)
    if depth > 0:
        for child_state in parent_state.children:
            build_search_tree(child_state, depth - 1)



grid_size = 3
board = make_board(grid_size, False, False)
# print(board)
moves = [(1,2),(2,1),(0,1),(0,3),(1,4)]
board = simulate_moves(board, moves)

root = Tree({'board': board})
prof = LineProfiler()

# prof.add_function(build_search_tree)
# prof.add_function(macro_append_next_valid_moves)
# prof.add_function(simulate_moves)
# prof.add_function(get_available_moves)
# prof.add_function(micro_append_next_valid_moves)
# prof.add_function(get_valid_moves)
prof.add_function(move_squares)
# prof.add_function(get_cell_value)

prof.runcall(build_search_tree, root, 2)
prof.print_stats()