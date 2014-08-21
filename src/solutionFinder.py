class SolutionFinder:
	def solve(self, puzzle, solutions):
		if puzzle.solved():
			solutions.record(puzzle.clone())
			return

		for candidate in puzzle.candidates():
			newPuzzle = puzzle.fill(candidate)
			self.solve(newPuzzle, solutions)
			if solutions.done():
				return
		
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