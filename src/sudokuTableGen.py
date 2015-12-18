from puzzle import RandomPuzzleFactory
from solutionFinder import *

# sudoku table generation is actually solve a empty 9 9 table
class SudokuTableGenerator:
	solver = SolutionFinder()
	puzzleFactory = RandomPuzzleFactory(9, 3, 3)
		
	def getTable(self):
		solutionCollector = SolutionsCollector()
		self.solver.solve(self.puzzleFactory.tableBase(), solutionCollector)
		return solutionCollector.result()