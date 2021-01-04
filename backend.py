import re
import constraint as cp
import numpy as np
import json
from typing import List, Tuple
from functools import partial


def detect_groups(group_sums, *args):
    str_ = "".join([str(a) for a in list(args)])
    groups = re.split('0+', str_)
    groups = [g for g in groups if g != '']
    result_sums = [len(g) for g in groups]
    if group_sums != result_sums:
        return False
    else:
        return True


def backend(r: int, c: int,
            r_num: List[List[int]],
            c_num: List[List[int]],
            crossed_cells: List[Tuple[int, int]] = None):
    # Setup CP problem object
    problem = cp.Problem()
    
    # Create variables
    variables = [f"A_{row}_{col}" for row in range(r) for col in range(c)]
    problem.addVariables(variables, [0, 1])
    
    # Create starting constraints (crossed-out cells)
    if crossed_cells and len(crossed_cells) != 0:
        crossed_variables = [f"A_{row}_{col}" for row, col in crossed_cells]
        problem.addConstraint(cp.InSetConstraint({0}), crossed_variables)
    
    # Create row-sum and column-sum constraints
    for row in range(r):
        constraint_vars = [v for v in variables if re.search(f"_{row}_", v)]
        row_sum = sum(r_num[row])
        
        # Add constraint to CP object
        # Doesn't work because of https://github.com/python-constraint/python-constraint/issues/48
        # Understand what's happening ToDo
        # problem.addConstraint(lambda *args: sum(args) == row_sum, constraint_vars)
        
        problem.addConstraint(cp.ExactSumConstraint(row_sum), constraint_vars)
        
        # multi-group constraints
        group_details = r_num[row]
        constraint_group = partial(detect_groups, group_details)
        problem.addConstraint(constraint_group, constraint_vars)
        
        # Constraints to speed-up processing
        if row_sum == c:
            # The whole row must be 1's
            problem.addConstraint(cp.InSetConstraint({1}), constraint_vars)
        
    for col in range(c):
        constraint_vars = [v for v in variables if re.search(f"_{col}$", v)]
        col_sum = sum(c_num[col])
        
        # Add constraint to CP object
        # problem.addConstraint(lambda *args: sum(args) == col_sum, constraint_vars)
        problem.addConstraint(cp.ExactSumConstraint(col_sum), constraint_vars)

        # multi-group constraints
        group_details = c_num[col]
        constraint_group = partial(detect_groups, group_details)
        problem.addConstraint(constraint_group, constraint_vars)
        
        # Constraints to speed-up processing
        if col_sum == r:
            # The whole column must be 1's
            problem.addConstraint(cp.InSetConstraint({1}), constraint_vars)
    
    # Solve
    # Convert dict solution into array ToDO
    solutions = problem.getSolutions()
    solutions_array = []
    for solution in solutions:
        variables_in_order = [solution[k] for k in sorted(solution)]
        solutions_array.append(np.array(variables_in_order).reshape((r, c)))
    
    return solutions_array


if __name__ == '__main__':
    # print(json.dumps(backend(2, 2,
    #                          [[1], [2]],
    #                          [[2], [1]]),
    #                  indent=2, sort_keys=True))
    # print(json.dumps(backend(2, 3,
    #                          [[1], [2]],
    #                          [[1], [1], [1]],
    #                          [(0, 1)]),
    #                  indent=2, sort_keys=True))
    # print(json.dumps(backend(10, 10,
    #                          [[4], [4], [2], [9], [10], [10], [9], [2], [5], [5]],
    #                          [[2], [4], [4], [4, 2], [4, 2], [2, 4, 2], [2, 7], [10], [7], [4]]),
    #                  indent=2, sort_keys=True))
    # print(json.dumps(backend(10, 10,
    #                          [[5], [3, 1], [3, 1], [1, 2, 1], [10], [9], [3], [3], [3], [3]],
    #                          [[2], [2], [2], [2], [2], [10], [10], [3, 6], [1, 2], [6]]),
    #                  indent=2, sort_keys=True))
    print(backend(2, 2,
                  [[1], [2]],
                  [[2], [1]]))
    print(backend(2, 3,
                  [[1], [2]],
                  [[1], [1], [1]],
                  [(0, 1)]))
    print(backend(10, 10,
                  [[4], [4], [2], [9], [10], [10], [9], [2], [5], [5]],
                  [[2], [4], [4], [4, 2], [4, 2], [2, 4, 2], [2, 7], [10], [7], [4]]))
    print(backend(10, 10,
                  [[5], [3, 1], [3, 1], [1, 2, 1], [10], [9], [3], [3], [3], [3]],
                  [[2], [2], [2], [2], [2], [10], [10], [3, 6], [1, 2], [6]]))
    print(backend(10, 10,
                  [[5], [2], [3], [9], [9], [1], [3], [2], [5], [2]],
                  [[2], [3], [2], [9], [9], [9], [2], [4], [2], [3]]))
