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

	def candidatesAt(self, pos):
		return self.candidatesGen.getCandidatesAt(self.grid, pos)		

	def clone(self):
		return Puzzle(self.grid.clone(), self.validator, self.candidatesGen)

	def toString(self):
		return self.grid.toString()

	def getNumbersInPos(self, pos):
		return self.grid.getNumbers(pos)

	def differences(self, theOtherOne):
		diff = self.grid.differences(theOtherOne.grid)
		index = random.randint(0, len(diff) - 1)
		return diff[index]

	def firstEmptyCell(self):
		return self.grid.firstEmptyCell()

	def change(self, pos, value):
		self.grid.change(pos, value)

	def clear(self, pos):
		self.grid.clear(pos)

	def compare(self, theOtherOne):
		return self.grid.compare(theOtherOne.grid)
		pass


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

	def getCandidatesAt(self, grid, pos):
		return self.subList(self.candidatesList, grid.suroundings(pos))

	def subList(self, list1, list2):
		return [number for number in list1 if number not in list2]

class RandomSeqCandidatesDecorator:
	def __init__(self, candidatesGen):
		self.candidatesGen = candidatesGen

	def getCandidatesAt(self, grid, pos):
		candidates = list(self.candidatesGen.getCandidatesAt(grid, pos))
		candidatesCount = len(candidates)
		result = []
		for i in range(0, candidatesCount):
			r = random.randint(0, candidatesCount - i - 1)
			result.append(candidates[r])
			del candidates[r]
		return result		
		pass

