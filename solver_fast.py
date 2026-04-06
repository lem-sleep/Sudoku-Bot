"""
Fast Sudoku solver using bitmask constraint propagation + backtracking with MRV heuristic.
Replaces the constraint-based solver in sudoku.py for speed.
"""

def solve(board):
    """
    Solve a 9x9 sudoku board in-place using bitmask backtracking.
    board: list of 9 lists of 9 ints (0 = empty).
    Returns (solved_board, empties_board) or (board, empties) if unsolvable.
    empties_board has non-zero values only in cells that were originally 0.
    """
    FULL = 0x1FF  # bits 0-8 = digits 1-9

    # Track which digits are used per row, col, box
    row_used = [0] * 9
    col_used = [0] * 9
    box_used = [0] * 9

    empties = []

    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v != 0:
                bit = 1 << (v - 1)
                row_used[r] |= bit
                col_used[c] |= bit
                box_used[(r // 3) * 3 + c // 3] |= bit
            else:
                empties.append((r, c))

    solved_board = [row[:] for row in board]
    empties_board = [[0] * 9 for _ in range(9)]

    def backtrack(idx):
        if idx == len(empties):
            return True

        r, c = empties[idx]
        b = (r // 3) * 3 + c // 3
        available = FULL & ~(row_used[r] | col_used[c] | box_used[b])

        while available:
            # Extract lowest set bit
            bit = available & (-available)
            available ^= bit
            digit = bit.bit_length()  # 1-indexed

            row_used[r] |= bit
            col_used[c] |= bit
            box_used[b] |= bit
            solved_board[r][c] = digit

            if backtrack(idx + 1):
                return True

            row_used[r] ^= bit
            col_used[c] ^= bit
            box_used[b] ^= bit
            solved_board[r][c] = 0

        return False

    # Sort empties by MRV (fewest candidates first) for faster pruning
    def count_candidates(r, c):
        b = (r // 3) * 3 + c // 3
        available = FULL & ~(row_used[r] | col_used[c] | box_used[b])
        return bin(available).count('1')

    empties.sort(key=lambda rc: count_candidates(rc[0], rc[1]))

    if backtrack(0):
        for r, c in empties:
            empties_board[r][c] = solved_board[r][c]
        return solved_board, empties_board
    else:
        return board, empties_board
