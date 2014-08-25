from collections import Counter
from functools import reduce
import operator
import random
import json

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
		return Puzzle(self.grid.fill(number), self.validator, self.candidatesGen)

	def clone(self):
		return Puzzle(self.grid.clone(), self.validator, self.candidatesGen)

	def toString(self):
		return self.grid.toString()

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

class RandomSeqCandidatesDecorator:
	def __init__(self, candidatesGen):
		self.candidatesGen = candidatesGen

	def getCandidates(self, grid):
		candidates = list(self.candidatesGen.getCandidates(grid))
		candidatesCount = len(self.candidatesGen.getCandidates(grid))
		result = []
		for i in range(0, candidatesCount):
			r = random.randint(0, candidatesCount - i - 1)
			result.append(candidates[r])
			del candidates[r]
		return result

class Grid:
	EmptySign = '/'
	nonEmptyNumberIn = lambda self, zone: [number for number in zone if number is not self.EmptySign]

	def __init__(self, matrix, bw, bh):
		self.matrix = matrix
		self.bw = bw
		self.bh = bh

	def allRows(self):
		return [self.row(i) for i in range(0, len(self.matrix))]

	def allColumns(self):
		return [self.column(j) for j in range(0, len(self.transMatrix(self.matrix)))]

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

	# fill means fill number in the first empty cell found
	# after fill, there comes new grid
	def fill(self, number):
		newMatrix = [list(row) for row in self.matrix]

		if self.full():
			return type(self)(newMatrix, self.bw, self.bh)

		i, j = self.findEmptyCell()
		newMatrix[i][j] = number
		return Grid(newMatrix, self.bw, self.bh)

	# findEmptyCell only find the first empty cell
	def findEmptyCell(self):
		for i in range(0, len(self.matrix)):
			for j in range(0, len(self.matrix[i])):
				if self.matrix[i][j] is self.EmptySign:
					return i, j

	def row(self, i):
		return self.nonEmptyNumberIn(self.matrix[i])

	def column(self, j):
		return self.nonEmptyNumberIn(self.transMatrix(self.matrix)[j])

	def emptyCellSurounding(self):
		i, j = self.findEmptyCell()
		return set(reduce(operator.add, [self.row(i), self.column(j), self.block(i, j)]))

	def clone(self):
		newMatrix = [list(row) for row in self.matrix]
		return Grid(newMatrix, self.bw, self.bh)

	def toString(self):
		return json.dumps(self.matrix)

ThreeThreeGrid = type('ThreeThreeGrid', (Grid, ), {'bw':3, 'bh':3})
_ = Grid.EmptySign

# this empty puzzle is used to generate sudoku table
# its candidates are in random sequence so as to generate random table
def empty99Puzzle():
	grid = Grid([[_ for i in range(9)] for j in range(9)], 3, 3)
	candidatesGen = RandomSeqCandidatesDecorator(CandidatesGen(range(1, 10)))
	validator = Validator()
	return Puzzle(grid, validator, candidatesGen)