class PuzzleGenerator:
	def __init__(self, puzzleFactory):
		self.puzzleFactory = puzzleFactory

	def constructPuzzleWithOnlySolution(self, table, initNumCnt):
		pos = self.randomPos(initNumCnt)
		puzzle = self.createPuzzle(table, pos)
		result = self.solve(puzzle)

		while result.solutionCount() > 1:
			pos = pos + [result.solutionDifference()]
			puzzle = self.createPuzzle(table, pos)
			result = self.solve(puzzle)

		return puzzle

	def createPuzzle(self, table, pos):
		return self.puzzleFactory.createPuzzleFromTable(table, pos)

	def randomPos(self, count):
		return self.puzzleFactory.getRandomPos(count)

