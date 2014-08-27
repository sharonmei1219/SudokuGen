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

	def compare(self, theOtherOne):
		differences = self.grid.compare(theOtherOne.grid)
		index = random.randint(0, len(differences) - 1)
		return differences[index]

	def firstEmptyCell(self):
		return self.grid.firstEmptyCell()

	def change(self, pos, value):
		self.grid.change(pos, value)

	def clear(self, pos):
		self.grid.clear(pos)


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
	EmptySign = '/'
	nonEmptyNumberIn = lambda self, zone: [number for number in zone if number is not self.EmptySign]

	def __init__(self, matrix, bw, bh):
		self.matrix = matrix
		self.bw = bw
		self.bh = bh

		mHeight = len(matrix)
		mWidth = len(matrix[0])

		self.emptyList = [(i, j) for i in range(mHeight) for j in range(mWidth) if matrix[i][j] is _]
		self.columns = self.transMatrix(matrix)
		
		self.nbPerRow = len(matrix[0]) // bw
		to_i = lambda bi, bj: self.blockIndexToMatrixIndex(bi, bj)[0]
		to_j = lambda bi, bj: self.blockIndexToMatrixIndex(bi, bj)[1]
		bsize = bw * bh
		bnum = mHeight * mWidth // bsize
		self.blocks = [[matrix[to_i(i, j)][to_j(i,j)] for j in range(bsize)] for i in range(bnum)]
		self.blockIndexMap = [[(i // self.bh * self.nbPerRow + j // self.bw, i % self.bh * self.bw + j % self.bw) for j in range(mWidth)] for i in range(mHeight)]

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
		nbPerRow = len(self.matrix[0]) //self.bw
		bi = i // self.bh * nbPerRow + j // self.bw
		blc = self.blocks[bi]
		return self.nonEmptyNumberIn(blc)

	def blockArea(self, i, j):
		left = j - j % self.bw
		right = left + self.bw
		top = i - i % self.bh
		bottom = top + self.bh
		return left, right, top, bottom

	def full(self):
		return len(self.emptyList) is 0

	def row(self, i):
		return self.nonEmptyNumberIn(self.matrix[i])

	def column(self, j):
		return self.nonEmptyNumberIn(self.columns[j])

	def suroundings(self, pos):
		i, j = pos[0], pos[1]
		return set(reduce(operator.add, [self.row(i), self.column(j), self.block(i, j)]))

	def clone(self):
		newMatrix = [list(row) for row in self.matrix]
		return Grid(newMatrix, self.bw, self.bh)

	def toString(self):
		return json.dumps(self.matrix)

	def getNumbers(self, pos):
		return [self.matrix[p[0]][p[1]] for p in pos]

	def compare(self, theOtherGrid):
		m1, m2 = self.matrix, theOtherGrid.matrix
		return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix[0])) if m1[i][j] is not m2[i][j]]

	def firstEmptyCell(self):
		result = self.emptyList[0]
		del self.emptyList[0]
		return result

	def change(self, pos, value):
		# i, j = pos[0], pos[1]
		self.matrix[pos[0]][pos[1]] = value
		self.columns[pos[1]][pos[0]] = value
		# nbPerRow = len(self.matrix[0]) //self.bw
		# bi = i // self.bh * nbPerRow + j // self.bw
		# bj = i % self.bh * self.bw + j % self.bw
		(bi, bj) = self.matrixIndexToBlockIndex(pos[0], pos[1])
		self.blocks[bi][bj] = value

	def clear(self, pos):
		# i, j = pos[0], pos[1]
		self.matrix[pos[0]][pos[1]] = _
		self.columns[pos[1]][pos[0]] = _
		# nbPerRow = len(self.matrix[0]) //self.bw
		# bi = i // self.bh * nbPerRow + j // self.bw
		# bj = i % self.bh * self.bw + j % self.bw
		(bi, bj) = self.matrixIndexToBlockIndex(pos[0], pos[1])
		self.blocks[bi][bj] = _
		self.emptyList = [pos] + self.emptyList

	def blockIndexToMatrixIndex(self, bi, bj):
		i = int(bi // self.nbPerRow * self.bh + bj // self.bw)
		j = int(bi % self.nbPerRow * self.bw + bj % self.bw)
		return (i, j)

	def matrixIndexToBlockIndex(self, i, j):
		return self.blockIndexMap[i][j]

_ = Grid.EmptySign

class RandomPuzzleFactory:
	def __init__(self, tableSize, blockWidth, blockHeight):
		self.tableSize = tableSize
		self.bw = blockHeight
		self.bh = blockHeight
		self.validator = Validator()
		self.candidatesGen = RandomSeqCandidatesDecorator(CandidatesGen(range(1, tableSize+1)))

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
