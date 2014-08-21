from puzzle import empty99Puzzle
from solutionFinder import *

# sudoku table generation is actually solve a empty 9 9 table
class SudokuTableGenerator:
	solver = SolutionFinder()
		
	def getTable(self):
		solutionCollector = SolutionsCollector()
		self.solver.solve(empty99Puzzle(), solutionCollector)
		return solutionCollector.result()