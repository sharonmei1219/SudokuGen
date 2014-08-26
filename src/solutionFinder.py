class SolutionFinder:
	def solve(self, puzzle, solutions):
		if puzzle.solved():
			solutions.record(puzzle.clone())
			return

		(i, j) = puzzle.firstEmptyCell()
		
		for candidate in puzzle.candidatesAt((i, j)):
			puzzle.change((i, j), candidate)
			self.solve(puzzle, solutions)
			if solutions.done():
				break

		puzzle.clear((i, j))
		
class SolutionsCollector:
	def __init__(self):
		self.workDone = False

	def record(self, puzzle):
		self.puzzle = puzzle
		self.workDone = True

	def done(self):
		return self.workDone

	def result(self):
		return self.puzzle