class Grid:
	EmptySign = "/"
	nonEmptyNumberIn = lambda self, zone: list(filter(("/").__ne__, zone))

	def __init__(self, matrix, bw, bh):
		self.matrix = matrix
		self.bw = bw
		self.bh = bh

		self.mHeight = len(matrix) #matrix Height
		self.mWidth = len(matrix[0]) #matrix Width

		self.emptyList = [(i, j) for i in range(self.mHeight) for j in range(self.mWidth) if matrix[i][j] is _]
		self.columns = self.transMatrix(matrix)
		
		self.nbPerRow = len(matrix[0]) // bw
		to_i = lambda bi, bj: self.blockIndexToMatrixIndex(bi, bj)[0]
		to_j = lambda bi, bj: self.blockIndexToMatrixIndex(bi, bj)[1]
		bsize = bw * bh
		bnum = self.mHeight * self.mWidth // bsize
		self.blocks = [[matrix[to_i(i, j)][to_j(i,j)] for j in range(bsize)] for i in range(bnum)]
		self.blockIndexMap = [[(i // self.bh * self.nbPerRow + j // self.bw, i % self.bh * self.bw + j % self.bw) for j in range(self.mWidth)] for i in range(self.mHeight)]

	def allRows(self):
		return [self.row(i) for i in range(0, len(self.matrix))]

	def allColumns(self):
		return [self.column(j) for j in range(0, len(self.columns))]

	def transMatrix(self, matrix):
		return [list(column) for column in list(zip(*matrix))]

	def allBlocks(self):
		blocks = [[self.block(i, j) for j in range(0, len(self.matrix[i]), self.bw)] for i in range(0, len(self.matrix), self.bh)]
		return reduce(operator.add, blocks) #flatten blocks

	def block(self, i, j):
		(bi, bj) = self.matrixIndexToBlockIndex(i, j)
		return self.nonEmptyNumberIn(self.blocks[bi])

	def full(self):
		return len(self.emptyList) is 0

	def row(self, i):
		return self.nonEmptyNumberIn(self.matrix[i])

	def column(self, j):
		return self.nonEmptyNumberIn(self.columns[j])

	def suroundings(self, pos):
		i, j = pos[0], pos[1]
		(bi, bj) = self.matrixIndexToBlockIndex(i, j)
		return set(self.matrix[i] + self.columns[j] + self.blocks[bi]) - set(self.EmptySign)

	def clone(self):
		newMatrix = [list(row) for row in self.matrix]
		return Grid(newMatrix, self.bw, self.bh)

	def toString(self):
		return json.dumps(self.matrix)

	def getNumbers(self, pos):
		return [self.matrix[p[0]][p[1]] for p in pos]

	def differences(self, theOtherGrid):
		m1, m2 = self.matrix, theOtherGrid.matrix
		return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix[0])) if m1[i][j] is not m2[i][j]]

	def firstEmptyCell(self):
		result = self.emptyList[0]
		del self.emptyList[0]
		return result

	def change(self, pos, value):
		self.matrix[pos[0]][pos[1]] = value
		self.columns[pos[1]][pos[0]] = value
		(bi, bj) = self.matrixIndexToBlockIndex(pos[0], pos[1])
		self.blocks[bi][bj] = value

	def clear(self, pos):
		self.matrix[pos[0]][pos[1]] = _
		self.columns[pos[1]][pos[0]] = _
		(bi, bj) = self.matrixIndexToBlockIndex(pos[0], pos[1])
		self.blocks[bi][bj] = _
		self.emptyList = [pos] + self.emptyList

	def blockIndexToMatrixIndex(self, bi, bj):
		i = int(bi // self.nbPerRow * self.bh + bj // self.bw)
		j = int(bi % self.nbPerRow * self.bw + bj % self.bw)
		return (i, j)

	def matrixIndexToBlockIndex(self, i, j):
		return self.blockIndexMap[i][j]

	def compare(self, theOtherGrid):
		for i in range(self.mHeight):
			for j in range(self.mWidth):
				if self.matrix[i][j] != theOtherGrid.matrix[i][j]:
					return self.compareElement(self.matrix[i][j], theOtherGrid.matrix[i][j])
		return 0

	def compareElement(self, x, y):
		if x is y:
			return 0

		if (x is self.EmptySign) or (x > y) : 
			return 1
		else:
			return -1

_ = Grid.EmptySign

class PuzzleFactory:
	def __init__(self, tableSize, blockWidth, blockHeight):
		self.tableSize = tableSize
		self.bw = blockHeight
		self.bh = blockHeight
		self.validator = Validator()
		self.candidatesGen = CandidatesGen(range(1, tableSize+1))

	def creatPuzzleByMatrix(self, matrix):
		grid = Grid(matrix, self.bw, self.bh)
		return Puzzle(grid, self.validator, self.candidatesGen)

	def emptyPuzzle(self):
		grid = Grid(self.emptyMatrix(), self.bw, self.bh)
		return Puzzle(grid, self.validator, self.candidatesGen)

	def getRandomPos(self, count):
		d = self.tableSize

		indexs = list(range(d*d))

		tops = [d*d - i - 1 for i in range(count)]
		randNum = [random.randint(0, top) for top in tops]

		result = []
		for num in randNum:
			result = result + [indexs[num]]
			del indexs[num]

		return [(num // d, num % d) for num in result]

	def createPuzzleFromTable(self, table, pos):
		posNumMap = dict(zip(pos, table.getNumbersInPos(pos)))
		matrix = self.emptyMatrix()
		for pos in posNumMap:
			matrix[pos[0]][pos[1]] = posNumMap[pos]
		return self.creatPuzzleByMatrix(matrix)

	def emptyMatrix(self):
		return  [[_]*self.tableSize for j in range(self.tableSize)]

	def tableBase(self):
		grid = Grid(self.tableBaseMatrix(), self.bw, self.bh)
		return Puzzle(grid, self.validator, self.candidatesGen)

	def tableBaseMatrix(self):
		return [[1, 2, 3, 4, 5, 6, 7, 8, 9]] + [[_]*self.tableSize for j in range(self.tableSize - 1)]


class RandomPuzzleFactory(PuzzleFactory):
	def __init__(self, tableSize, blockWidth, blockHeight):
		super(RandomPuzzleFactory, self).__init__(tableSize, blockWidth, blockHeight)
		self.candidatesGen = RandomSeqCandidatesDecorator(self.candidatesGen)
		pass