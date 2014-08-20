from collections import Counter
import operator
from functools import reduce

class Puzzle():
	def __init__(self, grid, validator, candidates):
		self.grid = grid
		self.validator = validator
		self.candidatesGen = candidates

	def solved(self):
		return self.grid.full() and self.validator.validate(self.grid)
	
	def candidates(self):
		return self.candidatesGen.getCandidates(self.grid)

	def fill(self, number):
		return Puzzle(self.grid.fill(number), self.validator, self.candidates)


class Validator:
	def validate(self, grid):
		zones = reduce(operator.add, [grid.allRows(), grid.allColumns(), grid.allBlocks()])
		return all(not self.detectDuplication(zone) for zone in zones)

	def detectDuplication(self, numberList):
		counter = Counter(numberList)
		return not all(counter[number] == 1 for number in counter)


class CandidatesGen:
	def __init__(self, candidatesList):
		self.candidatesList = candidatesList

	def getCandidates(self, grid):
		return self.subList(self.candidatesList, grid.emptyCellSurounding())

	def subList(self, list1, list2):
		return [number for number in list1 if number not in list2]


class Grid:
	EmptySign = '/'
	nonEmptyNumberIn = lambda self, zone: [number for number in zone if number is not self.EmptySign]

	def __init__(self, matrix):
		self.matrix = matrix

	def allRows(self):
		return [self.nonEmptyNumberIn(row) for row in self.matrix]

	def allColumns(self):
		return [self.nonEmptyNumberIn(row) for row in self.transMatrix()]

	def transMatrix(self):
		return [list(column) for column in list(zip(*self.matrix))]