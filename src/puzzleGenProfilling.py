from solutionFinder import *
from sudokuTableGen import *
from puzzleGenerator import *
from quickSolutionFinder import * 
from puzzle import *


tableGen = SudokuTableGenerator()

factory = PuzzleFactory(9, 3, 3)
solutionFinder = QuickSolutionFinder()
solver = QuickSolver(solutionFinder)
puzzleGen = QuickPuzzleGenerator(factory, solver)
digger = HoleDigger(puzzleGen)
for i in range(5):
	table = tableGen.getTable()
	puzzle = digger.constructPuzzleWithOnlySolution(table, 21)
	# slow_solutionFinder = SolutionFinder()
	# slow_solver = MultiSolutionSolver(slow_solutionFinder)
	# self.assertEquals(1, slow_solver.solve(puzzle).solutionCount())

# self.assertEquals("sharon", puzzle.toString())