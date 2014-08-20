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
	pass