
class QuickSolutionFinder:
	def solve(self, puzzle, solutions):
		if solutions.impossibleTohaveSolution(puzzle):
			return

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