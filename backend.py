import re
import constraint as cp
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
    
    # Solve
    # Convert dict solution into array ToDO
    solution = problem.getSolutions()
    return solution


if __name__ == '__main__':
    print(json.dumps(backend(2, 2,
                             [[1], [2]],
                             [[2], [1]]),
                     indent=2, sort_keys=True))
    print(json.dumps(backend(2, 3,
                             [[1], [2]],
                             [[1], [1], [1]],
                             [(0, 1)]),
                     indent=2, sort_keys=True))
