from solutionCollector import *

class PuzzleGenerator:
	def __init__(self, puzzleFactory, puzzleSolver):
		self.puzzleFactory = puzzleFactory
		self.puzzleSolver = puzzleSolver

	def constructPuzzleWithOnlySolution(self, table, initNumCnt):
		pos = self.randomPos(initNumCnt)
		result, newAddedPos= self.constructPuzzleWithInitialPos(table, pos)
		return result

	def constructPuzzleWithInitialPos(self, table, pos):
		puzzle = self.createPuzzle(table, pos)
		result = self.solve(puzzle)
		newlyAddedPos = []

		while result.solutionCount() > 1:
			newlyAddedPos = newlyAddedPos + [result.solutionDifference()]
			puzzle = self.createPuzzle(table, pos + newlyAddedPos)
			result = self.solve(puzzle)

		return puzzle, newlyAddedPos


	def solve(self, puzzle):
		return self.puzzleSolver.solve(puzzle)

	def createPuzzle(self, table, pos):
		return self.puzzleFactory.createPuzzleFromTable(table, pos)

	def randomPos(self, count):
		return self.puzzleFactory.getRandomPos(count)


class QuickPuzzleGenerator:
	def __init__(self, puzzleFactory, puzzleSolver):
		self.gen = PuzzleGenerator(puzzleFactory, puzzleSolver)

	def constructPuzzleWithOnlySolution(self, table, initNumCnt):
		pos = self.gen.randomPos(initNumCnt)
		self.gen.puzzleSolver.refresh(table)
		result, newAddedPos= self.gen.constructPuzzleWithInitialPos(table, pos)
		return result

class QuickSolver:
	def __init__(self, solutionFinder):
		self.solutionFinder = solutionFinder
		self.solutioncollecor = None

	def refresh(self, table):
		self.solutioncollecor = SolutionCollectorWithoutMemory(table)
		
	def solve(self, puzzle):
		self.solutionFinder.solve(puzzle, self.solutioncollecor)
		result = self.solutioncollecor.result()
		self.solutioncollecor = self.solutioncollecor.next()
		return result

class MultiSolutionSolver:
	def __init__(self, solutionFinder):
		self.solutionFinder = solutionFinder

	def solve(self, puzzle):
		solutionCollection = self.newSolutionCollections()
		self.solutionFinder.solve(puzzle, solutionCollection)
		return solutionCollection.result()

	def newSolutionCollections(self):
		return MultisolutionCollector()