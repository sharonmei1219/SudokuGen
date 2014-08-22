from puzzle import *
from itertools import repeat

class PuzzleGenerator():

	def generatePuzzle(self, table, initNumCnt):
		fromList = table.toElementList()

		toList = fromList.extractRandomly(initNumCnt)
		puzzle = toList.toPuzzle()
		result = self.solve(puzzle)

		while result.solutionCnt() > 1:
			i, j = result.difference()
			toList = toList.add(fromList.retrieve(i, j))
			puzzle = toList.toPuzzle()
			result = self.solve(puzzle)

		return puzzle


class NumberOccupationList():
	def __init__(self, occupationNumberMap, gridType, validator, candidatesGen, width, height):
		self.gridType = gridType
		self.validator = validator
		self.candidatesGen = candidatesGen
		self.width = width
		self.height = height
		self.map = occupationNumberMap

	def toPuzzle(self):
		_ = self.gridType.EmptySign
		matrix = [[_ for j in range(self.width)] for i in range(self.height)]
		for (i, j) in self.map:
			matrix[i][j] = self.map[(i, j)]

		return Puzzle(self.gridType(matrix), self.validator, self.candidatesGen)


	pass

		