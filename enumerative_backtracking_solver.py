import numpy as np
import itertools as it
import re
from typing import List, Dict, Tuple, Set, AnyStr, Type

solution_list: List[Type[np.ndarray]] = []
placements: Dict[str, Dict[int, List[Type[np.ndarray]]]] = {}


def compute_blocks(line_len: int, blocks: Tuple):
    """
    Given line and a tuple of blocks, generate valid start and stop positions for each block
    Examples:
        (line_len = 10, blocks = (1, )) : 10 possible options [(0, ), (1, ) ... (9, )]
        (line_len = 10, blocks = (3, 3, 2, )) : 1 possible option [(0, 4, 8, )]
    """
    block_buffer: List[int] = []
    for i, block in enumerate(blocks):
        if i == 0 and i == len(blocks) - 1:
            # Only 1 block
            block_buffer.append(block)
        elif i != 0 and i == len(blocks) - 1:
            # Last block out of many
            block_buffer.append(block)
        else:
            # Many blocks. Current block can be any of them except the last one
            block_buffer.append(block + 1)
    assert sum(block_buffer) <= line_len
    block_pos: List[Tuple[int, int]] = []
    start, stop = None, None
    for i in range(len(block_buffer)):
        if i == 0:
            start = 0
        else:
            start = block_pos[i - 1][0] + block_buffer[i - 1]
        stop = (line_len - 1) - sum(block_buffer[(i + 1):]) - (block_buffer[i] - 1)
        block_pos.append((start, stop))
    # For each placement of blocks, check if length constraints are met
    result: List[Tuple] = []
    for pos in it.product(*[range(start, stop + 1) for start, stop in block_pos]):
        # Check if block_buffer length between each consecutive block is met
        invalid_flag = False
        for i in range(len(pos)):
            if i == len(pos) - 1:
                block_space = line_len - pos[i]
            else:
                block_space = pos[i + 1] - pos[i]
            if block_space < block_buffer[i]:
                invalid_flag = True
                break
        if not invalid_flag:
            result.append(pos)
    return result


def enumerate_blocks(block_start: List[Tuple], block_size: Tuple, total_size: int):
    """
    Given starting position and size, generates list of arrays, each array representing placed blocks
    """
    result = []
    for option in block_start:
        line = np.zeros(total_size, dtype=np.int8)
        for start, length in zip(option, block_size):
            line[start:(start + length)] = 1
        result.append(line.copy())
    return result


def valid_groups(arg: Tuple, line: AnyStr):
    groups = re.split('0+', line)
    groups = [g for g in groups if g != '']
    group_sums = tuple([len(g) for g in groups])
    if group_sums != arg:
        return False
    else:
        return True


def valid(row_args: List[Tuple], col_args: List[Tuple], partial_solution: Type[np.ndarray],
          completed_rows: Set[int], completed_cols: Set[int]):
    global placements
    # Check row and column constraints - sum and grouping
    for r, row_constraints in enumerate(row_args):
        if r in completed_rows:
            # Strict check - sum and grouping
            if sum(row_constraints) != np.sum(partial_solution[r, :]):
                return False
            str_ = ''.join(partial_solution[r, :].astype('int').astype('str'))
            if not valid_groups(row_constraints, str_):
                return False
        elif np.all(partial_solution[r, :] == -1):
            # Row hasn't been touched yet
            continue
        else:
            # Partially solved row. Check that sum isn't exceeded and that 1's are consistent with row's placements
            if sum(row_constraints) < np.sum(partial_solution[r, :] == 1):
                return False
            consistent_ones = False
            for placement in placements['row'][r]:
                if np.all(
                        np.bitwise_and(
                            np.select([partial_solution[r, :] == -1], [0], default=partial_solution[r, :]),
                            placement
                        ) == np.select([partial_solution[r, :] == -1], [0], default=partial_solution[r, :])
                ):
                    consistent_ones = True
                    break
            if not consistent_ones:
                return False
    
    for c, col_constraints in enumerate(col_args):
        if c in completed_cols:
            # Strict check - sum and grouping
            if sum(col_constraints) != np.sum(partial_solution[:, c]):
                return False
            str_ = ''.join(partial_solution[:, c].astype('int').astype('str'))
            if not valid_groups(col_constraints, str_):
                return False
        elif np.all(partial_solution[:, c] == -1):
            # Column hasn't been touched yet
            continue
        else:
            # Partially solved column. Check that sum isn't exceeded and 1's are consistent with column's placements
            if sum(col_constraints) < np.sum(partial_solution[:, c] == 1):
                return False
            consistent_ones = False
            for placement in placements['column'][c]:
                if np.all(
                        np.bitwise_and(
                            np.select([partial_solution[:, c] == -1], [0], default=partial_solution[:, c]),
                            placement
                        ) == np.select([partial_solution[:, c] == -1], [0], default=partial_solution[:, c])
                ):
                    consistent_ones = True
                    break
            if not consistent_ones:
                return False
    
    return True


