import re
import constraint as cp


def detect_groups():
    pass


def contiguity(*args):
    str_ = "".join([str(a) for a in list(args)])
    if re.search("10+1", str_):
        return False
    else:
        return True


def backend(r: int, c: int, r_num: list, c_num: list):
    # Setup CP problem object
    problem = cp.Problem()
    
    # Create variables
    variables = [f"A_{row}_{col}" for row in range(r) for col in range(c)]
    problem.addVariables(variables, [0, 1])
    
    # Create starting constraints (crossed-out cells)
    # ToDo
    
    # Create row-sum and column-sum constraints
    for row in range(r):
        constraint_vars = [v for v in variables if re.search(f"_{row}_", v)]
        row_sum = sum(r_num[row])
        
        # Add constraint to CP object
        # Doesn't work because of https://github.com/python-constraint/python-constraint/issues/48
        # Understand what's happening
        # problem.addConstraint(lambda *args: sum(args) == row_sum, constraint_vars)
        
        problem.addConstraint(cp.ExactSumConstraint(row_sum), constraint_vars)
        problem.addConstraint(contiguity, constraint_vars)
        
    for col in range(c):
        constraint_vars = [v for v in variables if re.search(f"_{col}$", v)]
        col_sum = sum(c_num[col])
        
        # Add constraint to CP object
        # problem.addConstraint(lambda *args: sum(args) == col_sum, constraint_vars)
        problem.addConstraint(cp.ExactSumConstraint(col_sum), constraint_vars)
        problem.addConstraint(contiguity, constraint_vars)
        
    # Create multi-group constraints
    # ToDo
    
    # Solve
    return problem.getSolutions()
