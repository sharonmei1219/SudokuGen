class PuzzleGenerator:
	def __init__(self, puzzleFactory, puzzleSolver):
		self.puzzleFactory = puzzleFactory
		self.puzzleSolver = puzzleSolver

	def constructPuzzleWithOnlySolution(self, table, initNumCnt):
		pos = self.randomPos(initNumCnt)
		puzzle = self.createPuzzle(table, pos)
		result = self.solve(puzzle)

		while result.solutionCount() > 1:
			pos = pos + [result.solutionDifference()]
			puzzle = self.createPuzzle(table, pos)
			result = self.solve(puzzle)

		return puzzle

	def solve(self, puzzle):
		return self.puzzleSolver.solve(puzzle)

	def createPuzzle(self, table, pos):
		return self.puzzleFactory.createPuzzleFromTable(table, pos)

	def randomPos(self, count):
		return self.puzzleFactory.getRandomPos(count)

class MultiSolutionSolver:
	def __init__(self, solutionFinder):
		self.solutionFinder = solutionFinder

	def solve(self, puzzle):
		solutionCollection = self.newSolutionCollections()
		self.solutionFinder.solve(puzzle, solutionCollection)
		return solutionCollection.result()

class MultisolutionCollector:
	def __init__(self):
		self.solutionCount = 0
		self.solutions = []

	def record(self, puzzle):
		self.solutions = self.solutions + [puzzle]
		self.solutionCount += 1

	def result(self):
		if self.solutionCount is 2:
			return MultiSolutionResult(self.solutionCount, self.solutions[0].compare(self.solutions[1]))

		return MultiSolutionResult(self.solutionCount)

	def done(self):
		return self.solutionCount is 2

class MultiSolutionResult:
	def __init__(self, count, differencePos = None):
		self.count = count
		self.difference = differencePos

	def solutionCount(self):
		return self.count;

	def solutionDifference(self):
		return self.difference
				