def infer_values(solution_array: Type[np.ndarray],
                 placements_dict: Dict[str, Dict[int, List[Type[np.ndarray]]]]):
    # Set cell values as 1/0 for rows. If value can be either 1 or 0, set as -1.
    for r in placements_dict['row']:
        row_ones = np.ones(solution_array.shape[1], dtype=np.int8)
        row_zeros = np.zeros(solution_array.shape[1], dtype=np.int8)
        for placement in placements_dict['row'][r]:
            row_ones = np.bitwise_and(row_ones, placement)
            row_zeros = np.bitwise_or(row_zeros, placement)
        row_ones = np.select([row_ones == 1, row_ones == 0], [1, -1])
        row_zeros = np.select([row_zeros == 0, row_zeros == 1], [0, -1])
        # Check for contradiction between cell value set by row vs cell value set by column
        for c in range(solution_array.shape[1]):
            # If cell-value via row is 0 and via col is 1 then this fails
            assert not (partial_solution[r, c] == 0 and row_ones[c] == 1)
            assert not (partial_solution[r, c] == 1 and row_zeros[c] == 0)
        solution_array[r, :] = np.select(
            [np.bitwise_and(row_ones == -1, row_zeros == -1), np.bitwise_and(row_ones == -1, row_zeros == 0),
             np.bitwise_and(row_ones == 1, row_zeros == -1), np.bitwise_and(row_ones == 1, row_zeros == 0)],
            [-1, 0, 1, -2]
        )
    # Set cell values as 1/0 for columns. If value can be either 1 or 0, set as -1.
    for c in placements_dict['column']:
        col_ones = np.ones(solution_array.shape[0], dtype=np.int8)
        col_zeros = np.zeros(solution_array.shape[0], dtype=np.int8)
        for placement in placements_dict['column'][c]:
            col_ones = np.bitwise_and(col_ones, placement)
            col_zeros = np.bitwise_or(col_zeros, placement)
        col_ones = np.select([col_ones == 1, col_ones == 0], [1, -1])
        col_zeros = np.select([col_zeros == 0, col_zeros == 1], [0, -1])
        # Check for contradiction between cell value set by row vs cell value set by column
        for r in range(solution_array.shape[0]):
            # If cell-value via row is 0 and via col is 1 then this fails
            assert not (partial_solution[r, c] == 0 and col_ones[r] == 1)
            assert not (partial_solution[r, c] == 1 and col_zeros[r] == 0)
        solution_array[:, c] = np.select(
            [np.bitwise_and(col_ones == -1, col_zeros == -1), np.bitwise_and(col_ones == -1, col_zeros == 0),
             np.bitwise_and(col_ones == 1, col_zeros == -1), np.bitwise_and(col_ones == 1, col_zeros == 0)],
            [partial_solution[:, c], 0, 1, -2]
        )


def update_completions(solution_array: Type[np.ndarray]):
    rows_completed = set(np.where(np.all(solution_array != -1, axis=1))[0].tolist())
    cols_completed = set(np.where(np.all(solution_array != -1, axis=0))[0].tolist())
    return rows_completed, cols_completed


def update_placements(solution_array: Type[np.ndarray],
                      placements_dict: Dict[str, Dict[int, List[Type[np.ndarray]]]],
                      completed_rows: Set[int], completed_columns: Set[int]):
    # Update comprises of 2 changes
    # 1. Remove completed rows and completed columns entirely. This doesn't change update flag.
    # 2. For remaining rows/columns, check all possible arrays vs corresponding line in solution_array to filter out
    #    incompatible options. Changes update flag to True (as it's possible solution_array can be further narrowed)
    updated = False
    indexes_for_deletion = []
    for r in placements_dict['row']:
        if r in completed_rows:
            indexes_for_deletion.append(r)
        else:
            valid_placements = []
            for option in placements_dict['row'][r]:
                valid = np.all(
                    np.select(
                        [np.bitwise_and(option == 0, solution_array[r, :] == 1),
                         np.bitwise_and(option == 1, solution_array[r, :] == 0)],
                        [False, False], default=True
                    )
                )
                if valid:
                    valid_placements.append(option)
            if len(valid_placements) != len(placements_dict['row'][r]):
                # Some options were pruned away
                updated = True
                placements_dict['row'][r] = valid_placements.copy()
    for idx in indexes_for_deletion:
        del placements_dict['row'][idx]
    
    indexes_for_deletion = []
    for c in placements_dict['column']:
        if c in completed_columns:
            indexes_for_deletion.append(c)
        else:
            valid_placements = []
            for option in placements_dict['column'][c]:
                valid = np.all(
                    np.select(
                        [np.bitwise_and(option == 0, solution_array[:, c] == 1),
                         np.bitwise_and(option == 1, solution_array[:, c] == 0)],
                        [False, False], default=True
                    )
                )
                if valid:
                    valid_placements.append(option)
            if len(valid_placements) != len(placements_dict['column'][c]):
                # Some options were pruned away
                updated = True
                placements_dict['column'][c] = valid_placements.copy()
    for idx in indexes_for_deletion:
        del placements_dict['column'][idx]
    
    return updated, placements_dict


