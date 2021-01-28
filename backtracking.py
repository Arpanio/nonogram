import re
from random import sample
from typing import List, Tuple, Dict

solution_list: List[List[int]] = []


def valid(s: List[int], r: List[Tuple], c: List[Tuple]):
    s_all: List[int] = s.copy() + [-1]*(len(r)*len(c) - len(s))
    grid: Dict[int, List] = {}
    row: int = 0
    for i in range(0, len(s_all), len(c)):
        grid[row] = s_all[i:(i + len(c))]
        row += 1
    
    # Check row and column constraints
    for row in grid.keys():
        # Ensure row sum is not exceeded
        row_sum_max = sum(r[row])
        row_sum_now = sum([1 if r == 1 else 0 for r in grid[row]])
        if row_sum_now > row_sum_max:
            return False
        
        # If row sum is not exceeded, can they still be obtained from the blank cells?
        sum_from_blank = sum([1 if r == -1 else 0 for r in grid[row]])
        if row_sum_now + sum_from_blank < row_sum_max:
            return False
        
        # Are grouping requirements met?
        if sum_from_blank != 0:
            # Blank cells exist. Assume True.
            continue
        else:
            str_ = "".join([str(a) for a in grid[row]])
            groups = re.split('0+', str_)
            groups = [g for g in groups if g != '']
            group_sums = tuple([len(g) for g in groups])
            if group_sums != r[row]:
                return False
    
    for col in range(len(c)):
        col_values = []
        for row in grid.keys():
            col_values.append(grid[row][col])
        
        # Ensure column sum is not exceeded
        col_sum_max = sum(c[col])
        col_sum_now = sum([1 if c == 1 else 0 for c in col_values])
        if col_sum_now > col_sum_max:
            return False
        
        # If col sum is not exceeded, can they still be obtained from the blank cells?
        sum_from_blank = sum([1 if r == -1 else 0 for r in col_values])
        if col_sum_now + sum_from_blank < col_sum_max:
            return False

        # Are grouping requirements met?
        if sum_from_blank != 0:
            # Blank cells exist. Assume True.
            continue
        else:
            str_ = "".join([str(a) for a in col_values])
            groups = re.split('0+', str_)
            groups = [g for g in groups if g != '']
            group_sums = tuple([len(g) for g in groups])
            if group_sums != c[col]:
                return False
    
    # Both row and column checks passed
    return True


def extend(row_args: List[Tuple], col_args: List[Tuple], partial_solution: List[int]):
    global solution_list
    if len(partial_solution) == len(row_args) * len(col_args):
        solution_list.append(partial_solution.copy())
        return
    
    # Define move list based on how sparse the row/column sum is
    # move_row, move_col = len(partial_solution) % len(row_args), int(len(partial_solution)/len(row_args)) % len(col_args)
    for move in sample([0, 1], k=2):
        partial_solution.append(move)
        if not valid(partial_solution, row_args, col_args):
            # Backtrack
            partial_solution.pop()
            continue
        extend(row_args, col_args, partial_solution)
        partial_solution.pop()
    return


if __name__ == "__main__":
    # row_args = [(1, ), (2, )]
    # col_args = [(2, ), (1, )]
    # row_args = [(1, ), (2, )]
    # col_args = [(1, ), (1, ), (1, )]
    # row_args = [(4, ), (4, ), (2, ), (9, ), (10, ), (10, ), (9, ), (2, ), (5, ), (5, )]
    # col_args = [(2, ), (4, ), (4, ), (4, 2, ), (4, 2, ), (2, 4, 2, ), (2, 7, ), (10, ), (7, ), (4, )]
    # The below doesn't finish running
    # row_args = [
    #     (6, ), (2, 9, ), (6, 1, 1, 1, ), (4, 1, 5, ), (2, 5, ),
    #     (1, 1, 4, ), (2, 4, 2, 3, ), (3, 3, 1, 4, ), (2, 2, 2, 4, ),
    #     (4, 2, 3, 3, ), (2, 2, 2, 1, 2, ), (1, 1, 2, 3, 1, ), (2, 1, 3, 2, 1, ), (3, 2, 2, 2, 3, ),
    #     (5, 2, 2, 3, ), (5, 2, 2, 2, ), (7, 3, 5, ), (1, 3, 9, ), (3, 9, )
    # ]
    # col_args = [
    #     (6, ), (2, 2, 2, ), (1, 1, 1, ), (2, 2, 2, 2, ), (5, 3, 1, ),
    #     (4, 1, 3, 1, ), (3, 2, 4, 1, ), (2, 3, 8, ), (2, 3, 3, ), (3, 2, 2, ),
    #     (2, 1, 1, 2, ), (3, 7, ), (2, 2, 3, 4, ), (3, 9, 3, ), (2, 1, 3, 3, 2, ),
    #     (1, 2, 3, 5, ), (1, 6, 2, 3, ), (9, 4, 3, ), (9, 6, ), (2, 13, )
    # ]
    # The below also takes a long time to run (didn't finish in < 10 minutes)
    # row_args = [
    #     (5, ), (1, 3, ), (6, ), (2, 5, ), (3, 4, ),
    #     (3, 7, ), (3, 10, ), (3, 11, ), (5, 7, ), (5, 5, ),
    #     (5, 6, ), (13, ), (9, ), (1, 1, ), (2, 1, 4, )
    # ]
    # col_args = [
    #     (6, ), (8, ), (9, ), (4, ), (6, ),
    #     (2, 5, ), (1, 1, 3, 2, 1, ), (8, 2, ), (1, 7, 2, 1, ),
    #     (9, 3, ), (13, 1, ), (3, 8, 1, ), (8, 1, ), (9, ), (5, )
    # ]
    row_args = [
        (2, ), (4, ), (3, 3, ), (5, 1, 1, ), (3, 1,),
        (10, ), (10, ), (1, ), (3, ), (10, )
    ]
    col_args = [
        (4, 1, ), (4, 1, ), (4, 1, ), (2, 2, 1, ), (2, 2, 1, ),
        (2, 2, 1, ), (2, 2, 2, ), (10, ), (2, 2, 2, ), (2, 2, 1, )
    ]
    extend(row_args, col_args, [])
    # Display
    for i, solution in enumerate(solution_list):
        print(f'Solution: {i + 1}/{len(solution_list)}')
        for r in range(0, len(row_args)*len(col_args), len(col_args)):
            print(solution[r:(r + len(col_args))])
        print('\n')
