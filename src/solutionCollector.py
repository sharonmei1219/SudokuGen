class MultisolutionCollector:
	def __init__(self):
		self.solutionCount = 0
		self.solutions = []

	def record(self, puzzle):
		self.solutions = self.solutions + [puzzle]
		self.solutionCount += 1

	def result(self):
		if self.solutionCount is 2:
			return MultiSolutionResult(self.solutionCount, self.solutions[0].differences(self.solutions[1]))

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


class SolutionCollectorWithoutMemory:
	def __init__(self, table):
		self.table = table
		self.findDifferentSolution = False
		self.solution = None

	def done(self):
		return self.findDifferentSolution 

	def record(self, puzzle):
		self.solution = puzzle
		if puzzle.compare(self.table) is not 0:
			self.findDifferentSolution = True

	def result(self):
		if self.findDifferentSolution:
			return MultiSolutionResult(2, self.solution.differences(self.table))
		else:
			return MultiSolutionResult(1)

	def next(self):
		if self.solution is not None:
			return self.createCollectorWithMemory(self.table, self.solution)
		else:
			return self

	def createCollectorWithMemory(self, table, lastSolution):
		return SolutionCollectorWithMemory(table, lastSolution)

	def impossibleTohaveSolution(self, puzzle):
		return False

class SolutionCollectorWithMemory(SolutionCollectorWithoutMemory):
	def __init__(self, table, startingPoint):
		super(SolutionCollectorWithMemory, self).__init__(table)
		self.startingPoint = startingPoint
		self.reachedStartingPoint = False

	def record(self, puzzle):
		self.solution = puzzle

		if puzzle.compare(self.table) is not 0:
			self.findDifferentSolution = True
			self.reachedStartingPoint = True

	def impossibleTohaveSolution(self, puzzle):
		if self.reachedStartingPoint is True:
			return False
		return puzzle.compare(self.startingPoint) <= 0
