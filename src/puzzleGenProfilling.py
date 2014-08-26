from solutionFinder import *
from sudokuTableGen import *
from puzzleGenerator import *

tableGen = SudokuTableGenerator()
factory = RandomPuzzleFactory(9, 3, 3)
solutionFinder = SolutionFinder()
solver = MultiSolutionSolver(solutionFinder)
puzzleGen = PuzzleGenerator(factory, solver)

for i in range(10):
	table = tableGen.getTable()
	puzzle = puzzleGen.constructPuzzleWithOnlySolution(table, 27)
print(puzzle.toString())