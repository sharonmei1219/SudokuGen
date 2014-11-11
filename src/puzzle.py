from collections import Counter
from functools import reduce
import operator
import random
import json
import copy

class Puzzle():
	EmptySign = "/"
	def __init__(self, matrix, grid, validator, candidates):
		self.grid = grid
		self.validator = validator
		self.candidatesGen = candidates

		self.puzzleMatrix = PuzzleMatrix(matrix)
		self.matrix = matrix
		self.mHeight = len(matrix)
		self.mWidth = len(matrix[0])
		self.emptyList = [(i, j) for i in range(self.mHeight) for j in range(self.mWidth) if matrix[i][j] is _]

	def solved(self):
		return self.full() and self.validator.validate(self.grid, self.puzzleMatrix)

	def candidatesAt(self, pos):
		return self.candidatesGen.getCandidatesAt(self.grid, pos, self.matrix)		

	def clone(self):
		return Puzzle(copy.deepcopy(self.matrix), self.grid, self.validator, self.candidatesGen)

	def toString(self):
		return json.dumps(self.matrix)

	def getNumbersInPos(self, pos):
		return self.puzzleMatrix.getNumbersInPos(pos)

	def differences(self, theOtherOne):
		m1, m2 = self.matrix, theOtherOne.matrix
		diff =  [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix[0])) if m1[i][j] is not m2[i][j]]
		index = random.randint(0, len(diff) - 1)
		return diff[index]

	def full(self):
		return self.puzzleMatrix.full()

	def firstEmptyCell(self):
		return self.puzzleMatrix.firstEmptyCell()

	def suroundings(self, pos):
		i, j = pos[0], pos[1]
		return set(self.matrix[i] + self.column(j) + self.block(i, j)) - set(self.EmptySign)

	def clear(self, pos):
		self.puzzleMatrix.clear(pos)

	def change(self, pos, value):
		self.puzzleMatrix.change(pos, value)

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

class PuzzleMatrix:
	def __init__(self, matrix):
		self.matrix = matrix
		self.mHeight = len(matrix)
		self.mWidth = len(matrix[0])
		self.emptyList = [(i, j) for i in range(self.mHeight) for j in range(self.mWidth) if matrix[i][j] is _]
		pass

	def change(self, pos, value):
		(i, j) = pos
		self.matrix[i][j] = value
		pass

	def clear(self, pos):
		(i, j) = pos
		self.matrix[i][j] = _
		self.emptyList = [pos] + self.emptyList	
		pass

	def firstEmptyCell(self):
		result = self.emptyList[0]
		del self.emptyList[0]
		return result
	
	def full(self):
		return len(self.emptyList) is 0

	def getNumbersInPos(self, pos):
		return [self.matrix[i][j] for (i, j) in pos]

	pass
class Validator:
	def validate(self, grid, puzzleMatrix):
		directions = grid.allDirection()
		return all([self.validInDirection(direction, puzzleMatrix) for direction in directions])

	def validInDirection(self, direction, puzzleMatrix):
		zones = direction.zones()
		return all(not self.detectDuplication(puzzleMatrix.getNumbersInPos(zone)) for zone in zones)

	def detectDuplication(self, numberList):
		counter = Counter(numberList)
		return not all(counter[number] == 1 for number in counter)

class CandidatesGen:
	def __init__(self, candidatesList):
		self.candidatesList = candidatesList

	def getCandidatesAt(self, grid, pos, matrix):
		return self.subList(self.candidatesList, grid.suroundings(pos, matrix))

	def subList(self, list1, list2):
		return [number for number in list1 if number not in list2]