def backtrack(solution_array: Type[np.ndarray], row_placements: Dict[int, List[Type[np.ndarray]]],
              row_args: List[Tuple], col_args: List[Tuple], completed_rows: Set[int], completed_cols: Set[int]):
    assert (len(completed_rows) == len(row_args) and len(completed_cols) == len(col_args)) or \
           (len(completed_rows) != len(row_args) and len(completed_cols) != len(col_args))
    
    if len(completed_rows) == len(row_args):
        solution_already_found = False
        for solution in solution_list:
            if solution.tobytes() == partial_solution.tobytes():
                solution_already_found = True
                break
        if not solution_already_found:
            solution_list.append(partial_solution.copy())
        return
    
    for row in row_placements:
        line = solution_array[row, :]
        line_copy = line.copy()
        for option in row_placements[row]:
            line[:] = option.copy()
            completed_rows_next, completed_cols_next = update_completions(solution_array)
            row_placements_next = {r: opt for r, opt in row_placements.items() if r != row}
            if not valid(row_args, col_args, partial_solution, completed_rows_next, completed_cols_next):
                # Undo this choice and continue
                line[:] = line_copy.copy()
                continue
            backtrack(solution_array, row_placements_next, row_args, col_args, completed_rows_next, completed_cols_next)
            line[:] = line_copy.copy()


if __name__ == "__main__":
    # Easy case 1
    # row_args = [(1, ), (2, )]
    # col_args = [(2, ), (1, )]
    
    # Easy case 2 - non-unique
    # row_args = [(1,), (2,)]
    # col_args = [(1, ), (1, ), (1, )]
    
    # Medium case 1
    # row_args = [(2,), (2,), (1,), (1, 1,), (3,)]
    # col_args = [(1,), (2, 1,), (2, 2,), (1, 1,)]
    
    # Medium case 2
    # row_args = [
    #     (5,), (1, 3,), (6,), (2, 5,), (3, 4,),
    #     (3, 7,), (3, 10,), (3, 11,), (5, 7,), (5, 5,),
    #     (5, 6,), (13,), (9,), (1, 1,), (2, 1, 4,)
    # ]
    # col_args = [
    #     (6,), (8,), (9,), (4,), (6,),
    #     (2, 5,), (1, 1, 3, 2, 1,), (8, 2,), (1, 7, 2, 1,), (9, 3,),
    #     (13, 1,), (3, 8, 1,), (8, 1,), (9,), (5,)
    # ]
    
    # Hard case 1
    row_args = [
        (3, 2, 3, ), (3, 1, 1, 1, 3, ), (1, 5, 2, 1, ), (4, 6, 1, ), (3, 6, ),
        (1, 4, 7, ), (4, 2, 2, 6, ), (3, 5, ), (2, 1, 3, ), (7, ),
        (3, 4, 2, ), (1, 2, 3, 4, ), (5, 2, 2, ), (4, 1, 4, ), (5, 5, 1, ),
        (5, 5, ), (2, 1, 6, ), (1, 2, 2, 7, ), (2, 2, 1, 8, ), (7, 1, 7, )
    ]
    col_args = [
        (3, 4, 1, 3, ), (2, 3, 2, ), (3, 2, 1, ), (1, 1, 1, 7, ), (4, 8, ),
        (3, 1, 4, 1, ), (4, 1, 4, 1, ), (1, 1, 3, 2, ), (2, 1, 3, 4, ), (1, 2, 1, 1, ),
        (2, 2, ), (2, 1, 2, ), (4, 3, 4, ), (4, 1, 11, ), (4, 3, 6, ),
        (5, 2, 6, ), (5, 1, 1, 7, ), (8, 6, ), (10, 1, ), (8, 4, )
    ]
    
    # Generate possibilities for each row and column
    row_vector_len = len(col_args)
    col_vector_len = len(row_args)
    placements['row'] = {}
    for i, arg in enumerate(row_args):
        blocks = compute_blocks(row_vector_len, arg)
        placements['row'][i] = enumerate_blocks(blocks, arg, row_vector_len)
    placements['column'] = {}
    for i, arg in enumerate(col_args):
        blocks = compute_blocks(col_vector_len, arg)
        placements['column'][i] = enumerate_blocks(blocks, arg, col_vector_len)
    
    # Infer values
    partial_solution = -1 * np.ones((col_vector_len, row_vector_len), dtype=np.int8)
    completed_rows = set()
    completed_columns = set()
    updated = True
    while updated:
        infer_values(partial_solution, placements)
        completed_rows, completed_columns = update_completions(partial_solution)
        updated, placements = update_placements(partial_solution, placements.copy(), completed_rows, completed_columns)
    
    assert (len(placements['row']) == 0 and len(placements['column']) == 0) or \
           (len(placements['row']) != 0 and len(placements['column']) != 0)
    
    if len(placements['row']) == 0:
        solution_list.append(partial_solution)
    else:
        # Backtrack through the rest of the unsolved rows
        print('Solving via backtracking')
        backtrack(partial_solution, placements['row'], row_args, col_args, completed_rows, completed_columns)
    
    for solution in solution_list:
        print(solution)
