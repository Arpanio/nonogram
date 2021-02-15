# Nonogram Solver

> Nonograms, also known as **Paint by Numbers**, **Picross**, **Griddlers**, **Pic-a-Pix**, and various other names, are picture logic puzzles in which cells in a grid must be colored or left blank according to numbers at the side of the grid to reveal a hidden picture.

Source: [Wikipedia](https://en.wikipedia.org/wiki/Nonogram)

While simple Nonograms may be solved using brute force, the number of total combinations quickly reaches into the 10 Billion range even for a moderate sized 15 x 15 grid.

### Example of a Nonogram:

![Nonogram Example](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Nonogram_wiki.svg/500px-Nonogram_wiki.svg.png "Nonogram example for the letter W")

This repository contains solution using [backtracking](https://en.wikipedia.org/wiki/Backtracking) and [constraint programming](https://en.wikipedia.org/wiki/Constraint_programming) for Nonogram puzzles.

1. `constraint_programming_solver.py`: Uses the constraint Python module
2. `backtracking_naive.py`: Uses a backtracking implementation that does not scale beyond very small (5 x 5) grids
3. `enumerative_backtracking_solver.py`: Uses enumerative reasoning for rows and columns to nail down known cell values (a cell value is known if all possible combinations for that row/column agree that the cell should have either a 0 or a 1), before switching to backtracking
