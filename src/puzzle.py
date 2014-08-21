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
		return [self.nonEmptyNumberIn(row) for row in self.transMatrix(self.matrix)]

	def transMatrix(self, matrix):
		return [list(column) for column in list(zip(*matrix))]

	def allBlocks(self):
		blocks = [[self.block(i, j) for j in range(0, len(self.matrix[i]), self.bw)] for i in range(0, len(self.matrix), self.bh)]
		return reduce(operator.add, blocks) #flatten blocks

	def block(self, i, j):
		left, right, top, bottom = self.blockArea(i, j)
		blc = [row[left: right] for row in self.matrix[top:bottom]]
		blc = reduce(operator.add, blc)
		return self.nonEmptyNumberIn(blc)

	def blockArea(self, i, j):
		left = j - j % self.bw
		right = left + self.bw
		top = i - i % self.bh
		bottom = top + self.bh
		return left, right, top, bottom

	def full(self):
		rowFull = [all(mem is not self.EmptySign for mem in row) for row in self.matrix]
		return all(rowIsFull for rowIsFull in rowFull)