class RandomSeqCandidatesDecorator:
	def __init__(self, candidatesGen):
		self.candidatesGen = candidatesGen

	def getCandidatesAt(self, grid, pos, matrix):
		candidates = list(self.candidatesGen.getCandidatesAt(grid, pos, matrix))
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

	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		self.gridRow = GridRow(matrixHeight, matrixWidth)
		self.gridColumn = GridColumn(matrixHeight, matrixWidth)
		self.gridBlock = GridBlock(matrixHeight, matrixWidth, blockHeight, blockWidth)

		self.views = [self.gridRow, self.gridColumn, self.gridBlock]

	def flatten(self, twoDArray):
		return reduce(operator.add, twoDArray, [])

	def suroundings(self, pos, matrix):
		poses = self.flatten([view.zoneWithPosIn(pos) for view in self.views])
		return set([matrix[i][j] for (i, j) in poses]) - set(self.EmptySign)

	def allPos(self):
		return self.flatten(self.gridRow.zones())

	def allDirection(self):
		return [self.gridRow, self.gridColumn, self.gridBlock]

class GridDirection:
	def posesInSameZone(self, poses):
		return any([all([pos in zone for pos in poses]) for zone in self.zones()])

	def split(self, poses):
		areas = [{pos for pos in poses if pos in zone} for zone in self.zones()]
		return [area for area in areas if len(area) > 0]

class GridRow(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self.matrixHeight = matrixHeight
		self.matrixWidth = matrixWidth
		pass

	def zones(self):
		return [self.zoneWithPosIn((i, 0)) for i in range(self.matrixHeight)]

	def zoneWithPosIn(self, pos):
		return [(pos[0], x) for x in range(self.matrixWidth)]

class GridColumn(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self.matrixHeight = matrixHeight
		self.matrixWidth = matrixWidth

	def zones(self):
		return [self.zoneWithPosIn((0, j)) for j in range(self.matrixWidth)]

	def zoneWithPosIn(self, pos):
		return [(x, pos[1]) for x in range(self.matrixHeight)]

class GridBlock(GridDirection):
	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		self.blockHeight = blockHeight
		self.blockWidth = blockWidth

		self.nbPerRow = matrixWidth // blockWidth
		bsize = blockWidth * blockHeight
		bnum = matrixHeight * matrixWidth // bsize
		self.blockIndex = [[self.blockIndexToMatrixIndex(i, j) for j in range(bsize)] for i in range(bnum)]
		self.blockIndexMap = [[(i // self.blockHeight * self.nbPerRow + j // self.blockWidth, i % self.blockHeight * self.blockWidth + j % self.blockWidth) for j in range(matrixWidth)] for i in range(matrixHeight)]

	def blockIndexToMatrixIndex(self, bi, bj):
		i = int(bi // self.nbPerRow * self.blockHeight + bj // self.blockWidth)
		j = int(bi % self.nbPerRow * self.blockWidth + bj % self.blockWidth)
		return (i, j)

	def zones(self):
		return self.blockIndex

	def zoneWithPosIn(self, pos):
		(bi, bj) = self.blockIndexMap[pos[0]][pos[1]]
		return self.blockIndex[bi]

_ = Grid.EmptySign

class PuzzleFactory:
	def __init__(self, tableSize, blockWidth, blockHeight):
		self.tableSize = tableSize
		self.bw = blockHeight
		self.bh = blockHeight
		self.validator = Validator()
		self.candidatesGen = CandidatesGen(range(1, tableSize+1))

	def creatPuzzleByMatrix(self, matrix):
		grid = Grid(self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(matrix, grid, self.validator, self.candidatesGen)

	def emptyPuzzle(self):
		grid = Grid(self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(self.emptyMatrix(), grid, self.validator, self.candidatesGen)

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
		grid = Grid(self.tableBaseMatrix(), self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(self.tableBaseMatrix(), grid, self.validator, self.candidatesGen)

	def tableBaseMatrix(self):
		return [[1, 2, 3, 4, 5, 6, 7, 8, 9]] + [[_]*self.tableSize for j in range(self.tableSize - 1)]


class RandomPuzzleFactory(PuzzleFactory):
	def __init__(self, tableSize, blockWidth, blockHeight):
		super(RandomPuzzleFactory, self).__init__(tableSize, blockWidth, blockHeight)
		self.candidatesGen = RandomSeqCandidatesDecorator(self.candidatesGen)
		pass