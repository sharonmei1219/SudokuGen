from puzzle import Puzzle
from solutionFinder import *

# sudoku table generation is actually solve a empty 9 9 table
class SudokuTableGenerator:
	puzzle = Puzzle.empty99Puzzle()
	solver = SolutionFinder()
		
	def getTable(self):
		solutionCollector = SolutionsCollector()
		self.solver.solve(self.puzzle, solutionCollector)
		return solutionCollector.result()